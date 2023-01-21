import * as vscode from "vscode";
import * as bridge from "./bridge";
import {
  showSuggestion,
  suggestionUpCommand,
  suggestionDownCommand,
  acceptSuggestionCommand,
  showAnswerInTextEditor,
} from "./textEditorDisplay";
const pty = require("node-pty");
const os = require("os");
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
    vscode.window.registerWebviewViewProvider(
      DebugPanelViewProvider.viewType,
      new DebugPanelViewProvider(context.extensionUri)
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
          webviewView
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
  webviewView: vscode.WebviewView | undefined = undefined
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
        if (webviewView) {
          webviewView.webview.postMessage({
            type: "answerQuestion",
            answer: resp.answer,
          });
        }
        showAnswerInTextEditor(resp.filename, resp.range, resp.answer);
      } catch (error: any) {
        if (webviewView) {
          webviewView.webview.postMessage({
            type: "answerQuestion",
            answer: error,
          });
        }
      }
    }
  );
}

function openCapturedTerminal(webview: vscode.Webview) {
  let workspaceFolders = vscode.workspace.workspaceFolders;
  if (!workspaceFolders) return;

  var isWindows = os.platform() === "win32";
  var shell = isWindows ? "powershell.exe" : "zsh";

  var ptyProcess = pty.spawn(shell, [], {
    name: "xterm-256color",
    cols: 100, // TODO: Get size of vscode terminal, and change with resize
    rows: 26,
    cwd: isWindows ? process.env.USERPROFILE : process.env.HOME,
    env: Object.assign({ TEST: "Environment vars work" }, process.env),
    useConpty: true,
  });

  const writeEmitter = new vscode.EventEmitter<string>();

  const tracebackStart = "Traceback (most recent call last):";
  const tracebackEnd = (buf: string): string | undefined => {
    let lines = buf.split("\n");
    for (let i = 0; i < lines.length; i++) {
      if (
        lines[i].startsWith("  File") &&
        i + 2 < lines.length &&
        lines[i + 2][0] != " "
      ) {
        return lines.slice(0, i + 3).join("\n");
      }
    }
    return undefined;
  };
  let tracebackBuffer = "";

  ptyProcess.onData((data: any) => {
    // Snoop for traceback
    let idx = data.indexOf(tracebackStart);
    if (idx >= 0) {
      tracebackBuffer = data.substr(idx);
    } else if (tracebackBuffer.length > 0) {
      tracebackBuffer += data;
    }
    // End of traceback, send to webview
    if (idx > 0 || tracebackBuffer.length > 0) {
      let wholeTraceback = tracebackEnd(tracebackBuffer);
      if (wholeTraceback) {
        webview.postMessage({ type: "traceback", traceback: wholeTraceback });
      }
    }
    // Pass data through to terminal
    // if (tracebackBuffer.length > 0) {
    //   writeEmitter.fire("----------------------------------------\r");
    // }
    writeEmitter.fire(data);
  });
  process.on("exit", () => ptyProcess.kill());

  ptyProcess.write("cd " + workspaceFolders[0].uri.fsPath + "\n\r");
  ptyProcess.write("clear\n\r");

  const newPty: vscode.Pseudoterminal = {
    onDidWrite: writeEmitter.event,
    open: () => {},
    close: () => {},
    handleInput: (data) => {
      ptyProcess.write(data);
    },
  };
  const terminal = vscode.window.createTerminal({
    name: "AutoDebug",
    pty: newPty,
  });
}
