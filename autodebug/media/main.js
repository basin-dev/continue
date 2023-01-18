(function () {
  const vscode = acquireVsCodeApi();

  const oldState = vscode.getState();

  document.querySelector("#startDebug").addEventListener("click", () => {
    startDebug();
  });

  // Handle messages sent from the extension to the webview
  window.addEventListener("message", (event) => {
    const message = event.data; // The json data that the extension sent
    switch (message.type) {
      case "something": {
        break;
      }
      case "something else": {
        break;
      }
    }
  });

  function startDebug() {
    vscode.postMessage({ type: "startDebug" });
  }
})();
