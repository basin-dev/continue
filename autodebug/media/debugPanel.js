(function () {
  const vscode = acquireVsCodeApi();

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
  const generateUnitTestButton = document.querySelector(
    ".generateUnitTestButton"
  );
  const autoModeCheckbox = document.querySelector(".autoMode");

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

  function formatFileRange(filename, range) {
    return `${formatPathRelativeToWorkspace(filename)}, lines ${
      range.start.line + 1
    }-${range.end.line + 1}:`;
    // +1 because VSCode Ranges are 0-indexed
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
      element.getElementsByTagName("p")[0].textContent = formatFileRange(
        filename,
        range
      );
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
    p.textContent = formatFileRange(filename, range);

    let delButton = document.createElement("button");
    delButton.textContent = "x";
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
    generateUnitTestButton.disabled = false;
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

  // SAVE AND LOAD STATE
  let debugContext = {};

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
    return debugContext;
  }

  function loadState() {
    const oldState = vscode.getState();
    if (!oldState) {
      return;
    }
    if (oldState.debugContext) {
      debugContext = oldState.debugContext;
    }
    workspacePath = debugContext.workspacePath;

    if (debugContext.explanation) {
      bugDescription.value = debugContext.explanation;
      stacktrace.value = debugContext.stacktrace;
      fixSuggestion.innerHTML = debugContext.suggestion;
      selectedRanges = debugContext.codeSelections.map((obj) => {
        addMultiselectOption(obj.filename, obj.range, obj.code);
        return {
          filename: obj.filename,
          range: obj.range,
          code: obj.code,
          selected: true,
        };
      });
    }
  }

  function saveState() {
    let ctx = gatherDebugContext();
    vscode.setState({
      debugContext: ctx,
      workspacePath,
    });
  }
  loadState();
  setInterval(saveState, 1000);
  // SAVE AND LOAD STATE

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
        if (selectedRanges.length === 0) {
          findSuspiciousCode();
        }
        break;
      }
      case "highlightedCode": {
        workspacePath = message.workspacePath;
        addMultiselectOption(message.filename, message.range, message.code);
        break;
      }
      case "findSuspiciousCode": {
        clearMultiselectOptions();
        for (let codeLocation of message.codeLocations) {
          // It's serialized to be an array [startPos, endPos]
          let range = {
            start: {
              line: codeLocation.range[0].line,
              character: codeLocation.range[0].character,
            },
            end: {
              line: codeLocation.range[1].line,
              character: codeLocation.range[1].character,
            },
          };

          addMultiselectOption(codeLocation.filename, range, codeLocation.code);
        }
        if (autoModeCheckbox.checked === true) {
          makeEdit();
        }
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
        break;
      }
    }
    saveState();
  });

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

  function makeEdit() {
    makeEditLoader.hidden = false;
    makeEditButton.hidden = true;
    gatherDebugContext();
    vscode.postMessage({
      type: "makeEdit",
      debugContext,
    });
  }
  makeEditButton.addEventListener("click", () => {
    makeEdit();
  });

  generateUnitTestButton.addEventListener("click", () => {
    gatherDebugContext();
    vscode.postMessage({
      type: "generateUnitTest",
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
