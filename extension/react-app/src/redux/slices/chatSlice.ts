import { createSlice } from "@reduxjs/toolkit";
import { ChatMessage, RootStore } from "../store";

export const chatSlice = createSlice({
  name: "chat",
  initialState: {
    messages: [
      {
        role: "user",
        content: "Hello, my name is Nate.",
      },
      {
        role: "assistant",
        content: "Hi Nate!\n* One\n * Two\n * Three\n How can I help?",
      },
    ],
    isStreaming: false,
  } as RootStore["chat"],
  reducers: {
    addMessage: (
      state,
      action: {
        type: string;
        payload: ChatMessage;
      }
    ) => {
      return {
        ...state,
        messages: [...state.messages, action.payload],
      };
    },
    streamUpdate: (state, action) => {
      if (!state.isStreaming) {
        return {
          ...state,
          messages: [
            ...state.messages,
            {
              role: "assistant",
              content: action.payload,
            },
          ],
          isStreaming: true,
        };
      } else {
        let lastMessage = state.messages[state.messages.length - 1];
        return {
          ...state,
          messages: [
            ...state.messages.slice(0, state.messages.length - 1),
            {
              ...lastMessage,
              content: lastMessage.content + action.payload,
            },
          ],
          isStreaming: true,
        };
      }
    },
    closeStream: (state) => {
      return {
        ...state,
        isStreaming: false,
      };
    },
    clearChat: (state) => {
      return {
        ...state,
        messages: [],
        isStreaming: false,
      };
    },
  },
});

export const { addMessage, streamUpdate, closeStream, clearChat } =
  chatSlice.actions;
export default chatSlice.reducer;
