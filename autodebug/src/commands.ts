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
import { setupDebugPanel } from "./debugPanel";
import { openCapturedTerminal } from "./terminalEmulator";

// These commands are those just being used for the sake of the universal command prompt
const unregisteredCommands: {
  [command: string]: (...args: any) => any;
} = {
  "autodebug.inputTerminalCommand": (params: { command: string }) => {
    // Some simple safeguards
    if (params.command.includes("rm") || params.command.includes("sudo")) {
      return;
    }
    vscode.window.activeTerminal?.sendText(params.command + " \\");
  },
};

// COpy everything over from extension.ts
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

        answerQuestion(
          question,
          vscode.workspace.workspaceFolders[0].uri.fsPath
        );
      });
  },
  "autodebug.universalCommand": () => {
    vscode.window
      .showInputBox({
        placeHolder:
          "This is the universal command prompt. It can do anything within VSCode. Ask away!",
      })
      .then(async (request) => {
        if (!request || !vscode.workspace.workspaceFolders) {
          return;
        }

        vscode.window.withProgress(
          {
            location: vscode.ProgressLocation.Notification,
            title: "Processing request...",
            cancellable: false,
          },
          async () => {
            let { action, params } = await bridge.universalPrompt(request);
            console.log("Action: ", action);
            console.log("Params: ", params);
            if (unregisteredCommands.hasOwnProperty(action)) {
              unregisteredCommands[action](params);
            } else {
              vscode.commands.executeCommand(action, params);
            }
          }
        );
      });
  },
  "autodebug.suggestionDown": suggestionDownCommand,
  "autodebug.suggestionUp": suggestionUpCommand,
  "autodebug.acceptSuggestion": acceptSuggestionCommand,
  "autodebug.rejectSuggestion": rejectSuggestionCommand,
  "autodebug.openDebugPanel": () => {
    const panel = vscode.window.createWebviewPanel(
      "autodebug.debugPanelView",
      "AutoDebug",
      vscode.ViewColumn.Beside,
      {
        enableScripts: true,
      }
    );

    // And set its HTML content
    panel.webview.html = setupDebugPanel(panel.webview);
  },
  "autodebug.openCapturedTerminal": () => {
    // Happens in webview resolution function
    openCapturedTerminal();
  },
};

const textEditorCommandsMap: { [command: string]: (...args: any) => {} } = {
  "autodebug.writeUnitTest": writeUnitTestCommand,
  "autodebug.writeDocstring": async (editor: vscode.TextEditor, _) => {
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
