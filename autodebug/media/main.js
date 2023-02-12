(function () {
  const vscode = acquireVsCodeApi();

  const oldState = vscode.getState();

  document.querySelector(".ask-button").addEventListener("click", () => {
    askQuestion();
  });

  const traceback = document.querySelector(".traceback");
  const explanation = document.querySelector(".explanation");
  const answerDiv = document.querySelector(".answer");
  const question = document.querySelector(".question");

  // Handle messages sent from the extension to the webview
  window.addEventListener("message", (event) => {
    const message = event.data; // The json data that the extension sent
    switch (message.type) {
      case "answerQuestion": {
        // Clear the answer and display new one
        while (answerDiv.firstChild) {
          answerDiv.removeChild(answerDiv.firstChild);
        }
        answerDiv.appendChild(document.createTextNode(message.answer));
        break;
      }
      case "traceback": {
        traceback.value = message.traceback;
        break;
      }
    }
  });

  function startDebug() {
    vscode.postMessage({
      type: "startDebug",
      explanation: explanation.value,
      traceback: traceback.value,
    });
  }

  function askQuestion() {
    vscode.postMessage({ type: "askQuestion", question: question.value });

    // Clear answerDiv, add a loader
    while (answerDiv.firstChild) {
      answerDiv.removeChild(answerDiv.firstChild);
    }

    const loader = document.createElement("div");
    loader.classList.add("loader");
    answerDiv.appendChild(loader);
  }
})();
