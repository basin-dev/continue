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
  },
});

export const { updateValue } = debugContextSlice.actions;
export default debugContextSlice.reducer;
