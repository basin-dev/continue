import time
from typing import Tuple
from llm import OpenAI, LLM, HuggingFace
import numpy as np
from optimum.onnxruntime import ORTModelForCausalLM
from onnxruntime import InferenceSession

path = "Salesforce/codegen-2B-mono"
onnx_model = ORTModelForCausalLM.from_pretrained(path, from_transformers=True)
onnx_model.save_pretrained(path)
sess = InferenceSession(str(path / "model.onnx"), providers=["CUDAExecutionProvider"])


def benchmark(llm: LLM, n: int=1):
    times = []
    for _ in range(n):
        start = time.time()
        print("Completion: ", llm.complete("# Implement bubble sort in python"))
        end = time.time()
        times.append(end - start)
    return np.mean(times), np.std(times)

davinci = OpenAI()
codegen2b = HuggingFace(model_path="Salesforce/codegen-2B-mono")
codegen350m = HuggingFace(model_path="Salesforce/codegen-350M-mono")

if __name__ == "__main__":
    print("Davinci:", benchmark(davinci))
    print("Codegen:", benchmark(codegen350m))
