(function () {
  const vscode = acquireVsCodeApi();

  const relevantVarsSelect = document.querySelector(".relevantVars");
  const highlightedCode = document.querySelector(".highlightedCode");
  const bugDescription = document.querySelector(".bugDescription");
  const traceback = document.querySelector(".traceback");

  // Find suspicious code when traceback textarea value is changed
  traceback.addEventListener("input", () => {
    updateState({ debugContext: gatherDebugContext() });
    findSuspiciousCode();
  });

  const fixSuggestion = document.querySelector(".fixSuggestion");
  const explainCodeButton = document.querySelector(".explainCodeButton");
  const listTenThingsButton = document.querySelector(".listTenThingsButton");
  const makeEditButton = document.querySelector(".makeEditButton");
  const makeEditLoader = document.querySelector(".makeEditLoader");
  const multiselectContainer = document.querySelector(".multiselectContainer");
  const additionalContextTextarea = document.querySelector(
    ".additionalContextTextarea"
  );
  const generateUnitTestButton = document.querySelector(
    ".generateUnitTestButton"
  );
  const tabBar = document.querySelector(".tabBar");
  const tabs = document.getElementsByClassName("tab");

  let selectedRanges = []; // Elements are { filename, range, code }
  let canUpdateLast = true;
  let highlightLocked = true;

  function formatPathRelativeToWorkspace(path) {
    let workspacePath = vscode.getState()?.workspacePath;
    if (!workspacePath) return path;
    if (path.startsWith(workspacePath)) {
      return path.substring(workspacePath.length + 1);
    } else {
      return path;
    }
  }

  function formatFileRange(filename, range) {
    return `${formatPathRelativeToWorkspace(filename)} (lines ${
      range.start.line + 1
    }-${range.end.line + 1})`;
    // +1 because VSCode Ranges are 0-indexed
  }

  const filenameToLanguage = {
    py: "python",
    js: "javascript",
    ts: "typescript",
    html: "html",
    css: "css",
    java: "java",
    c: "c",
    cpp: "cpp",
    cs: "csharp",
    go: "go",
    rb: "ruby",
    rs: "rust",
    swift: "swift",
    php: "php",
    scala: "scala",
    kt: "kotlin",
    dart: "dart",
    hs: "haskell",
    lua: "lua",
    pl: "perl",
    r: "r",
    sql: "sql",
    vb: "vb",
    xml: "xml",
    yaml: "yaml",
  };

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
      let codeElement = element
        .getElementsByTagName("pre")[0]
        .getElementsByTagName("code")[0];
      codeElement.textContent = code;

      hljs.highlightElement(codeElement);

      return;
    }

    canUpdateLast = true;

    let div = document.createElement("div");
    div.className = "multiselectOption multiselectOptionSelected";

    let pre = document.createElement("pre");
    // Code element inside because required for highlight.js
    let codeElement = document.createElement("code");
    let ext = filename.split(".").pop();
    if (ext in filenameToLanguage) {
      codeElement.className = "language-" + filenameToLanguage[ext];
    }
    codeElement.textContent = code;
    pre.appendChild(codeElement);

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
    selectedRanges.push(obj);

    div.addEventListener("click", () => {
      obj.selected = !obj.selected;
      if (obj.selected) {
        div.classList.add("multiselectOptionSelected");
      } else {
        div.classList.remove("multiselectOptionSelected");
      }
    });
    multiselectContainer.appendChild(div);

    hljs.highlightElement(codeElement);

    // If this is the first added option, we should display an "add another" button
    if (selectedRanges.length >= 1) {
      makeEditButton.disabled = false;
    }
    generateUnitTestButton.disabled = false;
  }

  const lockClosedIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="20px" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
