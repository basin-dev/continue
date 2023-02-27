import React, { useState } from "react";
import styled from "styled-components";
import { Button, buttonColor, defaultBorderRadius, secondaryDark } from ".";
import { useDebugContextValue } from "../../redux/hooks";

const MultiSelectContainer = styled.div`
  border-radius: ${defaultBorderRadius};
  padding: 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const MultiSelectHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: left;
`;

const MultiSelectOption = styled.div`
  border-radius: ${defaultBorderRadius};
  padding-top: 4px;
  cursor: pointer;
  background-color: ${secondaryDark};
`;

const DeleteSelectedRangeButton = styled.button`
  align-self: right;
  padding: 0px;
  margin-top: 0;
  margin-right: 2px;
  border: none;
  aspect-ratio: 1/1;
  width: 20px;
  border-radius: ${defaultBorderRadius};

  &:hover:enabled {
    border: none;
  }
`;

const ToggleHighlightButton = styled.button`
  display: grid;
  justify-content: center;
  align-items: center;
  grid-template-columns: 30px 1fr;
  margin-left: 20px;
  order: 1;
  width: fit-content;
`;

function formatPathRelativeToWorkspace(path: string, workspacePath: string) {
  if (path.startsWith(workspacePath)) {
    return path.substring(workspacePath.length + 1);
  } else {
    return path;
  }
}

function formatFileRange(filename: string, range: any) {
  return `${formatPathRelativeToWorkspace(filename, workspacePath)} (lines ${
    range.start.line + 1
  }-${range.end.line + 1})`;
  // +1 because VSCode Ranges are 0-indexed
}

function CodeMultiselect(props: { onChange: (selectedRanges: any[]) => void }) {
  const [selectedRanges, setSelectedRanges] = useState<any[]>([]);
  const [selectedMask, setSelectedMask] = useState<boolean[]>([]);
  const [highlightLocked, setHighlightLocked] = useState(false);

  function deleteSelectedRange(index: number) {
    selectedRanges.splice(index, 1);
    selectedMask.splice(index, 1);
    setSelectedRanges([...selectedRanges]);
    setSelectedMask([...selectedMask]);
    props.onChange(selectedRanges);
  }

  function deselectRange(index: number) {
    selectedMask[index] = false;
    setSelectedMask([...selectedMask]);
    props.onChange(selectedRanges);
  }

  return (
    <MultiSelectContainer>
      {selectedRanges.map((range: any, index: number) => {
        return (
          <MultiSelectOption
            key={index}
            style={{
              border: `1px solid ${selectedMask[index] ? buttonColor : "gray"}`,
            }}
            onClick={() => {}}
          >
            <MultiSelectHeader>
              <p style={{ margin: "4px" }}>
                {formatFileRange(range.filename, range.range)}
              </p>
              <DeleteSelectedRangeButton
                onClick={() => deleteSelectedRange(index)}
              >
                x
              </DeleteSelectedRangeButton>
            </MultiSelectHeader>
            <pre>
              <code>{range.code}</code>
            </pre>
          </MultiSelectOption>
        );
      })}
      {selectedRanges.length === 0 && (
        <>
          <p>Highlight relevant code in the editor.</p>
          <ToggleHighlightButton
            onClick={() => {
              setCanUpdateLast(false);
              setHighlightLocked(!highlightLocked);
            }}
          >
            {highlightLocked ? (
              <>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20px"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke="currentColor"
                  className="w-6 h-6"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"
                  />
                </svg>{" "}
                Enable Highlight
              </>
            ) : (
              <>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20px"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke="currentColor"
                  className="w-6 h-6"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M13.5 10.5V6.75a4.5 4.5 0 119 0v3.75M3.75 21.75h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H3.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"
                  />
                </svg>{" "}
                Disable Highlight
              </>
            )}
          </ToggleHighlightButton>
        </>
      )}
    </MultiSelectContainer>
  );
}

export default CodeMultiselect;
