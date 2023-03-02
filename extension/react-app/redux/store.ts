import { configureStore } from "@reduxjs/toolkit";
import debugContextReducer from "./slices/debugContexSlice";
import { Range } from "vscode";
import { SerializedDebugContext } from "../../src/client";

export interface RootStore {
  debugContext: SerializedDebugContext;
  workspacePath: string | undefined;
}

const store = configureStore({
  reducer: debugContextReducer,
});

export default store;
