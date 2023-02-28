import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { Button, buttonColor, defaultBorderRadius, secondaryDark } from ".";
import { useDebugContextValue } from "../../redux/hooks";
import { createVscListener } from "../vscode";
import { useSelector } from "react-redux";
import { selectDebugContext } from "../../redux/selectors/debugContextSelectors";
import "../highlight/dark.min.css";
import hljs from "highlight.js";
import { postVscMessage } from "../vscode";
import { RootStore } from "../../redux/store";

//#region Styled Components

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

const ToggleHighlightButton = styled(Button)`
  display: grid;
  justify-content: center;
  align-items: center;
  grid-template-columns: 30px 1fr;
  margin-left: 20px;
  order: 1;
  width: fit-content;
`;

//#endregion

const filenameToLanguageMap: any = {
  py: "python",
  js: "javascript",
  ts: "typescript",
  html: "html",
  css: "css",
  java: "java",
  c: "c",
  cpp: "cpp",
  cs: "csharp",
  go: "go",
  rb: "ruby",
  rs: "rust",
  swift: "swift",
  php: "php",
  scala: "scala",
  kt: "kotlin",
  dart: "dart",
  hs: "haskell",
  lua: "lua",
  pl: "perl",
  r: "r",
  sql: "sql",
  vb: "vb",
  xml: "xml",
  yaml: "yaml",
};

function filenameToLanguage(filename: string): string {
  const extension = filename.split(".").pop();
  if (extension === undefined) {
    return "";
  }
  return filenameToLanguageMap[extension] || "";
}

function formatPathRelativeToWorkspace(
  path: string,
  workspacePath: string | undefined
) {
  if (workspacePath === undefined) {
    return path;
  }
  if (path.startsWith(workspacePath)) {
    return path.substring(workspacePath.length + 1);
  } else {
    return path;
  }
}

function formatFileRange(
  filename: string,
  range: any,
  workspacePath: string | undefined
) {
  return `${formatPathRelativeToWorkspace(filename, workspacePath)} (lines ${
    range.start.line + 1
  }-${range.end.line + 1})`;
  // +1 because VSCode Ranges are 0-indexed
}

function CodeMultiselect(props: {
  onChange?: (selectedRanges: any[]) => void;
}) {
  const [selectedRanges, setSelectedRanges] = useState<any[]>([]);
  const [selectedMask, setSelectedMask] = useState<boolean[]>([]);
  const [highlightLocked, setHighlightLocked] = useState(false);
  const [canUpdateLast, setCanUpdateLast] = useState(true);
  const debugContext = useSelector(selectDebugContext);
  const workspacePath = useSelector((state: RootStore) => state.workspacePath);

  function filterSelectedRanges(selectedRanges: any[]) {
    return selectedRanges.filter((range: any, index: number) => {
      return selectedMask[index];
    });
  }

  function onChangeUpdate() {
    if (props.onChange) {
      props.onChange(filterSelectedRanges(selectedRanges));
    }
  }

  function deleteSelectedRange(index: number) {
    selectedRanges.splice(index, 1);
    selectedMask.splice(index, 1);
    setSelectedRanges([...selectedRanges]);
    setSelectedMask([...selectedMask]);
    onChangeUpdate();
  }

  function addSelectedRange(range: any) {
    if (
      canUpdateLast &&
      selectedRanges.length > 0 &&
      range.filename === selectedRanges[selectedRanges.length - 1].filename
    ) {
      let updatedRanges = [...selectedRanges];
      updatedRanges[updatedRanges.length - 1] = range;
    } else {
      setSelectedRanges([...selectedRanges, range]);
      setSelectedMask([...selectedMask, true]);
    }
    onChangeUpdate();
  }

  function deselectRange(index: number) {
    selectedMask[index] = false;
    setSelectedMask([...selectedMask]);
    onChangeUpdate();
  }

  useEffect(() => {
    createVscListener((event) => {
      switch (event.data.type) {
        case "highlightedCode":
          if (!highlightLocked) {
            addSelectedRange(event.data);
          }
          break;
        case "findSuspiciousCode":
          event.data.codeLocations.forEach((c: any) => {
            addSelectedRange(c.range);
          });

          // It's serialized to be an array [startPos, endPos]
          // let range = {
          //   start: {
          //     line: codeLocation.range[0].line,
          //     character: codeLocation.range[0].character,
          //   },
          //   end: {
          //     line: codeLocation.range[1].line,
          //     character: codeLocation.range[1].character,
          //   },
          // };
          setCanUpdateLast(true);
          // setResponseLoading(true);
          postVscMessage("listTenThings", debugContext);
          break;
      }
    });
  });

  useEffect(() => {
    hljs.highlightAll();
  }, selectedRanges);

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
                {formatFileRange(range.filename, range.range, workspacePath)}
              </p>
              <DeleteSelectedRangeButton
                onClick={() => deleteSelectedRange(index)}
              >
                x
              </DeleteSelectedRangeButton>
            </MultiSelectHeader>
            <pre>
              <code
                className={"language-" + filenameToLanguage(range.filename)}
              >
                {range.code}
              </code>
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
                  strokeWidth="1.5"
                  stroke="currentColor"
                  className="w-6 h-6"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
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
                  strokeWidth="1.5"
                  stroke="currentColor"
                  className="w-6 h-6"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
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
