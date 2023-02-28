import { useEffect, useState } from "react";
import "vscode-webview";

declare const vscode: any;

export function createVscListener(callback: (event: MessageEvent) => void) {
  window.addEventListener("message", (event) => {
    console.log("Event received", event.data);
    callback(event);
  });
}

export function postVscMessage(type: string, data: any) {
  vscode.postMessage({
    type,
    ...data,
  });
}

export function useVscMessageValue(
  messageType: string | string[],
  initialValue?: any
) {
  const [value, setValue] = useState<any>(initialValue);
  createVscListener((event) => {
    if (event.data.type === messageType) {
      setValue(event.data.value);
    }
  });
  return [value, setValue];
}
