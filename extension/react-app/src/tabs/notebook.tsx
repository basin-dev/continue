import { Play } from "@styled-icons/heroicons-outline";
import { useSelector } from "react-redux";
import styled from "styled-components";
import { Button } from "../components";
import IterationContainer from "../components/IterationContainer";
import { useEffect, useState } from "react";
import { History } from "../../../schema/History";
import { HistoryNode } from "../../../schema/HistoryNode";
import StepContainer from "../components/StepContainer";

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

interface NotebookProps {
  apiBaseUrl: string;
  firstObservation?: any;
}

function Notebook(props: NotebookProps) {
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [history, setHistory] = useState<History | undefined>(undefined);

  useEffect(() => {
    if (sessionId === undefined) {
      (async () => {
        console.log("Notebook mounted");
        let resp = await fetch(props.apiBaseUrl + "/session", {
          method: "POST",
          headers: new Headers({
            "Content-Type": "application/json",
          }),
        });
        let json = await resp.json();
        setSessionId(json.session_id);

        if (props.firstObservation) {
          let resp = await fetch(props.apiBaseUrl + "/observation", {
            method: "POST",
            headers: new Headers({
              "x-continue-session-id": json.session_id,
            }),
            body: JSON.stringify({
              observation: props.firstObservation,
            }),
          });
        }
      })();
    }
  }, [props.firstObservation]);

  useEffect(() => {
    // Connect to a websocket to relay history and user updates
    if (sessionId) {
      console.log("Creating websocket", sessionId);
      let wsUrl =
        props.apiBaseUrl.replace("http", "ws") +
        "/ws?session_id=" +
        encodeURIComponent(sessionId);
      let ws = new WebSocket(wsUrl);
      ws.onopen = () => {
        console.log("Websocket opened");
        ws.send(JSON.stringify({ sessionId }));
      };
      ws.onmessage = (msg) => {
        console.log("Got message", msg);
        if (msg.data.type === "history") {
          setHistory(msg.data.history);
        }
      };
    }
  }, [sessionId]);

  // const iterations = useSelector(selectIterations);
  return (
    <TopNotebookDiv>
      <h1 className="m-4">Notebook</h1>
      {history?.timeline.map((node: HistoryNode, index: number) => {
        return <StepContainer historyNode={node} />;
      })}
      <StyledButton className="m-auto">
        <Play /> Continue
      </StyledButton>
    </TopNotebookDiv>
  );
}

export default Notebook;
