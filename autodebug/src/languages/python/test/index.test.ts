import { describe, expect, test } from "@jest/globals";
import { parseFirstStacktrace } from "..";

describe("Python Test Suite", () => {
  test("Traceback parser", () => {
    expect(parseFirstStacktrace("")).toBeUndefined();
  });
});
