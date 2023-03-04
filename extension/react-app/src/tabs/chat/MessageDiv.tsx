import React from "react";
import { ChatMessage } from "../../../redux/store";
import styled from "styled-components";

const Container = styled.div<{ role: ChatMessage["role"] }>`
  background-color: ${(props) => {
    if (props.role === "user") {
      return "#455588";
    } else {
      return "lightgreen";
    }
  }};
  text-align: ${(props) => {
    if (props.role === "user") {
      return "right";
    } else {
      return "left";
    }
  }};
  border-radius: 8px;
  padding-top: 1px;
  padding-bottom: 1px;
  padding-left: 8px;
  padding-right: 8px;

  margin: 8px;
`;

function MessageDiv(props: ChatMessage) {
  return (
    <Container role={props.role}>
      <p>{props.content}</p>
    </Container>
  );
}

export default MessageDiv;
