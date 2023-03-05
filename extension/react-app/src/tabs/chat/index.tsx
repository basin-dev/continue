import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { selectChat } from "../../redux/selectors/chatSelectors";
import MessageDiv from "./MessageDiv";
import styled from "styled-components";
import { addMessage } from "../../redux/slices/chatSlice";

const TextEntryBar = styled.input`
  width: 100%;
  height: 20px;
  border-radius: 16px;
  padding: 8px;
  border: 1px solid white;
  background-color: black;
  color: white;
`;

function ChatTab() {
  const dispatch = useDispatch();
  const chatMessages = useSelector(selectChat);
  return (
    <div>
      <h1>Chat</h1>
      {chatMessages.map((message) => {
        return <MessageDiv {...message}></MessageDiv>;
      })}
      <TextEntryBar
        type="text"
        placeholder="Enter your message here"
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            dispatch(
              addMessage({ content: e.currentTarget.value, role: "user" })
            );
            (e.target as any).value = "";
          }
        }}
      ></TextEntryBar>
    </div>
  );
}

export default ChatTab;
