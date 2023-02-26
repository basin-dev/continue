import React, { useState } from "react";
interface DebugPanelProps {
  tabs: {
    element: React.ReactElement;
    title: string;
  }[];
}

function DebugPanel(props: DebugPanelProps) {
  const [currentTab, setCurrentTab] = useState(0);
  return (
    <div className="gradient">
      <h1 className="bg-red-500">Title</h1>
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
    </div>
  );
}

export default DebugPanel;
