import { useCallback, useEffect, useState } from "react";
import "vscode-webview";

export function createVscListener(
  messageType: string | string[],
  callback: (event: any) => void
) {
  if (typeof messageType === "string") {
    messageType = [messageType];
  }
  useEffect(() => {
    window.addEventListener("message", (event) => {
      const message = event.data;
      if (messageType.includes(message.type)) {
        callback(message);
      }
    });
  }, []);
}

export function useVscMessageValue(
  messageType: string | string[],
  initialValue?: any
) {
  const [value, setValue] = useState<any>(initialValue);
  createVscListener(messageType, (message) => {
    setValue(message.value);
  });
  return [value, setValue];
}

const vscode = acquireVsCodeApi();

export function postVscMessage(type: string, data: any) {
  vscode.postMessage({
    type,
    ...data,
  });
}

function vscCommunication() {
  const vscode = acquireVsCodeApi();

  // Handle messages sent from the extension to the webview
  window.addEventListener("message", (event) => {
    const message = event.data; // The json data that the extension sent
    switch (message.type) {
      case "relevantVars": {
        message.relevantVars.forEach((varName) => {
          let option = document.createElement("option");
          option.text = varName;
          option.value = varName;
          relevantVarsSelect.appendChild(option);
        });
        break;
      }
      case "traceback": {
        traceback.value = message.traceback;
        if (selectedRanges.length === 0) {
          findSuspiciousCode();
        }
        break;
      }
      case "highlightedCode": {
        updateState({ workspacePath: message.workspacePath });
        if (!highlightLocked) {
          addMultiselectOption(message.filename, message.range, message.code);
        }
        break;
      }
      case "findSuspiciousCode": {
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

          addMultiselectOption(codeLocation.filename, range, codeLocation.code);
        }
        canUpdateLast = true;
        listTenThings();
        break;
      }
      // case "listTenThings": {
      //   fixSuggestion.textContent = message.tenThings;
      //   break;
      // }
      // case "explainCode": {
      //   fixSuggestion.textContent = message.completion;
      //   break;
      // }
      // case "suggestFix": {
      //   fixSuggestion.textContent = message.fixSuggestion;
      //   break;
      // }
      // case "makeEdit": {
      //   // Edit is done
      //   makeEditLoader.hidden = true;
      //   break;
      // }
    }
    updateState({ debugContext: gatherDebugContext() });
  });
}
