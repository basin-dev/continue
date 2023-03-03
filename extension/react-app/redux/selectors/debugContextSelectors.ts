import { RootStore } from "../store";

const selectDebugContext = (state: RootStore) => {
  return {
    ...state.debugContext,
    rangesInFiles: state.debugContext.rangesInFiles.filter(
      (_, index) => state.rangesMask[index]
    ),
  };
};

const selectAllRangesInFiles = (state: RootStore) => {
  return state.debugContext.rangesInFiles;
};

const selectRangesMask = (state: RootStore) => {
  return state.rangesMask;
};

const selectDebugContextValue = (state: RootStore, key: string) => {
  return (state.debugContext as any)[key];
};

export {
  selectDebugContext,
  selectDebugContextValue,
  selectAllRangesInFiles,
  selectRangesMask,
};
