import { createSlice } from "@reduxjs/toolkit";
import { RootStore } from "../store";
import { IterationContext } from "../../components/IterationContainer";

export const notebookSlice = createSlice({
  name: "notebook",
  initialState: {
    iterations: [
      {
        codeSelections: [
          {
            filepath: "python/main.py",
            range: {
              start: { line: 1, character: 1 },
              end: { line: 1, character: 1 },
            },
          },
        ],
        instruction: "This is the instruction",
        suggestedChanges: [
          {
            filepath: "python/sum.py",
            range: {
              start: { line: 1, character: 1 },
              end: { line: 1, character: 1 },
            },
            replacement: `second = "two" => second = 2`,
          },
        ],
        status: "waiting",
        summary: "Iteration #1",
        action: "python3 main.py",
        error: `Traceback (most recent call last):
      File "/Users/natesesti/Desktop/continue/extension/examples/python/main.py", line 10, in <module>
        sum(first, second)
      File "/Users/natesesti/Desktop/continue/extension/examples/python/sum.py", line 2, in sum
        return a + b
    TypeError: unsupported operand type(s) for +: 'int' and 'str'
    `,
      },
    ],
  } as RootStore["notebook"],
  reducers: {
    addIteration: (
      state,
      action: {
        type: string;
        payload: IterationContext;
      }
    ) => {
      return {
        ...state,
        iterations: [...state.iterations, action.payload],
      };
    },
  },
});

export const { addIteration } = notebookSlice.actions;
export default notebookSlice.reducer;
