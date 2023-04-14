import { useEffect, useRef, useState } from "react";
import styled, { keyframes } from "styled-components";
import {
  appear,
  buttonColor,
  defaultBorderRadius,
  GradientBorder,
  MainTextInput,
  secondaryDark,
  vscBackground,
} from ".";
import { RangeInFile, FileEdit } from "../../../src/client";
import CodeBlock from "./CodeBlock";
import SubContainer from "./SubContainer";

import {
  ChevronDown,
  ChevronRight,
  Backward,
} from "@styled-icons/heroicons-outline";
import { HistoryNode } from "../../../schema/HistoryNode";
import ReactMarkdown from "react-markdown";
import ContinueButton from "./ContinueButton";

interface StepContainerProps {
  historyNode: HistoryNode;
  onReverse: () => void;
}

const MainDiv = styled.div`
  animation: ${appear} 0.3s ease-in-out;
`;

const StepContainerDiv = styled.div<{ open: boolean }>`
  background-color: ${(props) => (props.open ? vscBackground : secondaryDark)};
  border-radius: ${defaultBorderRadius};
  padding: 8px;
`;

const HeaderDiv = styled.div`
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
`;

const HeaderButton = styled.button`
  background-color: transparent;
  border: 1px solid white;
  border-radius: ${defaultBorderRadius};
  padding: 2px;
  cursor: pointer;
  color: white;

  &:hover {
    background-color: white;
    color: black;
  }
`;

const OnHoverDiv = styled.div`
  text-align: center;
  padding: 10px;
  animation: ${appear} 0.3s ease-in-out;
`;

const NaturalLanguageInput = styled(MainTextInput)`
  width: 80%;
`;

function StepContainer(props: StepContainerProps) {
  const [open, setOpen] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const naturalLanguageInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isHovered) {
      naturalLanguageInputRef.current?.focus();
    }
  }, [isHovered]);

  return (
    <MainDiv
      onMouseEnter={() => {
        setIsHovered(true);
      }}
      onMouseLeave={() => {
        setIsHovered(false);
      }}
    >
      <GradientBorder className="m-2 overflow-hidden">
        <StepContainerDiv open={open}>
          <HeaderDiv>
            <h4
              className="m-2 cursor-pointer"
              onClick={() => setOpen((prev) => !prev)}
            >
              {open ? (
                <ChevronDown size="1.4em" />
              ) : (
                <ChevronRight size="1.4em" />
              )}
              {props.historyNode.step.name as any}:
            </h4>
            <HeaderButton>
              <Backward size="1.6em" onClick={props.onReverse}></Backward>
            </HeaderButton>
          </HeaderDiv>

          <ReactMarkdown key={1}>
            {props.historyNode.step.description as any}
          </ReactMarkdown>

          {open && (
            <>
              {props.historyNode.observation && (
                <SubContainer title="Error">
                  <CodeBlock>Error Here</CodeBlock>
                </SubContainer>
              )}
              {/* {props.iterationContext.suggestedChanges.map((sc) => {
              return (
                <SubContainer title="Suggested Change">
                  {sc.filepath}
                  <CodeBlock>{sc.replacement}</CodeBlock>
                </SubContainer>
              );
            })} */}
            </>
          )}
        </StepContainerDiv>
      </GradientBorder>

      <OnHoverDiv hidden={!isHovered && !open}>
        <NaturalLanguageInput
          ref={naturalLanguageInputRef}
        ></NaturalLanguageInput>
        <ContinueButton></ContinueButton>
      </OnHoverDiv>
    </MainDiv>
  );
}

export default StepContainer;
