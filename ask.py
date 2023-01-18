from enum import Enum
from math import floor
import os
import subprocess
from typing import Dict, List, Tuple
import numpy as np
import pickle
import typer
import ast
from transformers import GPT2TokenizerFast
from llm import OpenAI

gpt2_tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
gpt = OpenAI()

app = typer.Typer()

embeddings = []
def load_embeddings(chunks: list[dict[str, str]]):
    vecs = gpt.embed([chunk["text"] for chunk in chunks])
    for i in range(len(chunks)):
        embeddings.append({
            "embedding": vecs[i],
            **chunks[i]
        })

def binary_insert(l: list, item, lge) -> int:
    """Takes a list, an item to insert, and a less/greater/equal comparion function, and returns the index at which it shoud be inserted."""
    if len(l) == 0:
        return 0

    idx = floor(len(l)/2)

    comparison = lge(item, l[idx])
    if comparison == 0:
        return idx
    elif comparison == -1:
        if idx == 0:
            return 0
        else:
            return binary_insert(l[:idx], item, lge)
    elif comparison == 1:
        if idx == len(l) - 1:
            return len(l)
        else:
            return idx + 1 + binary_insert(l[idx + 1:], item, lge)
    else:
        raise NotImplementedError

def compare_similarity(a: float, b: float) -> int:
    if a < b:
        return -1
    elif a > b:
        return 1
    else:
        return 0

def brute_top_k(target: np.ndarray, k: int) -> List:
    """Returns the top k most similar embeddings to the target embedding, by brute force."""
    top_k = [] # Of type {embedding: {text: str, embedding: list[float], *other}, similarity: float}. Ordered from largest to smallest inner_prod (similarity)
    for e in embeddings:
        inner_prod = np.inner(e["embedding"], target)
        if len(top_k) < k or inner_prod > top_k[-1]["similarity"]:
            if len(top_k) == k:
                top_k.pop()

            item = { "embedding": e, "similarity": inner_prod }
            idx = binary_insert(top_k, item,
                lambda a, b: compare_similarity(a["similarity"], b["similarity"])
            )
            top_k.insert(idx, item)
    
    return top_k

def mips_top_k(target: np.ndarray, k: int) -> List[str]:
    top_k = brute_top_k(target, k)
    print("Similarities: ", list(map(lambda t: t["similarity"], top_k)))
    return list(map(lambda t: t["embedding"], top_k))

class QType(Enum):
    QA = 0
    EDIT = 1

def compile_prompt(top_k: list[str], question: str, version: QType=QType.QA) -> str:
    if version == QType.QA:
        return "\n\n".join(top_k) + "\n\nAnswer the following question using the code above as reference: " + question + "\n\n"
    elif version == QType.EDIT:
        return "\n\n".join(top_k) + "\n\nEdit the above code to do the following:" + question + "\n\n"

K = 1
def answer(question: str, version: QType=QType.QA) -> Tuple[str, List[Dict[str, str]]]:
    target = gpt.embed_single(question)
    top_k = mips_top_k(target, K)
    texts = list(map(lambda e: e["text"], top_k))
    prompt = compile_prompt(texts, question, version=version)
    return gpt.complete(prompt, max_tokens=1024), top_k

def chunk_file(path: str, chunk_size: int=1024 - 256) -> List: # -256 to give room for question
    with open(path, "r") as f:
        code = f.read()
        chunks = []

        try:
            nodes = ast.parse(code).body
        except:
            # Unparsable file, just do a dumb chunking
            for i in range(0, len(code), chunk_size):
                chunks.append({
                    "text": code[i:i+chunk_size],
                    "path": path,
                    "name": ""
                })
            return chunks

        curr_size = 0
        curr_chunk = ""
        curr_chunk_name = ""
        for node in nodes:
            node_code = ast.unparse(node)
            curr_size += len(gpt2_tokenizer.encode(node_code))

            # A sketchy way of giving a fn or class or variable name as an anchor to link to the pdoc
            if hasattr(node, "name"):
                curr_chunk_name = node.name

            if curr_size > chunk_size:
                chunks.append({
                    "text": curr_chunk,
                    "path": path,
                    "name": curr_chunk_name
                })
                curr_size = 0
                curr_chunk = node_code
            else:
                curr_chunk += "\n" + node_code
        
        chunks.append({
            "text": curr_chunk,
            "path": path,
            "name": curr_chunk_name
        })

        return chunks

def load_codebase(path: str):
    try:
        with open("cached_embeddings.pkl", "rb") as f:
            global embeddings
            embeddings = pickle.load(f)
    except BaseException:
        print("File not found, loading data...")

        chunks = []

        for subpath, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    chunks += chunk_file(os.path.join(subpath, file))

        if len(chunks) > 0:
            load_embeddings(chunks) # Need a way to store metadata with the embeddings

        with open("cached_embeddings.pkl", "wb") as f:
            pickle.dump(embeddings, f)

@app.command()
def repl(inp: str, output: str, gen_docs: bool=False):
    if gen_docs:
        # write_ds(input, output)
        pass

    load_codebase(inp)

    # Start pdoc server in a separate process
    pdoc_proc = subprocess.Popen(["pdoc", inp], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        question = input("Question: ")
        ans, top_k = answer(question, version=QType.EDIT)
        print("Answer: ", ans)
        print("Relevant documentation here:")
        for top in top_k:
            print(f"http://localhost:8080/{top['path'].replace('..', 'talking-codebases').replace('.py', '')}#{top['name']}")

@app.command()
def ask(inp: str, question: str):
    load_codebase(inp)
    ans, top_k = answer(question, version=QType.QA)
    print(ans)

@app.command()
def loaded(inp: str):
    try:
        with open("cached_embeddings.pkl", "rb") as f:
            global embeddings
            embeddings = pickle.load(f)
            print("True")
    except BaseException:
        print("False")

if __name__ == "__main__":
    app()