import { test, describe } from "mocha";
import * as assert from "assert";
import { PythonTracebackSnooper } from "../../terminal/snoopers";

suite("Snoopers", () => {
  suite("PythonTracebackSnooper", () => {
    test("should detect traceback given all at once", async () => {
      let traceback = `Traceback (most recent call last):
              File "/Users/natesesti/Desktop/continue/extension/examples/python/main.py", line 10, in <module>
                sum(first, second)
              File "/Users/natesesti/Desktop/continue/extension/examples/python/sum.py", line 2, in sum
                return a + b
            TypeError: unsupported operand type(s) for +: 'int' and 'str'`;
      let returnedTraceback = await new Promise((resolve) => {
        let callback = (data: string) => {
          resolve(data);
        };
        let snooper = new PythonTracebackSnooper(callback);
        snooper.onData(traceback);
      });
      assert(
        returnedTraceback === traceback,
        "Detected \n" + returnedTraceback
      );
    });
    test("should detect traceback given in chunks", () => {});

    test("should detect multi-line error message traceback", async () => {
      let traceback = `Traceback (most recent call last):
  File "/Users/ty/scripts/update.py", line 130, in <module>
    update_codebase_index()
  File "/Users/ty/scripts/update.py", line 117, in update_codebase_index
    create_codebase_index()
  File "/Users/ty/scripts/update.py", line 85, in create_codebase_index
    index = GPTFaissIndex(documents, faiss_index=faiss_index)
  File "/Users/ty/env/lib/python3.10/site-packages/tiktoken/core.py", line 322, in raise_disallowed_special_token
    raise ValueError(
ValueError: Encountered text corresponding to disallowed special token '<|endoftext|>'.
If you want this text to be encoded as a special token, pass it to \`allowed_special\`.
If you want this text to be encoded as normal text, disable the check.
To disable this check for all special tokens, pass \`disallowed_special=()\`.`;
      let returnedTraceback = await new Promise((resolve) => {
        let callback = (data: string) => {
          resolve(data);
        };
        let snooper = new PythonTracebackSnooper(callback);
        snooper.onData(traceback);
      });
      // Normalize whitespace for comparison (the test input has different indentation)
      const normalizeWhitespace = (s: string) => s.split("\n").map(line => line.trim()).filter(line => line.length > 0).join("\n");
      assert(
        normalizeWhitespace(returnedTraceback as string) === normalizeWhitespace(traceback),
        "Expected multi-line error message to be captured. Got:\n" + returnedTraceback
      );
    });

    test("should capture all continuation lines of error message", async () => {
      let traceback = `Traceback (most recent call last):
  File "test.py", line 1, in <module>
    raise ValueError("line1\nline2\nline3")
ValueError: line1
line2
line3`;
      let returnedTraceback = await new Promise((resolve) => {
        let callback = (data: string) => {
          resolve(data);
        };
        let snooper = new PythonTracebackSnooper(callback);
        snooper.onData(traceback);
      });
      const normalizeWhitespace = (s: string) => s.split("\n").map(line => line.trim()).filter(line => line.length > 0).join("\n");
      assert(
        normalizeWhitespace(returnedTraceback as string) === normalizeWhitespace(traceback),
        "Expected all error lines to be captured. Got:\n" + returnedTraceback
      );
    });
  });
});
