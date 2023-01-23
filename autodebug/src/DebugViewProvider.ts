import * as vscode from "vscode";
import * as bridge from "./bridge";
import { showSuggestion } from "./textEditorDisplay";
import { getNonce } from "./vscodeUtils";
const pty = require("node-pty");
const os = require("os");

export default class DebugViewProvider implements vscode.WebviewViewProvider {
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
                showSuggestion(
                  editor.document.fileName,
                  new vscode.Range(
                    editor.selection.start,
                    editor.selection.end
                  ),
                  ctx.suggestion || ""
                );
                // // Replace the selected text with the suggestion
                // editor.edit((editBuilder) => {
                //   editBuilder.replace(editor.selection, ctx.suggestion || "");
                // });
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

    // openCapturedTerminal(webviewView.webview);
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
