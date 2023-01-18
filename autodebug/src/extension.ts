import * as vscode from "vscode";

export function activate(context: vscode.ExtensionContext) {
  const provider = new DebugViewProvider(context.extensionUri);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      DebugViewProvider.viewType,
      provider
    )
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("autodebug.enterBugDescription", () => {
      terminal?.sendText("echo 'Entering bug description'");
      provider.enterBugDescription();
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("autodebug.restartDebugging", () => {
      terminal?.sendText("echo 'Restarting debugging'");
      provider.restartDebugging();
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

    webviewView.webview.onDidReceiveMessage((data) => {
      switch (data.type) {
        case "startDebug": {
          // Make sure there is an open editor, because we want to debug "current file"
          const editor = vscode.window.activeTextEditor;
          if (!editor) {
            break;
          }
          const currentFile = editor.document.fileName;

          // Run our script to get fix suggestions and a stack trace
          const terminal = vscode.window.createTerminal({
            name: `AutoDebug Terminal`,
            // hideFromUser: true,
          } as any);
          terminal.show();
          terminal.sendText(
            "bash && cd ../.. && source env/bin/activate && python debug.py " +
              currentFile
          );

          // TODO: No way to read from terminal
          // terminal.onDidWriteData((data) => {
          // 	console.log(data);
          // });
          // Solution is to use a file to store the output of the script, but also need to wait for the file to be written to
          // Or have the script do all the work

          // Add breakpoints
          let breakpoints: vscode.SourceBreakpoint[] = [
            new vscode.SourceBreakpoint(
              new vscode.Location(
                vscode.Uri.file(currentFile),
                new vscode.Position(0, 0)
              )
            ),
          ];
          vscode.debug.addBreakpoints(breakpoints);

          // Start the debugger
          vscode.debug.startDebugging(undefined, {
            type: "node",
            request: "launch",
            name: "Launch Program",
            program: "${file}",
            console: "integratedTerminal",
            internalConsoleOptions: "neverOpen",
            outFiles: ["${workspaceFolder}/dist/**/*.js"],
            protocol: "inspector",
            skipFiles: ["<node_internals>/**"],
          });

          // When we reach a breakpoint, have GPT automatically suggest fixes

          // When we want to change the text of the current file:
          const document = editor.document;
          const selection = editor.selection;
          const text = document.getText(selection);
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
  }

  public enterBugDescription() {
    if (this._view) {
      this._view.show?.(true); // `show` is not implemented in 1.49 but is for 1.50 insiders
      this._view.webview.postMessage({ type: "enterBugDescription" });
    }
  }

  public restartDebugging() {
    if (this._view) {
      this._view.webview.postMessage({ type: "restartDebugging" });
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

    return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<script src="${scriptUri}"></script>
				<link href="${styleMainUri}" rel="stylesheet">

				<title>AutoDebug</title>
			</head>
			<body>
				<h1>Debug</h1>
				<input type="text" id="bugDescription" name="bugDescription" placeholder="Describe the bug you are facing" />
				<button id="startDebug">Debug Current File</button>
			</body>
			</html>`;
  }
}
