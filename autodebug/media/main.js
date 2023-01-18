(function () {
  const vscode = acquireVsCodeApi();

  const oldState = vscode.getState();

  document.querySelector(".startDebug").addEventListener("click", () => {
    startDebug();
  });

  document.querySelector(".ask-button").addEventListener("click", () => {
    askQuestion();
  });

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
      case "something else": {
        break;
      }
    }
  });

  function startDebug() {
    vscode.postMessage({ type: "startDebug" });
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
