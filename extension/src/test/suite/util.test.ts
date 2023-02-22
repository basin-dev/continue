import { test, describe, expect } from "@jest/globals";
import { convertSingleToDoubleQuoteJSON } from "../../util/util";

describe("utils.ts", () => {
  test("convertSingleToDoubleQuoteJson", () => {
    let pairs = [
      [`{'a': 'b'}`, `{"a": "b"}`],
      [`{'a': "b", "c": 'd'}`, `{"a": "b", "c": "d"}`],
      [`{'a': '\\'"'}`, `{"a": "'\\""}`],
    ];
    for (let pair of pairs) {
      let result = convertSingleToDoubleQuoteJSON(pair[0]);
      expect(result).toBe(pair[1]);
      JSON.parse(result);
    }
  });
});
