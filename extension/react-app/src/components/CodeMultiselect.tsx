import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { Button, buttonColor, defaultBorderRadius, secondaryDark } from ".";
import { useSelector } from "react-redux";
import { selectDebugContext } from "../../redux/selectors/debugContextSelectors";
import "../highlight/dark.min.css";
import hljs from "highlight.js";
import { postVscMessage } from "../vscode";
import { RootStore } from "../../redux/store";
import { useDispatch } from "react-redux";
import { updateValue } from "../../redux/slices/debugContexSlice";
import { RangeInFile } from "../../../src/client";

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
  border-bottom: 1px solid gray;
  padding-left: 4px;
  padding-right: 4px;
  & p {
    overflow-wrap: break-word;
    word-wrap: break-word;
    -ms-wrap-flow: break-word;
    overflow: hidden;
  }
`;

const MultiSelectOption = styled.div`
  border-radius: ${defaultBorderRadius};
  padding-top: 4px;
  cursor: pointer;
  background-color: ${secondaryDark};
`;

const DeleteSelectedRangeButton = styled(Button)`
  align-self: right;
  padding: 0px;
  margin-top: 0;
  aspect-ratio: 1/1;
  height: 28px;
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

//#region Path Formatting

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
  rangeInFile: RangeInFile,
  workspacePath: string | undefined
) {
  return `${formatPathRelativeToWorkspace(
    rangeInFile.filepath,
    workspacePath
  )} (lines ${rangeInFile.range.start.line + 1}-${
    rangeInFile.range.end.line + 1
  })`;
  // +1 because VSCode Ranges are 0-indexed
}

//#endregion

type RangeInFileWithCode = RangeInFile & { code: string };

function CodeMultiselect(props: {
  onChange?: (selectedRanges: RangeInFile[]) => void;
}) {
  // State
  const [selectedRanges, setSelectedRanges] = useState<RangeInFileWithCode[]>(
    []
  );
  const [selectedMask, setSelectedMask] = useState<boolean[]>([]);
  const [highlightLocked, setHighlightLocked] = useState(false);
  const [canUpdateLast, setCanUpdateLast] = useState(true);
  const workspacePath = useSelector((state: RootStore) => state.workspacePath);

  // Redux
  const dispatch = useDispatch();
  const debugContext = useSelector(selectDebugContext);
  // useEffect(() => {
  //   // setSelectedRanges(debugContext.rangesInFiles || []);
  //   // setSelectedMask(debugContext.rangesInFiles?.map(() => true) || []);
  // }, []);

  //#region Update Functions
  function filterSelectedRanges(selectedRanges: RangeInFile[]) {
    return selectedRanges.filter((range: RangeInFile, index: number) => {
      return selectedMask[index];
    });
  }

  let onChangeTimout: NodeJS.Timeout | undefined = undefined;

  function onChangeUpdate() {
    // Debounce
    if (onChangeTimout) {
      clearTimeout(onChangeTimout);
    }
    onChangeTimout = setTimeout(() => {
      if (props.onChange) {
        props.onChange(filterSelectedRanges(selectedRanges));
      }
      dispatch(
        updateValue({
          key: "rangesInFiles",
          value: filterSelectedRanges(selectedRanges),
        })
      );
    }, 200);
  }

  function deleteSelectedRange(index: number) {
    let updatedRanges = [...selectedRanges];
    let updatedMask = [...selectedMask];
    updatedRanges.splice(index, 1);
    updatedMask.splice(index, 1);
    setSelectedRanges(updatedRanges);
    setSelectedMask(updatedMask);
    onChangeUpdate();
  }

  function addSelectedRange(range: RangeInFileWithCode) {
    if (
      canUpdateLast &&
      selectedRanges.length > 0 &&
      range.filepath === selectedRanges[selectedRanges.length - 1].filepath
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
    let updatedMask = [...selectedMask];
    updatedMask[index] = false;
    setSelectedMask(updatedMask);
    onChangeUpdate();
  }
  //#endregion

  useEffect(() => {
    let eventListener = (event: any) => {
      switch (event.data.type) {
        case "highlightedCode":
          if (!highlightLocked) {
            addSelectedRange(event.data.rangeInFile);
          }
          break;
        case "findSuspiciousCode":
          event.data.codeLocations.forEach((c: RangeInFileWithCode) => {
            addSelectedRange(c);
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
          postVscMessage("listTenThings", { debugContext });
          break;
      }
    };
    window.addEventListener("message", eventListener);
    return () => window.removeEventListener("message", eventListener);
  }, [debugContext, highlightLocked]);

  useEffect(() => {
    hljs.highlightAll();
  });

  return (
    <MultiSelectContainer>
      {selectedRanges.map((range: RangeInFileWithCode, index: number) => {
        return (
          <MultiSelectOption
            key={index}
            style={{
              border: `1px solid ${selectedMask[index] ? buttonColor : "gray"}`,
            }}
            onClick={() => {
              let updatedMask = [...selectedMask];
              updatedMask[index] = !selectedMask[index];
              setSelectedMask(updatedMask);
              onChangeUpdate();
            }}
          >
            <MultiSelectHeader>
              <p style={{ margin: "4px" }}>
                {formatFileRange(range, workspacePath)}
              </p>
              <DeleteSelectedRangeButton
                onClick={() => deleteSelectedRange(index)}
              >
                x
              </DeleteSelectedRangeButton>
            </MultiSelectHeader>
            <pre>
              <code
                className={"language-" + filenameToLanguage(range.filepath)}
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
