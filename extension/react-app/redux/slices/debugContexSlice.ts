import { createSlice } from "@reduxjs/toolkit";

export const debugContextSlice = createSlice({
  name: "debugContext",
  initialState: {} as any,
  reducers: {
    updateValue: (
      state,
      action: { type: string; payload: { key: string; value: any } }
    ) => {
      state[action.payload.key] = action.payload.value;
    },
    setWorkspacePath: (state, action: { type: string; payload: string }) => {
      state.workspacePath = action.payload;
    },
  },
});

export const { updateValue, setWorkspacePath } = debugContextSlice.actions;
export default debugContextSlice.reducer;
