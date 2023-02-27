import { configureStore } from "@reduxjs/toolkit";
import debugContextReducer from "./slices/debugContexSlice";
import { Range } from "vscode";

interface CodeSelection {
  filename?: string;
  range?: Range;
  code?: string;
}

interface DebugContext {
  traceback?: string;
  description?: string;
  suggestion?: string;
  codeSelections?: CodeSelection[];
}

export interface RootStore {
  debugContext: DebugContext; // TODO: Hook up to JSON Schema with everything else?
}

const store = configureStore({
  reducer: {
    debugContext: debugContextReducer,
  },
});

export default store;
