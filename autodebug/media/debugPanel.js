console.log("Debug Panel Loaded");

const relevantVarsSelect = document.getElementById("relevantVars");

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
    case "something else": {
      break;
    }
  }
});

function sendMessageBack() {
  vscode.postMessage({
    type: "messageType1",
    otherData: "Can be anything JSON serializable",
    abc: 123,
  });
}
