import * as vscode from "vscode";

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
