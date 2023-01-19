import * as vscode from "vscode";
import * as bridge from "./bridge";
const pty = require("node-pty");
const os = require("os");

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

export function activate(context: vscode.ExtensionContext) {
  const provider = new DebugViewProvider(context.extensionUri);

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

function showAnswerInTextEditor(
  filename: string,
  range: vscode.Range,
  answer: string
) {
  vscode.workspace.openTextDocument(vscode.Uri.file(filename)).then((doc) => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      return;
    }

    // Open file, reveal range, show decoration
    vscode.window.showTextDocument(doc).then((new_editor) => {
      new_editor.revealRange(
        new vscode.Range(range.end, range.end),
        vscode.TextEditorRevealType.InCenter
      );

      let decorationType = vscode.window.createTextEditorDecorationType({
        after: {
          contentText: answer + "\n",
          color: "rgb(0, 255, 0, 0.8)",
        },
        backgroundColor: "rgb(0, 255, 0, 0.2)",
      });
      new_editor.setDecorations(decorationType, [range]);
      vscode.window.showInformationMessage("Answer found!");

      // Remove decoration when user moves cursor
      vscode.window.onDidChangeTextEditorSelection((e) => {
        if (
          e.textEditor === new_editor &&
          e.selections[0].active.line !== range.end.line
        ) {
          new_editor.setDecorations(decorationType, []);
        }
      });
    });
  });
}

class DebugViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "autodebug.debugView";

  private _view?: vscode.WebviewView;

  constructor(private readonly _extensionUri: vscode.Uri) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      // Allow scripts in the webview
      enableScripts: true,

      localResourceRoots: [this._extensionUri],
    };

    webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

    webviewView.webview.onDidReceiveMessage(async (data) => {
      switch (data.type) {
        case "askQuestion": {
          vscode.commands.executeCommand(
            "autodebug.askQuestion",
            data,
            webviewView
          );
          break;
        }
        case "startDebug": {
          // Make sure there is an open editor, because we want to debug "current file"
          const editor = vscode.window.activeTextEditor;
          if (!editor) {
            break;
          }
          vscode.window.withProgress(
            {
              location: vscode.ProgressLocation.Notification,
              title: "Starting debugging",
              cancellable: false,
            },
            async (progress, token) => {
              let ctx = await bridge.getSuggestion({
                filename: editor.selection.isEmpty
                  ? undefined
                  : editor.document.fileName,
                range: editor.selection.isEmpty ? undefined : editor.selection,
                stacktrace: data.stackTrace,
                explanation: data.explanation,
              });
              vscode.window.showInformationMessage(
                ctx.suggestion || "No suggestion found"
              );

              if (!editor.selection.isEmpty) {
                // Replace the selected text with the suggestion
                editor.edit((editBuilder) => {
                  editBuilder.replace(editor.selection, ctx.suggestion || "");
                });
              }
            }
          );

          //   const currentFile = editor.document.fileName;

          // Run our script to get fix suggestions and a stack trace
          //   const terminal = vscode.window.createTerminal({
          //     name: `AutoDebug Terminal`,
          //     // hideFromUser: true,
          //   } as any);
          //   terminal.show();
          //   terminal.sendText(
          //     "bash && cd ../.. && source env/bin/activate && python debug.py " +
          //       currentFile
          //   );

          // TODO: No way to read from terminal
          // terminal.onDidWriteData((data) => {
          // 	console.log(data);
          // });
          // Solution is to use a file to store the output of the script, but also need to wait for the file to be written to
          // Or have the script do all the work

          // Add breakpoints
          //   let breakpoints: vscode.SourceBreakpoint[] = [
          //     new vscode.SourceBreakpoint(
          //       new vscode.Location(
          //         vscode.Uri.file(currentFile),
          //         new vscode.Position(0, 0)
          //       )
          //     ),
          //   ];
          //   vscode.debug.addBreakpoints(breakpoints);

          // Start the debugger
          //   vscode.debug.startDebugging(undefined, {
          //     type: "node",
          //     request: "launch",
          //     name: "Launch Program",
          //     program: "${file}",
          //     console: "integratedTerminal",
          //     internalConsoleOptions: "neverOpen",
          //     outFiles: ["${workspaceFolder}/dist/**/*.js"],
          //     protocol: "inspector",
          //     skipFiles: ["<node_internals>/**"],
          //   });

          // When we reach a breakpoint, have GPT automatically suggest fixes

          // When we want to change the text of the current file:
          //   const document = editor.document;
          //   const selection = editor.selection;
          //   const text = document.getText(selection);
          //   editor.edit((editBuilder) => {
          //     editBuilder.replace(
          //       selection,
          //       `
          // 		// ${data.bugDescription}
          // 		${text}
          // 		`
          //     );
          //   });

          break;
        }
      }
    });

    openCapturedTerminal(webviewView.webview);
  }

  public enterBugDescription() {
    if (this._view) {
      this._view.show?.(true); // `show` is not implemented in 1.49 but is for 1.50 insiders
      this._view.webview.postMessage({ type: "enterBugDescription" });
    }
  }

  private _getHtmlForWebview(webview: vscode.Webview) {
    // Get the local path to main script run in the webview, then convert it to a uri we can use in the webview.
    const scriptUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "media", "main.js")
    );

    const styleMainUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "media", "main.css")
    );

    const nonce = getNonce();

    return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<link href="${styleMainUri}" rel="stylesheet">
				
				<title>AutoDebug</title>
			</head>
			<body>
				
				<h2>Debug</h2>
				<textarea id="stackTrace" name="stackTrace" class="stackTrace" placeholder="Enter a stack trace" cols="80"></textarea>
				<input type="text" id="explanation" name="explanation" class="explanation" placeholder="Describe the problem"/>
        <p>Highlight text in the editor to suggest a fix in that range. Otherwise, we will guess where the problem is coming from.</p>
				<button id="startDebug" class="startDebug">Suggest Fix</button>

				<hr></hr>
				<h2>Ask a Question</h2>
				<input type="text" id="question" name="question" class="question" placeholder="Ask a question about your codebase" value="Where is binary search?" />
				<button id="ask" class="ask-button">Ask</button>

				<p>Answer:</p>
				<div id="answer" class="answer"></div>
				
				<script nonce="${nonce}" src="${scriptUri}"></script>
			</body>
			</html>`;
  }
}

function getNonce() {
  let text = "";
  const possible =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (let i = 0; i < 32; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}

class DebugPanelViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "autodebug.debugPanelView";

  private _view?: vscode.WebviewView;

  constructor(private readonly _extensionUri: vscode.Uri) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      // Allow scripts in the webview
      enableScripts: true,
      localResourceRoots: [this._extensionUri],
    };

    webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

    webviewView.webview.onDidReceiveMessage(async (data) => {
      switch (data.type) {
        case "messageType1": {
          vscode.commands.executeCommand(
            "autodebug.askQuestion",
            data,
            webviewView
          );
          break;
        }
        case "messageType2": {
          break;
        }
      }
    });
  }

  public sendSomeMessageToJS() {
    // the postMessage function lets you send a message to your .js script
    // See the .js script for how to send recieve and send back
    if (this._view) {
      this._view.show?.(true); // `show` is not implemented in 1.49 but is for 1.50 insiders
      this._view.webview.postMessage({ type: "messageType" });
    }
  }

  private _getHtmlForWebview(webview: vscode.Webview) {
    // Get the local path to main script run in the webview, then convert it to a uri we can use in the webview.
    const scriptUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "media", "debugPanel.js")
    );

    const styleMainUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "media", "main.css")
    );

    const nonce = getNonce();

    return `<!DOCTYPE html>
			  <html lang="en">
			  <head>
				  <meta charset="UTF-8">
				  <meta name="viewport" content="width=device-width, initial-scale=1.0">
				  <link href="${styleMainUri}" rel="stylesheet">
				  
				  <title>AutoDebug</title>
			  </head>
			  <body>
				  <h1>Debug Panel!!!</h1>

				  <script nonce="${nonce}" src="${scriptUri}"></script>
			  </body>
			  </html>`;
  }
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
