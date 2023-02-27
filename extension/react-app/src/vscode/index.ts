import { useEffect, useState } from "react";
import "vscode-webview";

const vscode = acquireVsCodeApi();

export function createVscListener(
  callback: (event: { data: any } & any) => void
) {
  useEffect(() => {
    window.addEventListener("message", (event) => {
      callback(event);
    });
  }, []);
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
