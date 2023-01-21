import * as vscode from "vscode";
import * as bridge from "./bridge";
import { setupDebugPanel } from "./debugPanel";
import DebugViewProvider from "./DebugViewProvider";
import {
  showSuggestion,
  suggestionUpCommand,
  suggestionDownCommand,
  acceptSuggestionCommand,
  showAnswerInTextEditor,
} from "./textEditorDisplay";

const path = require("path");

export function activate(context: vscode.ExtensionContext) {
  const provider = new DebugViewProvider(context.extensionUri);

  if (vscode.window.activeTextEditor) {
    showSuggestion(
      vscode.window.activeTextEditor,
      new vscode.Range(new vscode.Position(1, 0), new vscode.Position(2, 0)),
      `    abc = [1, 2, 3]
    return abc[0]
`
    )
      .then((_) =>
        showSuggestion(
          vscode.window.activeTextEditor!,
          new vscode.Range(
            new vscode.Position(7, 0),
            new vscode.Position(8, 0)
          ),
          `    abc = [1, 2, 3]
    return abc[0]
`
        )
      )
      .then((_) =>
        showSuggestion(
          vscode.window.activeTextEditor!,
          new vscode.Range(
            new vscode.Position(13, 0),
            new vscode.Position(14, 0)
          ),
          `    abc = [1, 2, 3]
    return abc[0]
`
        )
      );
  }

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      DebugViewProvider.viewType,
      provider
    )
  );

  context.subscriptions.push(
    vscode.commands.registerTextEditorCommand(
      "autodebug.writeDocstring",
      async (editor, _) => {
        vscode.window.withProgress(
          {
            location: vscode.ProgressLocation.Notification,
            title: "AutoDebug",
            cancellable: false,
          },
          async (progress, token) => {
            progress.report({
              message: "Writing docstring...",
            });

            const { lineno, docstring } =
              await bridge.writeDocstringForFunction(
                editor.document.fileName,
                editor.selection.active
              );
            // Can't use the edit given above after an async call
            editor.edit((edit) => {
              edit.insert(new vscode.Position(lineno, 0), docstring);
            });
          }
        );
      }
    )
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(
      "autodebug.askQuestion",
      (data: any, webviewView: vscode.WebviewView) => {
        if (!vscode.workspace.workspaceFolders) {
          return;
        }

        answerQuestion(
          data.question,
          vscode.workspace.workspaceFolders[0].uri.fsPath,
          webviewView.webview
        );
      }
    )
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("autodebug.askQuestionFromInput", () => {
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
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(
      "autodebug.suggestionDown",
      suggestionDownCommand
    )
  );
  context.subscriptions.push(
    vscode.commands.registerCommand(
      "autodebug.suggestionUp",
      suggestionUpCommand
    )
  );

  context.subscriptions.push(
    vscode.commands.registerCommand(
      "autodebug.acceptSuggestion",
      acceptSuggestionCommand
    )
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("autodebug.openDebugPanel", () => {
      const panel = vscode.window.createWebviewPanel(
        "autodebug.debugPanelView",
        "AutoDebug",
        vscode.ViewColumn.Beside,
        {}
      );

      // And set its HTML content
      panel.webview.html = setupDebugPanel(panel.webview);
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("autodebug.openCapturedTerminal", () => {
      // Happens in webviewview resolution function
      // openCapturedTerminal();
    })
  );

  let terminal: vscode.Terminal | undefined;
  context.subscriptions.push(
    vscode.commands.registerCommand("autodebug.createTerminal", () => {
      terminal = vscode.window.createTerminal({
        name: `AutoDebug Terminal`,
        // hideFromUser: true,
      } as any);
      terminal.show();
      terminal.sendText("echo 'Hello World'");
    })
  );
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