</svg>
`;
  const lockOpenIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="20px" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
<path stroke-linecap="round" stroke-linejoin="round" d="M13.5 10.5V6.75a4.5 4.5 0 119 0v3.75M3.75 21.75h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H3.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
</svg>
`;

  function clearMultiselectOptions() {
    // Remove everything
    while (multiselectContainer.firstChild) {
      multiselectContainer.removeChild(multiselectContainer.firstChild);
    }
    // Then add the default contents
    let p = document.createElement("p");
    p.textContent = "Highlight relevant code in the editor:";
    multiselectContainer.appendChild(p);

    let addAnotherButton = document.createElement("button");
    addAnotherButton.style.display = "grid";
    addAnotherButton.style.justifyContent = "center";
    addAnotherButton.style.alignItems = "center";
    addAnotherButton.style.gridTemplateColumns = "30px 1fr";

    addAnotherButton.innerHTML = lockClosedIcon + "Enable Highlight";
    addAnotherButton.className = "addAnotherButton";
    addAnotherButton.addEventListener("click", () => {
      if (highlightLocked) {
        addAnotherButton.innerHTML = lockOpenIcon + "Disable Highlight";
      } else {
        addAnotherButton.innerHTML = lockClosedIcon + "Enable Highlight";
      }
      canUpdateLast = false;
      highlightLocked = !highlightLocked;
    });
    multiselectContainer.appendChild(addAnotherButton);

    makeEditButton.disabled = true;
  }

  clearMultiselectOptions();

  function gatherDebugContext() {
    let debugContext = {};
    debugContext.description = bugDescription.value;
    debugContext.traceback = traceback.value;
    debugContext.suggestion = fixSuggestion.innerHTML;
    debugContext.additionalContext = additionalContextTextarea.value;
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
    let state = vscode.getState();
    if (!state) {
      return;
    }
    if (state.debugContext) {
      bugDescription.value = state.debugContext.description;
      traceback.value = state.debugContext.traceback;
      fixSuggestion.innerHTML = state.debugContext.suggestion;
      additionalContextTextarea.value = state.debugContext.additionalContext;
      for (let codeSelection of state.debugContext.codeSelections) {
        canUpdateLast = false;
        addMultiselectOption(
          codeSelection.filename,
          codeSelection.range,
          codeSelection.code
        );
      }
      selectedRanges = state.debugContext.codeSelections.map((obj) => {
        return {
          filename: obj.filename,
          range: obj.range,
          code: obj.code,
          selected: true,
        };
      });
      setTab(state.currentTab || 0);
    }
  }

  function updateState(newState) {
    let oldState = vscode.getState() || {};
    vscode.setState(Object.assign(oldState, newState));
  }

  loadState();
  setInterval(() => {
    let debugContext = gatherDebugContext();
    updateState({ debugContext });
  }, 500);

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
        traceback.value = message.traceback;
        if (selectedRanges.length === 0) {
          findSuspiciousCode();
        }
        break;
      }
      case "highlightedCode": {
        updateState({ workspacePath: message.workspacePath });
        if (!highlightLocked) {
          addMultiselectOption(message.filename, message.range, message.code);
        }
        break;
      }
      case "findSuspiciousCode": {
        clearMultiselectOptions();
        for (let codeLocation of message.codeLocations) {
          canUpdateLast = false;
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
        canUpdateLast = true;
        listTenThings();
        break;
      }
      case "listTenThings": {
        fixSuggestion.textContent = message.tenThings;
        break;
      }
      case "explainCode": {
        fixSuggestion.textContent = message.completion;
        break;
      }
      case "suggestFix": {
        fixSuggestion.textContent = message.fixSuggestion;
        break;
      }
      case "makeEdit": {
        // Edit is done
        makeEditLoader.hidden = true;
        break;
      }
    }
    updateState({ debugContext: gatherDebugContext() });
  });

  function listTenThings() {
    let debugContext = gatherDebugContext();
    fixSuggestion.hidden = false;
    fixSuggestion.innerHTML = `<div class="loader" ></div>`;
    vscode.postMessage({
      type: "listTenThings",
      debugContext,
    });
  }
  listTenThingsButton.addEventListener("click", listTenThings);

  function explainCode() {
    let debugContext = gatherDebugContext();
    fixSuggestion.hidden = false;
    fixSuggestion.innerHTML = `<div class="loader" ></div>`;
    vscode.postMessage({
      type: "explainCode",
      debugContext,
    });
  }
  explainCodeButton.addEventListener("click", explainCode);

  function makeEdit() {
    makeEditLoader.hidden = false;
    let debugContext = gatherDebugContext();
    vscode.postMessage({
      type: "makeEdit",
      debugContext,
    });
  }
  makeEditButton.addEventListener("click", () => {
    makeEdit();
  });

  generateUnitTestButton.addEventListener("click", () => {
    let debugContext = gatherDebugContext();
    vscode.postMessage({
      type: "generateUnitTest",
      debugContext,
    });
  });

  function findSuspiciousCode() {
    let debugContext = gatherDebugContext();
    vscode.postMessage({
      type: "findSuspiciousCode",
      debugContext,
    });
  }
})();
