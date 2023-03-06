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
  return richContent;
}

function format(content: string) {
  let richContent: JSX.Element[] = [];

  let lastMatchIndex = -1;
  let insideBullet = false;
  let bullets = [];
  for (let match of content.matchAll(/[\*]/g)) {
    console.log("MATCH: ", match);
    let index = match.index;
    if (index !== undefined) {
      let text = content.substring(lastMatchIndex + 1, index);
      let richText = formatWithLinks(text);
      if (insideBullet) {
        bullets.push(<li>{richText}</li>);
      } else {
        richContent.push(<>{richText}</>);
        insideBullet = true;
      }
      lastMatchIndex = index;
    }
  }
  richContent.push(<ul>{bullets}</ul>);
  return richContent;
}

function MessageDiv(props: ChatMessage) {
  const [richContent, setRichContent] = React.useState<JSX.Element[]>([]);

  useEffect(() => {
    console.log("U");
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
