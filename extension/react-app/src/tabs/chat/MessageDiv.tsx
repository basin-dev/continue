import React, { useEffect } from "react";
import { ChatMessage } from "../../redux/store";
import styled from "styled-components";
import {
  buttonColor,
  defaultBorderRadius,
  secondaryDark,
} from "../../components";
import VSCodeFileLink from "../../components/VSCodeFileLink";
import ReactMarkdown from "react-markdown";
import "../../highlight/dark.min.css";
import hljs from "highlight.js";
import { useSelector } from "react-redux";
import { selectIsStreaming } from "../../redux/selectors/chatSelectors";

const Container = styled.div`
  padding-left: 8px;
  padding-right: 8px;
  border-radius: 8px;
  margin: 3px;
  width: fit-content;
  max-width: 100%;
  overflow: scroll;
  height: fit-content;
  overflow: hidden;
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

  & pre {
    border: 1px solid gray;
    border-radius: ${defaultBorderRadius};
  }
`;

function MessageDiv(props: ChatMessage) {
  const [richContent, setRichContent] = React.useState<JSX.Element[]>([]);
  const isStreaming = useSelector(selectIsStreaming);

  useEffect(() => {
    if (!isStreaming) {
      hljs.highlightAll();
    }
  }, [richContent, isStreaming]);

  useEffect(() => {
    setRichContent([<ReactMarkdown>{props.content}</ReactMarkdown>]);
  }, [props.content]);

  return (
    <>
      <div className="overflow-auto">
        <Container role={props.role}>
          <p>{richContent}</p>
        </Container>
      </div>
    </>
  );
}

export default MessageDiv;
