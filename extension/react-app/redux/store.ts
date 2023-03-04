import { configureStore } from "@reduxjs/toolkit";
import debugStateReducer from "./slices/debugContexSlice";
import chatReducer from "./slices/chatSlice";
import configReducer from "./slices/configSlice";
import { SerializedDebugContext } from "../../src/client";

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
  chat: ChatMessage[];
}

const store = configureStore({
  reducer: {
    debugState: debugStateReducer,
    chat: chatReducer,
    config: configReducer,
  },
});

export default store;
