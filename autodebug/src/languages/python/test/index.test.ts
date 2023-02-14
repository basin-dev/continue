import { describe, expect, test } from "@jest/globals";
import { parseFirstStacktrace } from "..";

describe("Python Test Suite", () => {
  test("Traceback parser", () => {
    expect(parseFirstStacktrace("")).toBeUndefined();
  });

  let onboarding_trace = `Traceback (most recent call last):
  File "/Users/ty/.vscode/extensions/basin.autodebug-0.0.1/examples/python/main.py", line 10, in <module>
    sum(first, second)
  File "/Users/ty/.vscode/extensions/basin.autodebug-0.0.1/examples/python/sum.py", line 2, in sum
    return a + b
  TypeError: unsupported operand type(s) for +: 'int' and 'str'`

  test("", () => {
    expect(parseFirstStacktrace(onboarding_trace)).toBe(onboarding_trace);
  });
});