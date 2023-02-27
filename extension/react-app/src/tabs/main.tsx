import React, { useEffect, useState } from "react";
import { H3, TextArea, Button, Pre, Loader } from "../components";
import styled from "styled-components";
import { createVscListener, postVscMessage } from "../vscode";
import { useDebugContextValue } from "../../redux/hooks";
import CodeMultiselect from "../components/CodeMultiselect";
import { useSelector } from "react-redux";
import { selectDebugContext } from "../../redux/selectors/debugContextSelectors";

const ButtonDiv = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 4px;
  margin: 4px;
  flex-wrap: wrap;

  & button {
    flex-grow: 1;
  }
`;

const filenameToLanguage = {
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

function MainTab() {
  const [suggestion, setSuggestion] = useDebugContextValue("suggestion", "");
  const [traceback, setTraceback] = useDebugContextValue("traceback", "");
  const [selectedRanges, setSelectedRanges] = useDebugContextValue(
    "selectedRanges",
    []
  );

  const [responseLoading, setResponseLoading] = useState(false);
  const tracebackTextAreaRef = React.useRef<HTMLTextAreaElement>(null);

  const [highlightLocked, setHighlightLocked] = useState(false);
  const [workspacePath, setWorkspacePath] = useState<string | undefined>(
    undefined
  );

  function postVscMessageWithDebugContext(type: string) {
    let debugContext = useSelector(selectDebugContext);
    postVscMessage(type, { debugContext });
  }

  const [canUpdateLast, setCanUpdateLast] = useState(true);

  function addMultiselectOption(filename: string, range: any, code: string) {
    let ext = filename.split(".").pop();
    if (ext in filenameToLanguage) {
      codeElement.className = "language-" + filenameToLanguage[ext];
    }

    hljs.highlightElement(codeElement);
  }

  useEffect(() => {
    createVscListener((event) => {
      switch (event.data.type) {
        case "suggestFix":
        case "explainCode":
        case "listTenThings":
          setSuggestion(event.data.value);
          break;
        case "makeEdit":
          setResponseLoading(false);
          break;
        case "traceback":
          if (tracebackTextAreaRef.current) {
            tracebackTextAreaRef.current.value = event.data.value;
          }
          if (selectedRanges.length === 0) {
            postVscMessageWithDebugContext("findSuspiciousCode");
          }
          break;
        case "highlightedCode":
          let message = event.data;
          setWorkspacePath(message.workspacePath);
          if (!highlightLocked) {
            addMultiselectOption(message.filename, message.range, message.code);
          }
          break;
        case "findSuspiciousCode":
          clearMultiselectOptions();
          for (let codeLocation of message.codeLocations) {
            canUpdateLast = false;
            // It's serialized to be an array [startPos, endPos]
            let range = {
              start: {
                line: codeLocation.range[0].line,
                character: codeLocation.range[0].character,
              },
              end: {
                line: codeLocation.range[1].line,
                character: codeLocation.range[1].character,
              },
            };

            addMultiselectOption(
              codeLocation.filename,
              range,
              codeLocation.code
            );
          }
          canUpdateLast = true;
          setResponseLoading(true);
          postVscMessageWithDebugContext("listTenThings");
          break;
      }
    });
  });

  return (
    <>
      <h1>Debug Panel</h1>

      <H3>Code Sections</H3>
      <CodeMultiselect></CodeMultiselect>

      <H3>Bug Description</H3>
      <TextArea
        id="bugDescription"
        name="bugDescription"
        className="bugDescription"
        rows={4}
        cols={50}
        placeholder="Describe your bug..."
      ></TextArea>

      <H3>Stack Trace</H3>
      <TextArea
        ref={tracebackTextAreaRef}
        id="traceback"
        className="traceback"
        name="traceback"
        rows={4}
        cols={50}
        placeholder="Paste stack trace here"
        onChange={(e) => {
          setTraceback(e.target.value);
          postVscMessageWithDebugContext("findSuspiciousCode");
        }}
      ></TextArea>

      <select
        hidden
        id="relevantVars"
        className="relevantVars"
        name="relevantVars"
      ></select>

      <ButtonDiv>
        <Button
          onClick={() => {
            postVscMessageWithDebugContext("explainCode");
            setResponseLoading(true);
          }}
        >
          Explain Code
        </Button>
        <Button
          onClick={() => {
            postVscMessageWithDebugContext("suggestFix");
            setResponseLoading(true);
          }}
        >
          Generate Ideas
        </Button>
        <Button
          disabled
          onClick={() => {
            postVscMessageWithDebugContext("makeEdit");
            setResponseLoading(true);
          }}
        >
          Suggest Fix
        </Button>
        <Button
          disabled
          onClick={() => {
            postVscMessageWithDebugContext("generateUnitTest");
          }}
        >
          Create Test
        </Button>
      </ButtonDiv>
      <Loader hidden={!responseLoading}></Loader>

      <Pre className="fixSuggestion" hidden>
        {suggestion}
      </Pre>

      <br></br>
    </>
  );
}

export default MainTab;
