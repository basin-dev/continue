import { ShowSuggestionRequest } from "../schema/ShowSuggestionRequest";
import { FileEdit, RangeInFile } from "./client";
import * as vscode from "vscode";
import { setupDebugPanel } from "./debugPanel";
import { getRightViewColumn } from "./util/vscode";
const util = require("util");
const exec = util.promisify(require("child_process").exec);
const WebSocket = require("ws");

class IdeProtocolClient {
  private readonly _ws: WebSocket;
  private readonly _context: vscode.ExtensionContext;

  constructor(serverUrl: string, context: vscode.ExtensionContext) {
    this._context = context;
    this._ws = new WebSocket(serverUrl);
    // Setup listeners for any file changes in open editors
    vscode.workspace.onDidChangeTextDocument((event) => {});
  }

  async isConnected() {
    // On open, return a promise
    if (this._ws.readyState === WebSocket.OPEN) {
      return;
    }
    return new Promise((resolve, reject) => {
      this._ws.onopen = () => {
        resolve(null);
      };
    });
  }

  async startCore() {
    var { stdout, stderr } = await exec(
      "cd /Users/natesesti/Desktop/continue/continue && poetry shell"
    );
    if (stderr) {
      throw new Error(stderr);
    }
    var { stdout, stderr } = await exec(
      "cd .. && uvicorn continue.src.server.main:app --reload --reload-dir continue"
    );
    if (stderr) {
      throw new Error(stderr);
    }
    var { stdout, stderr } = await exec("python3 -m continue.src.libs.ide");
    if (stderr) {
      throw new Error(stderr);
    }
  }

  async send(messageType: string, data: object) {
    await this.isConnected();
    this._ws.send(JSON.stringify({ messageType, ...data }));
  }

  async receiveMessage(messageType: string): Promise<any> {
    await this.isConnected();
    return await new Promise((resolve, reject) => {
      if (!this._ws) {
        reject("Not connected to websocket");
      }
      this._ws!.onmessage = (event: any) => {
        let message = JSON.parse(event.data);
        if (message.messageType === messageType) {
          resolve(message);
        }
      };
    });
  }

  async sendAndReceive(message: any, messageType: string): Promise<any> {
    console.log("SENDING");
    let resp = await this.send(messageType, message);
    console.log("SENT");
    return await this.receiveMessage(messageType);
  }

  // ------------------------------------ //
  // On message handlers

  showSuggestion(edit: FileEdit) {
    // showSuggestion
  }

  openFile(filepath: string) {
    // TODO
  }

  // ------------------------------------ //
  // Initiate Request

  closeNotebook() {
    // TODO: And close the debug panel webview
    this._ws.close();
  }

  async openNotebook() {
    let resp = await this.sendAndReceive({}, "openNotebook");
    let sessionId = resp.sessionId;

    let column = getRightViewColumn();
    const panel = vscode.window.createWebviewPanel(
      "continue.debugPanelView",
      "Continue",
      column,
      {
        enableScripts: true,
        retainContextWhenHidden: true,
      }
    );

    // And set its HTML content
    panel.webview.html = setupDebugPanel(panel, this._context, sessionId);
  }

  acceptRejectSuggestion(accept: boolean) {
    // TODO
  }

  // ------------------------------------ //
  // Respond to request

  getOpenFiles(): string[] {
    return vscode.window.visibleTextEditors.map((editor) => {
      return editor.document.uri.fsPath;
    });
  }

  getHighlightedCode(): RangeInFile[] {
    // TODO
    return [];
  }
}

export default IdeProtocolClient;
