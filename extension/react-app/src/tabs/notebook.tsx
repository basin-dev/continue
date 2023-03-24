import { Play } from "@styled-icons/heroicons-outline";
import React from "react";
import { useSelector } from "react-redux";
import styled from "styled-components";
import { Button } from "../components";
import IterationContainer, {
  IterationContext,
} from "../components/IterationContainer";
import { selectIterations } from "../redux/selectors/notebookSelectors";

let StyledButton = styled(Button)`
  margin: auto;
  display: grid;
  grid-template-columns: 30px 1fr;
  align-items: center;
`;

let TopNotebookDiv = styled.div`
  display: grid;
  grid-template-columns: 1fr;
`;

function Notebook() {
  const iterations = useSelector(selectIterations);
  return (
    <TopNotebookDiv>
      <h1 className="m-4">Notebook</h1>
      {iterations.map((iteration) => {
        return <IterationContainer iterationContext={iteration} />;
      })}
      <StyledButton className="m-auto">
        <Play /> Continue
      </StyledButton>
    </TopNotebookDiv>
  );
}

export default Notebook;
