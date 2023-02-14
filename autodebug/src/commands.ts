import * as vscode from "vscode";
import {
  acceptSuggestionCommand,
  rejectSuggestionCommand,
  decorationManager,
  showAnswerInTextEditor,
  showGutterSpinner,
  suggestionDownCommand,
  suggestionUpCommand,
} from "./textEditorDisplay";
import { writeUnitTestCommand } from "./unitTests";
import * as bridge from "./bridge";
import { debugPanelWebview, setupDebugPanel } from "./debugPanel";
import { openCapturedTerminal } from "./terminalEmulator";
import { getRightViewColumn } from "./vscodeUtils";
import { findSuspiciousCode, runPythonScript } from "./bridge";
import { sendTelemetryEvent, TelemetryEvent } from "./telemetry";
import { parseFirstStacktrace } from "./languages/python";

// Copy everything over from extension.ts
const commandsMap: { [command: string]: (...args: any) => any } = {
  "autodebug.askQuestion": (data: any, webviewView: vscode.WebviewView) => {
    if (!vscode.workspace.workspaceFolders) {
      return;
    }

    answerQuestion(
      data.question,
      vscode.workspace.workspaceFolders[0].uri.fsPath,
      webviewView.webview
    );
  },
  "autodebug.askQuestionFromInput": () => {
    vscode.window
      .showInputBox({ placeHolder: "Ask away!" })
      .then((question) => {
        if (!question || !vscode.workspace.workspaceFolders) {
          return;
        }

        sendTelemetryEvent(TelemetryEvent.UniversalPromptQuery, {
          query: question,
        });

        answerQuestion(
          question,
          vscode.workspace.workspaceFolders[0].uri.fsPath
        );
      });
  },
  "autodebug.suggestionDown": suggestionDownCommand,
  "autodebug.suggestionUp": suggestionUpCommand,
  "autodebug.acceptSuggestion": acceptSuggestionCommand,
  "autodebug.rejectSuggestion": rejectSuggestionCommand,
  "autodebug.openDebugPanel": () => {
    let column = getRightViewColumn();
    const panel = vscode.window.createWebviewPanel(
      "autodebug.debugPanelView",
      "AutoDebug",
      column,
      {
        enableScripts: true,
      }
    );

    // And set its HTML content
    panel.webview.html = setupDebugPanel(panel);
  },
  "autodebug.openCapturedTerminal": () => {
    // Happens in webview resolution function
    openCapturedTerminal();
  },
  "autodebug.findSuspiciousCode": async (debugContext: bridge.DebugContext) => {
    vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "Finding suspicious code",
        cancellable: false,
      },
      async (progress, token) => {
        let suspiciousCode = await findSuspiciousCode(debugContext);
        debugPanelWebview?.postMessage({
          type: "findSuspiciousCode",
          codeLocations: suspiciousCode,
        });
      }
    );
  },
  "autodebug.debugTest": async (fileAndFunctionSpecifier: string) => {
    sendTelemetryEvent(TelemetryEvent.AutoDebugThisTest)
    let { stdout } = await runPythonScript("run_unit_test.py", [
      fileAndFunctionSpecifier,
    ]);
    let stacktrace = parseFirstStacktrace(stdout);
    if (!stacktrace) {
      vscode.window.showInformationMessage("The test passes!");
      return;
    }
    vscode.commands.executeCommand("autodebug.openDebugPanel").then(() => {
      debugPanelWebview?.postMessage({
        type: "traceback",
        traceback: stacktrace,
      });
    });
  },
};

const textEditorCommandsMap: { [command: string]: (...args: any) => {} } = {
  "autodebug.writeUnitTest": writeUnitTestCommand,
  "autodebug.writeDocstring": async (editor: vscode.TextEditor, _) => {
    sendTelemetryEvent(TelemetryEvent.GenerateDocstring)
    let gutterSpinnerKey = showGutterSpinner(
      editor,
      editor.selection.active.line
    );

    const { lineno, docstring } = await bridge.writeDocstringForFunction(
      editor.document.fileName,
      editor.selection.active
    );
    // Can't use the edit given above after an async call
    editor.edit((edit) => {
      edit.insert(new vscode.Position(lineno, 0), docstring);
      decorationManager.deleteDecoration(gutterSpinnerKey);
    });
  },
};

export function registerAllCommands(context: vscode.ExtensionContext) {
  for (const [command, callback] of Object.entries(commandsMap)) {
    context.subscriptions.push(
      vscode.commands.registerCommand(command, callback)
    );
  }

  for (const [command, callback] of Object.entries(textEditorCommandsMap)) {
    context.subscriptions.push(
      vscode.commands.registerTextEditorCommand(command, callback)
    );
  }
}

async function answerQuestion(
  question: string,
  workspacePath: string,
  webview: vscode.Webview | undefined = undefined
) {
  vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: "Anwering question...",
      cancellable: false,
    },
    async (progress, token) => {
      try {
        let resp = await bridge.askQuestion(question, workspacePath);
        // Send the answer back to the webview
        if (webview) {
          webview.postMessage({
            type: "answerQuestion",
            answer: resp.answer,
          });
        }
        showAnswerInTextEditor(resp.filename, resp.range, resp.answer);
      } catch (error: any) {
        if (webview) {
          webview.postMessage({
            type: "answerQuestion",
            answer: error,
          });
        }
      }
    }
  );
}

// async function suggestFixForAllWorkspaceProblems() {
// Something like this, just figure out the loops for diagnostics vs problems
// let problems = vscode.languages.getDiagnostics();
// let codeSuggestions = await Promise.all(problems.map((problem) => {
//   return bridge.suggestFixForProblem(problem[0].fsPath, problem[1]);
// }));
// for (const [uri, diagnostics] of problems) {
//   for (let i = 0; i < diagnostics.length; i++) {
//     let diagnostic = diagnostics[i];
//     let suggestedCode = codeSuggestions[i];
//     // If you're going to do this for a bunch of files at once, it will show the unsaved icon in the tab
//     // BUT it would be better to have a single window to review all edits
//     showSuggestion(uri.fsPath, diagnostic.range, suggestedCode)
//   }
// }
// }
