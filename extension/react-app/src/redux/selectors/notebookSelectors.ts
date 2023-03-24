import { RootStore } from "../store";

const selectIterations = (state: RootStore) => {
  return state.notebook.iterations;
};

export { selectIterations };
