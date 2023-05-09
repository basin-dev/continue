import { useCallback, useEffect, useRef, useState } from "react";
import styled, { keyframes } from "styled-components";
import {
  appear,
  buttonColor,
  defaultBorderRadius,
  MainContainerWithBorder,
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
  inFuture: boolean;
  onRefinement: (input: string) => void;
  onUserInput: (input: string) => void;
}

const MainDiv = styled.div<{ stepDepth: number; inFuture: boolean }>`
  opacity: ${(props) => (props.inFuture ? 0.3 : 1)};
  animation: ${appear} 0.3s ease-in-out;
  /* padding-left: ${(props) => props.stepDepth * 20}px; */
  overflow: hidden;
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
  const naturalLanguageInputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (isHovered) {
      naturalLanguageInputRef.current?.focus();
    }
  }, [isHovered]);

  const onTextInput = useCallback(() => {
    if (naturalLanguageInputRef.current) {
      props.onRefinement(naturalLanguageInputRef.current.value);
      naturalLanguageInputRef.current.value = "";
    }
  }, [naturalLanguageInputRef]);

  return (
    <MainDiv
      stepDepth={(props.historyNode.depth as any) || 0}
      inFuture={props.inFuture}
      onMouseEnter={() => {
        setIsHovered(true);
      }}
      onMouseLeave={() => {
        setIsHovered(false);
      }}
      hidden={props.historyNode.step.hide as any}
    >
      <MainContainerWithBorder
        className="m-2 overflow-hidden cursor-pointer"
        onClick={() => setOpen((prev) => !prev)}
      >
        <StepContainerDiv open={open}>
          <HeaderDiv>
            <h4 className="m-2 cursor-pointer">
              {open ? (
                <ChevronDown size="1.4em" />
              ) : (
                <ChevronRight size="1.4em" />
              )}
              {props.historyNode.step.name as any}:
            </h4>
            <HeaderButton
              onClick={(e) => {
                e.stopPropagation();
                props.onReverse();
              }}
            >
              <Backward size="1.6em" onClick={props.onReverse}></Backward>
            </HeaderButton>
          </HeaderDiv>

          <ReactMarkdown key={1} className="overflow-scroll">
            {props.historyNode.step.description as any}
          </ReactMarkdown>

          {props.historyNode.step.name === "Waiting for user input" && (
            <input
              className="m-auto p-2 rounded-md border-1 border-solid text-white w-3/4 border-gray-200 bg-vsc-background"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  props.onUserInput(e.currentTarget.value);
                }
              }}
              type="text"
              onSubmit={(ev) => {
                props.onUserInput(ev.currentTarget.value);
              }}
            />
          )}
          {props.historyNode.step.name === "Waiting for user confirmation" && (
            <>
              <input
                type="button"
                value="Cancel"
                className="m-4 p-2 rounded-md border border-solid text-white border-gray-200 bg-vsc-background cursor-pointer hover:bg-white hover:text-black"
              ></input>
              <input
                className="m-4 p-2 rounded-md border border-solid text-white border-gray-200 bg-vsc-background cursor-pointer hover:bg-white hover:text-black"
                onClick={(e) => {
                  props.onUserInput("ok");
                  e.preventDefault();
                  e.stopPropagation();
                }}
                type="button"
                value="Confirm"
              />
            </>
          )}

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
      </MainContainerWithBorder>

      <OnHoverDiv hidden={!open}>
        <NaturalLanguageInput
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onTextInput();
            }
          }}
          ref={naturalLanguageInputRef}
        ></NaturalLanguageInput>
        <ContinueButton onClick={onTextInput}></ContinueButton>
      </OnHoverDiv>
    </MainDiv>
  );
}

export default StepContainer;
