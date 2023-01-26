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
  const makeEditLoader = document.querySelector(".makeEditLoader");
  const multiselectContainer = document.querySelector(".multiselectContainer");

  let selectedRanges = []; // Elements are { filename, range, code }
  let canUpdateLast = true;

  let workspacePath = undefined;
  function formatPathRelativeToWorkspace(path) {
    if (!workspacePath) return path;
    if (path.startsWith(workspacePath)) {
      return path.substring(workspacePath.length + 1);
    } else {
      return path;
    }
  }

  function addMultiselectOption(filename, range, code) {
    // First, we check if this is just an update to the last range
    if (
      canUpdateLast &&
      selectedRanges.length > 0 &&
      filename === selectedRanges[selectedRanges.length - 1].filename
    ) {
      // Update the last element and its element
      selectedRanges[selectedRanges.length - 1].range = range;
      selectedRanges[selectedRanges.length - 1].code = code;
      let element = selectedRanges[selectedRanges.length - 1].element;
      element.getElementsByTagName(
        "p"
      )[0].textContent = `${formatPathRelativeToWorkspace(filename)}, lines ${
        range.start.line
      }-${range.end.line}:`;
      element.getElementsByTagName("pre")[0].textContent = code;
      console.log("Updated", element.getElementsByTagName("pre").length);
      return;
    }

    canUpdateLast = true;

    let div = document.createElement("div");
    div.className = "multiselectOption";

    let pre = document.createElement("pre");
    pre.textContent = code;

    let topDiv = document.createElement("div");
    topDiv.className = "multiselectOptionTopDiv";

    let p = document.createElement("p");
    p.style.margin = "4px";
    p.textContent = `${formatPathRelativeToWorkspace(filename)}, lines ${
      range.start.line
    }-${range.end.line}:`;

    let delButton = document.createElement("button");
    delButton.textContent = "X";
    delButton.className = "delSelectedRangeButton";
    delButton.addEventListener("click", () => {
      multiselectContainer.removeChild(div);
      selectedRanges = selectedRanges.filter((obj) => obj.element !== div);
      if (selectedRanges.length < 1) {
        clearMultiselectOptions();
      }
    });

    topDiv.appendChild(p);
    topDiv.appendChild(delButton);
    div.appendChild(topDiv);
    div.appendChild(pre);

    let obj = { filename, range, code, element: div, selected: true };
    div.style.border = "1px solid orange";
    selectedRanges.push(obj);

    div.addEventListener("click", () => {
      obj.selected = !obj.selected;
      obj.element.style.border = obj.selected
        ? "1px solid orange"
        : "1px solid gray";
    });
    multiselectContainer.appendChild(div);

    // If this is the first added option, we should display an "add another" button
    if (selectedRanges.length >= 1) {
      document.querySelector(".addAnotherButton").disabled = false;
      makeEditButton.disabled = false;
    }
  }

  function clearMultiselectOptions() {
    // Remove everything
    while (multiselectContainer.firstChild) {
      multiselectContainer.removeChild(multiselectContainer.firstChild);
    }
    // Then add the default contents
    let p = document.createElement("p");
    p.textContent = "Highlight relevant code in the editor:";
    multiselectContainer.appendChild(p);

    let buttonDiv = document.createElement("div");
    buttonDiv.className = "multiselectButtonsDiv";

    let susButton = document.createElement("button");
    susButton.textContent = "Automatically Find Suspicious Code";
    susButton.className = "susButton";
    susButton.addEventListener("click", findSuspiciousCode);
    multiselectContainer.appendChild(susButton);

    let addAnotherButton = document.createElement("button");
    addAnotherButton.textContent = "Add another code range in same file";
    addAnotherButton.className = "addAnotherButton";
    addAnotherButton.disabled = true;
    addAnotherButton.addEventListener("click", () => {
      canUpdateLast = false;
    });
    buttonDiv.appendChild(susButton);
    buttonDiv.appendChild(addAnotherButton);
    multiselectContainer.appendChild(buttonDiv);

    makeEditButton.disabled = true;
  }

  clearMultiselectOptions();

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
        break;
      }
      case "highlightedCode": {
        workspacePath = message.workspacePath;
        addMultiselectOption(message.filename, message.range, message.code);
        break;
      }
      case "findSuspiciousCode": {
        fixSuggestion.hidden = false;
        fixSuggestion.textContent = message.suspiciousCode;
        break;
      }
      case "listTenThings": {
        fixSuggestion.textContent = message.tenThings;
        break;
      }
      case "suggestFix": {
        fixSuggestion.textContent = message.fixSuggestion;
        break;
      }
      case "makeEdit": {
        // Edit is done
        makeEditLoader.hidden = true;
        makeEditButton.hidden = false;
      }
    }
  });

  function gatherDebugContext() {
    debugContext.explanation = bugDescription.value;
    debugContext.stacktrace = stacktrace.value;
    debugContext.suggestion = fixSuggestion.innerHTML;
    debugContext.codeSelections = selectedRanges
      .filter((obj) => obj.selected)
      .map((obj) => {
        return {
          filename: obj.filename,
          range: obj.range,
          code: obj.code,
        };
      });
  }

  function listTenThings() {
    gatherDebugContext();
    fixSuggestion.hidden = false;
    fixSuggestion.innerHTML = `<div class="loader" ></div>`;
    vscode.postMessage({
      type: "listTenThings",
      debugContext,
    });
  }
  listTenThingsButton.addEventListener("click", listTenThings);

  function suggestFix() {
    gatherDebugContext();
    fixSuggestion.hidden = false;
    fixSuggestion.innerHTML = `<div class="loader" ></div>`;
    vscode.postMessage({
      type: "suggestFix",
      debugContext,
    });
  }
  suggestFixButton.addEventListener("click", suggestFix);

  makeEditButton.addEventListener("click", () => {
    makeEditLoader.hidden = false;
    makeEditButton.hidden = true;
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
