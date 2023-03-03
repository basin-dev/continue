import { createSlice } from "@reduxjs/toolkit";
import { RangeInFile, SerializedDebugContext } from "../../../src/client";
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
    rangesMask: [],
    vscMachineId: undefined,
    apiUrl: undefined,
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
    addRangeInFile: (
      state: RootStore,
      action: {
        type: string;
        payload: {
          rangeInFile: RangeInFile;
          canUpdateLast: boolean;
        };
      }
    ) => {
      let rangesInFiles = state.debugContext.rangesInFiles;
      if (
        action.payload.canUpdateLast &&
        rangesInFiles.length > 0 &&
        rangesInFiles[rangesInFiles.length - 1].filepath ===
          action.payload.rangeInFile.filepath
      ) {
        return {
          ...state,
          debugContext: {
            ...state.debugContext,
            rangesInFiles: [
              ...rangesInFiles.slice(0, rangesInFiles.length - 1),
              action.payload.rangeInFile,
            ],
          },
        };
      } else {
        return {
          ...state,
          debugContext: {
            ...state.debugContext,
            rangesInFiles: [
              ...state.debugContext.rangesInFiles,
              action.payload.rangeInFile,
            ],
          },
          rangesMask: [...state.rangesMask, true],
        };
      }
    },
    deleteRangeInFileAt: (
      state: RootStore,
      action: {
        type: string;
        payload: number;
      }
    ) => {
      return {
        ...state,
        debugContext: {
          ...state.debugContext,
          rangesInFiles: state.debugContext.rangesInFiles.filter(
            (_, index) => index !== action.payload
          ),
        },
        rangesMask: state.rangesMask.filter(
          (_, index) => index !== action.payload
        ),
      };
    },
    toggleSelectionAt: (
      state: RootStore,
      action: {
        type: string;
        payload: number;
      }
    ) => {
      return {
        ...state,
        rangesMask: state.rangesMask.map((_, index) =>
          index === action.payload
            ? !state.rangesMask[index]
            : state.rangesMask[index]
        ),
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
    setApiUrl: (
      state: RootStore,
      action: { type: string; payload: string }
    ) => ({
      ...state,
      apiUrl: action.payload,
    }),
    setVscMachineId: (
      state: RootStore,
      action: { type: string; payload: string }
    ) => ({
      ...state,
      vscMachineId: action.payload,
    }),
  },
});

export const {
  updateValue,
  setWorkspacePath,
  updateFileSystem,
  addRangeInFile,
  deleteRangeInFileAt,
  toggleSelectionAt,
  setApiUrl,
  setVscMachineId,
} = debugContextSlice.actions;
export default debugContextSlice.reducer;
