import { createSlice } from "@reduxjs/toolkit";
import { RootStore } from "../store";

export const chatSlice = createSlice({
  name: "chat",
  initialState: [] as RootStore["chat"],
  reducers: {
    addMessage: (state, action) => {
      return [...state, action.payload];
    },
  },
});

export const { addMessage } = chatSlice.actions;
export default chatSlice.reducer;
