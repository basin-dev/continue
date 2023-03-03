import { configureStore } from "@reduxjs/toolkit";
import debugContextReducer from "./slices/debugContexSlice";
import { SerializedDebugContext } from "../../src/client";

export interface RootStore {
  debugContext: SerializedDebugContext;
  workspacePath: string | undefined;
  rangesMask: boolean[];
  apiUrl: string | undefined;
  vscMachineId: string | undefined;
}

const store = configureStore({
  reducer: debugContextReducer,
});

export default store;
