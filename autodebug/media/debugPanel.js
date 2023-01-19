console.log("Debug Panel Loaded");

// Handle messages sent from the extension to the webview
window.addEventListener("message", (event) => {
  const message = event.data; // The json data that the extension sent
  switch (message.type) {
    case "messageType": {
      // Do something
      // sendMessageBack();
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
