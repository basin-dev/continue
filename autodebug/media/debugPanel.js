(function () {
  const vscode = acquireVsCodeApi();
  const oldState = vscode.getState();

  const relevantVarsSelect = document.querySelector(".relevantVars");
  const highlightedCode = document.querySelector(".highlightedCode");
  const bugDescription = document.querySelector(".bugDescription");
  const stacktrace = document.querySelector(".stacktrace");
  const fixSuggestion = document.querySelector(".fixSuggestion");
  const listTenThingsButton = document.querySelector(".listTenThingsButton");
  const suggestFixButton = document.querySelector(".suggestFixButton");
  const makeEditButton = document.querySelector(".makeEditButton");

  let debugContext = {};

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
        stacktrace.value = message.traceback;
      }
      case "highlightedCode": {
        debugContext.filename = message.filename;
        debugContext.range = message.range;
        debugContext.code = message.code;
        highlightedCode.innerHTML = `${message.filename}, lines ${message.startLine}-${message.endLine}:\n\n<pre>${message.code}</pre>`;
        break;
      }
      case "findSuspiciousCode": {
        fixSuggestion.textContent = message.suspiciousCode;
        break;
      }
      case "listTenThings": {
        fixSuggestion.textContent = message.tenThings;
        makeEditButton.disabled = false;
        break;
      }
      case "suggestFix": {
        fixSuggestion.textContent = message.fixSuggestion;
        makeEditButton.disabled = false;
        break;
      }
    }
  });

  function gatherDebugContext() {
    debugContext.explanation = bugDescription.value;
    debugContext.stacktrace = stacktrace.value;
    debugContext.suggestion = fixSuggestion.innerHTML;
  }

  function listTenThings() {
    gatherDebugContext();
    fixSuggestion.innerHTML = `<div class="loader" ></div>`;
    vscode.postMessage({
      type: "listTenThings",
      debugContext,
    });
  }
  listTenThingsButton.addEventListener("click", listTenThings);

  function suggestFix() {
    gatherDebugContext();
    fixSuggestion.innerHTML = `<div class="loader" ></div>`;
    vscode.postMessage({
      type: "suggestFix",
      debugContext,
    });
  }
  suggestFixButton.addEventListener("click", suggestFix);

  makeEditButton.addEventListener("click", () => {
    gatherDebugContext();
    vscode.postMessage({
      type: "makeEdit",
      debugContext,
    });
  });

  function findSuspiciousCode() {
    gatherDebugContext();
    vscode.postMessage({
      type: "findSuspiciousCode",
      debugContext,
    });
  }
})();
