import { useEffect, useState } from "react";
import "vscode-webview";

declare const vscode: any;

export function postVscMessage(type: string, data: any) {
  if (typeof vscode === "undefined") {
    return;
  }
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
  window.addEventListener("message", (event) => {
    if (event.data.type === messageType) {
      setValue(event.data.value);
    }
  });
  return [value, setValue];
}

export async function withProgress(title: string, fn: () => Promise<any>) {
  postVscMessage("withProgress", { title, done: false });
  return fn().finally(() => {
    postVscMessage("withProgress", { title, done: true });
  });
}
