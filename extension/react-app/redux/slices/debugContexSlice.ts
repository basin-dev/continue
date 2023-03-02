import { createSlice } from "@reduxjs/toolkit";
import { SerializedDebugContext } from "../../../src/client";
import { RootStore } from "../store";

export const debugContextSlice = createSlice({
  name: "debugContext",
  initialState: {
    debugContext: {
      rangesInFiles: [],
      filesystem: {},
      traceback: undefined,
      description: undefined,
    },
    workspacePath: undefined,
  } as RootStore,
  reducers: {
    updateValue: (
      state: RootStore,
      action: {
        type: string;
        payload: { key: keyof SerializedDebugContext; value: any };
      }
    ) => {
      return {
        ...state,
        debugContext: {
          ...state.debugContext,
          [action.payload.key]: action.payload.value,
        },
      };
    },
    setWorkspacePath: (
      state: RootStore,
      action: { type: string; payload: string }
    ) => {
      return {
        ...state,
        workspacePath: action.payload,
      };
    },
  },
});

export const { updateValue, setWorkspacePath } = debugContextSlice.actions;
export default debugContextSlice.reducer;
