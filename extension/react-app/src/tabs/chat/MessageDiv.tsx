import React from "react";
import { ChatMessage } from "../../../redux/store";
import styled from "styled-components";
import { buttonColor, secondaryDark } from "../../components";

const Container = styled.div`
  padding-left: 8px;
  padding-right: 8px;
  border-radius: 8px;
  margin: 3px;
  width: fit-content;
  background-color: ${(props) => {
    if (props.role === "user") {
      return buttonColor;
    } else {
      return secondaryDark;
    }
  }};
  float: ${(props) => {
    if (props.role === "user") {
      return "right";
    } else {
      return "left";
    }
  }};
  display: block;
`;

function MessageDiv(props: ChatMessage) {
  return (
    <>
      <div className="overflow-auto">
        <Container role={props.role}>
          <p>{props.content}</p>
        </Container>
      </div>
    </>
  );
}

export default MessageDiv;
