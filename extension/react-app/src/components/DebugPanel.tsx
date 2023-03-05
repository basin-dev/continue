import React, { useEffect, useState } from "react";
import styled from "styled-components";
import { postVscMessage } from "../vscode";
import { useDispatch } from "react-redux";
import { setApiUrl, setVscMachineId } from "../redux/slices/configSlice";
interface DebugPanelProps {
  tabs: {
    element: React.ReactElement;
    title: string;
  }[];
}

const GradientContainer = styled.div`
  background: linear-gradient(
    101.79deg,
    #12887a 0%,
    #87245c 37.64%,
    #e12637 65.98%,
    #ffb215 110.45%
  );
  padding: 10px;
  margin: 0;
  height: 100%;
`;

const TabBar = styled.div<{ numTabs: number }>`
  display: grid;
  grid-template-columns: repeat(${(props) => props.numTabs}, 1fr);
`;

function DebugPanel(props: DebugPanelProps) {
  const dispatch = useDispatch();
  useEffect(() => {
    const eventListener = (event: any) => {
      if (event.data.type === "onLoad") {
        dispatch(setApiUrl(event.data.apiUrl));
        dispatch(setVscMachineId(event.data.vscMachineId));
      }
    };
    window.addEventListener("message", eventListener);
    postVscMessage("onLoad", {});
    return () => window.removeEventListener("message", eventListener);
  }, []);

  const [currentTab, setCurrentTab] = useState(0);

  return (
    <GradientContainer>
      <div className="h-full rounded-md overflow-scroll bg-vsc-background">
        <div className="h-full">
          <TabBar numTabs={props.tabs.length}>
            {props.tabs.map((tab, index) => {
              return (
                <div
                  key={index}
                  className={`p-2 h-full cursor-pointer text-center ${
                    index === currentTab
                      ? "bg-secondary-dark"
                      : "bg-vsc-background"
                  }`}
                  onClick={() => setCurrentTab(index)}
                >
                  {tab.title}
                </div>
              );
            })}
          </TabBar>
          {props.tabs.map((tab, index) => {
            return (
              <div
                key={index}
                className="pl-5 pr-5 pb-5"
                hidden={index !== currentTab}
              >
                {tab.element}
              </div>
            );
          })}
        </div>
      </div>
    </GradientContainer>
  );
}

export default DebugPanel;
