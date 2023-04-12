import { useState } from "react";
import styled from "styled-components";
import {
  defaultBorderRadius,
  GradientBorder,
  secondaryDark,
  vscBackground,
} from ".";
import { RangeInFile, FileEdit } from "../../../src/client";
import CodeBlock from "./CodeBlock";
import SubContainer from "./SubContainer";

import { ChevronDown, ChevronRight } from "@styled-icons/heroicons-outline";
import { HistoryNode } from "../../../schema/HistoryNode";

interface StepContainerProps {
  historyNode: HistoryNode;
}

const StepContainerDiv = styled.div<{ open: boolean }>`
  background-color: ${(props) => (props.open ? vscBackground : secondaryDark)};
  border-radius: ${defaultBorderRadius};
  padding: ${(props) => (props.open ? "2px" : "8px")};
`;

function StepContainer(props: StepContainerProps) {
  const [open, setOpen] = useState(false);

  return (
    <GradientBorder className="m-2 overflow-hidden">
      <StepContainerDiv open={open}>
        <p
          className="m-2 cursor-pointer"
          onClick={() => setOpen((prev) => !prev)}
        >
          {open ? <ChevronDown size="1.4em" /> : <ChevronRight size="1.4em" />}
          {/* {props.historyNode.step.summary} */}
          *Summary of step*
        </p>

        {open && (
          <>
            <SubContainer title="Action">
              {/* {props.historyNode.output?.[1] || "No action"} */}
              Action
            </SubContainer>
            {props.historyNode.output?.[0] && (
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
  );
}

export default StepContainer;
