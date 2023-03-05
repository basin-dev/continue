import { RootStore } from "../store";

const selectChat = (state: RootStore) => {
  return state.chat;
};

export { selectChat };
