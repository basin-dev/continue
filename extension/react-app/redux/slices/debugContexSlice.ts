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
    updateFileSystem: (
      state: RootStore,
      action: {
        type: string;
        payload: { [filepath: string]: string };
      }
    ) => {
      return {
        ...state,
        debugContext: {
          ...state.debugContext,
          filesystem: {
            ...state.debugContext.filesystem,
            ...action.payload,
          },
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

export const { updateValue, setWorkspacePath, updateFileSystem } =
  debugContextSlice.actions;
export default debugContextSlice.reducer;
