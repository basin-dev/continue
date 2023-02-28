import { configureStore } from "@reduxjs/toolkit";
import debugContextReducer from "./slices/debugContexSlice";
import { Range } from "vscode";
import { DebugContext } from "../../schema/DebugContext";

export interface RootStore {
  debugContext: DebugContext; // TODO: Hook up to JSON Schema with everything else?
  workspacePath: string | undefined;
}

const store = configureStore({
  reducer: {
    debugContext: debugContextReducer,
  },
});

export default store;
