import { Play } from "@styled-icons/heroicons-outline";
import React from "react";
import styled from "styled-components";
import { Button } from "../components";
import IterationContainer, {
  IterationContext,
} from "../components/IterationContainer";

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
  const iterations: IterationContext[] = [
    {
      codeSelections: [
        {
          filepath: "python/main.py",
          range: {
            start: { line: 1, character: 1 },
            end: { line: 1, character: 1 },
          },
        },
      ],
      instruction: "This is the instruction",
      suggestedChanges: [
        {
          filepath: "python/sum.py",
          range: {
            start: { line: 1, character: 1 },
            end: { line: 1, character: 1 },
          },
          replacement: `second = "two" => second = 2`,
        },
      ],
      status: "waiting",
      summary: "Iteration #1",
      action: "python3 main.py",
      error: `Traceback (most recent call last):
      File "/Users/natesesti/Desktop/continue/extension/examples/python/main.py", line 10, in <module>
        sum(first, second)
      File "/Users/natesesti/Desktop/continue/extension/examples/python/sum.py", line 2, in sum
        return a + b
    TypeError: unsupported operand type(s) for +: 'int' and 'str'
    `,
    },
  ];
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
