import React, { useEffect } from "react";
import { ChatMessage } from "../../redux/store";
import styled from "styled-components";
import { buttonColor, secondaryDark } from "../../components";
import VSCodeFileLink from "../../components/VSCodeFileLink";

const Container = styled.div`
  padding-left: 8px;
  padding-right: 8px;
  border-radius: 8px;
  margin: 3px;
  width: fit-content;
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
`;

function formatWithLinks(content: string) {
  let richContent: JSX.Element[] = [];

  let lastMatchIndex = -1;
  let insideTicks = false;
  let tickIsPath = false;
  for (let match of content.matchAll(/[`]/g)) {
    let index = match.index;
    if (index !== undefined) {
      if (insideTicks && tickIsPath) {
        let path = content.slice(lastMatchIndex + 1, index);
        richContent.push(
          <VSCodeFileLink
            path={path}
            text={" " + path.split("/").at(-1) + " "}
          />
        );
        insideTicks = false;
      } else if (insideTicks && !tickIsPath) {
        richContent.push(
          <code>{content.substring(lastMatchIndex + 1, index)}</code>
        );
        insideTicks = false;
      } else {
        richContent.push(<>{content.substring(lastMatchIndex + 1, index)}</>);
        insideTicks = true;
        tickIsPath = content[index + 1] === "/";
      }
      lastMatchIndex = index;
    }
  }

  if (richContent.length === 0) {
    richContent = [<>{content}</>];
  }

  return richContent;
}

function format(content: string) {
  let richContent: JSX.Element[] = [];

  // Replace bullet point lines with <li> tags using regex
  let currentUl: JSX.Element[] = [];
  const updateUl = () => {
    if (currentUl.length > 0) {
      richContent.push(<ul>{currentUl}</ul>);
      currentUl = [];
    }
  };
  let endOfLastMatch = -1;
  for (let bullet of content.matchAll(/[\*-] (.*)\n/g)) {
    if (bullet.index === undefined) continue;

    let startOfThisMatch = bullet.index;
    if (endOfLastMatch < startOfThisMatch) {
      updateUl();
      richContent.push(
        <>{content.substring(endOfLastMatch + 1, startOfThisMatch)}</>
      );
    }

    endOfLastMatch = startOfThisMatch + bullet[0].length;
    currentUl.push(<li>{formatWithLinks(bullet[1])}</li>);
  }

  updateUl();

  if (endOfLastMatch < content.length) {
    richContent.push(<>{content.substring(endOfLastMatch + 1)}</>);
  }

  return richContent;
}

function MessageDiv(props: ChatMessage) {
  const [richContent, setRichContent] = React.useState<JSX.Element[]>([]);

  useEffect(() => {
    setRichContent(format(props.content));
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
