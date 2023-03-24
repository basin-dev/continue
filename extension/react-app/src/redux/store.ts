import { configureStore } from "@reduxjs/toolkit";
import debugStateReducer from "./slices/debugContexSlice";
import chatReducer from "./slices/chatSlice";
import configReducer from "./slices/configSlice";
import miscReducer from "./slices/miscSlice";
import { RangeInFile, SerializedDebugContext } from "../../../src/client";
import { IterationContext } from "../components/IterationContainer";
import notebookSlice from "./slices/notebookSlice";

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface RootStore {
  debugState: {
    debugContext: SerializedDebugContext;
    rangesMask: boolean[];
  };
  config: {
    workspacePath: string | undefined;
    apiUrl: string | undefined;
    vscMachineId: string | undefined;
  };
  chat: {
    messages: ChatMessage[];
    isStreaming: boolean;
  };
  misc: {
    highlightedCode: RangeInFile | undefined;
  };
  notebook: {
    iterations: IterationContext[];
  };
}

const store = configureStore({
  reducer: {
    debugState: debugStateReducer,
    chat: chatReducer,
    config: configReducer,
    misc: miscReducer,
    notebook: notebookSlice,
  },
});

export default store;
