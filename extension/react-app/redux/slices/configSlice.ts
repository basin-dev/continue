import { createSlice } from "@reduxjs/toolkit";
import { RootStore } from "../store";

export const configSlice = createSlice({
  name: "config",
  initialState: {} as RootStore["config"],
  reducers: {
    setWorkspacePath: (
      state: RootStore["config"],
      action: { type: string; payload: string }
    ) => {
      return {
        ...state,
        workspacePath: action.payload,
      };
    },
    setApiUrl: (
      state: RootStore["config"],
      action: { type: string; payload: string }
    ) => ({
      ...state,
      apiUrl: action.payload,
    }),
    setVscMachineId: (
      state: RootStore["config"],
      action: { type: string; payload: string }
    ) => ({
      ...state,
      vscMachineId: action.payload,
    }),
  },
});

export const { setVscMachineId, setApiUrl, setWorkspacePath } =
  configSlice.actions;
export default configSlice.reducer;
