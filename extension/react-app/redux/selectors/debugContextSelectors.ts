import { RootStore } from "../store";

const selectDebugContext = (state: RootStore) => state.debugContext;

const selectDebugContextValue = (state: RootStore, key: string) => {
  return (state.debugContext as any)[key];
};

export { selectDebugContext, selectDebugContextValue };
