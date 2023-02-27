import React, { useState } from "react";
import { H3, TextArea, Button, Pre, Loader } from "../components";
import styled from "styled-components";
import { createVscListener, useVscMessageValue } from "../vscode";

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

function MainTab() {
  const [responseLoading, setResponseLoading] = useState(false);
  const [suggestion, setSuggestion] = useVscMessageValue(
    ["suggestFix", "explainCode", "listTenThings"],
    ""
  );
  createVscListener("makeEdit", (event) => {
    setResponseLoading(false);
  });

  return (
    <>
      <h1>Debug Panel</h1>

      <H3>Code Sections</H3>
      <div className="multiselectContainer"></div>

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
        id="traceback"
        className="traceback"
        name="traceback"
        rows={4}
        cols={50}
        placeholder="Paste stack trace here"
      ></TextArea>

      <select
        hidden
        id="relevantVars"
        className="relevantVars"
        name="relevantVars"
      ></select>

      <ButtonDiv>
        <Button>Explain Code</Button>
        <Button>Generate Ideas</Button>
        <Button disabled>Suggest Fix</Button>
        <Button disabled>Create Test</Button>
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
