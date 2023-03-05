import { RootStore } from "../store";

const selectChatMessages = (state: RootStore) => {
  return state.chat.messages;
};

export { selectChatMessages };
