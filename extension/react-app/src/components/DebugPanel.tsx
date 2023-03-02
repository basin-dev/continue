import React, { useState } from "react";
import styled from "styled-components";
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

function DebugPanel(props: DebugPanelProps) {
  const [currentTab, setCurrentTab] = useState(0);
  return (
    <GradientContainer>
      <div className="h-full rounded-md overflow-hidden bg-vsc-background">
        <div>
          <div
            className={`grid grid-cols-${props.tabs.length} border-b-secondary-dark border-b`}
          >
            {props.tabs.map((tab, index) => {
              return (
                <div
                  key={index}
                  className={`p-2 cursor-pointer text-center ${
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
          </div>
          {props.tabs.map((tab, index) => {
            return (
              <div
                key={index}
                className="pl-5 pr-5 pt-2"
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
