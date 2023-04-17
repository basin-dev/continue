import { FileEditWithFullContents } from "../schema/FileEditWithFullContents";
import { FileEdit } from "../schema/FileEdit";
import { RangeInFile } from "../schema/RangeInFile";
import * as vscode from "vscode";
import { setupDebugPanel } from "./debugPanel";
import { getRightViewColumn, openEditorAndRevealRange } from "./util/vscode";
const util = require("util");
const exec = util.promisify(require("child_process").exec);
const WebSocket = require("ws");
import fs = require("fs");

class IdeProtocolClient {
  private _ws: WebSocket | null = null;
  private readonly _serverUrl: string;
  private readonly _context: vscode.ExtensionContext;

  private _makingEdit = 0;

  constructor(serverUrl: string, context: vscode.ExtensionContext) {
    this._context = context;
    this._serverUrl = serverUrl;
    let ws = new WebSocket(serverUrl);
    this._ws = ws;
    ws.onclose = () => {
      this._ws = null;
    };
    ws.on("message", (data: any) => {
      this.handleMessage(JSON.parse(data));
    });
    // Setup listeners for any file changes in open editors
    vscode.workspace.onDidChangeTextDocument((event) => {
      if (this._makingEdit === 0) {
        let fileEdits: FileEditWithFullContents[] = event.contentChanges.map(
          (change) => {
            return {
              fileEdit: {
                filepath: event.document.uri.fsPath,
                range: {
                  start: {
                    line: change.range.start.line,
                    character: change.range.start.character,
                  },
                  end: {
                    line: change.range.end.line,
                    character: change.range.end.character,
                  },
                },
                replacement: change.text,
              },
              fileContents: event.document.getText(),
            };
          }
        );
        this.send("fileEdits", { fileEdits });
      } else {
        this._makingEdit--;
      }
    });
  }

  async isConnected() {
    if (this._ws === null) {
      this._ws = new WebSocket(this._serverUrl);
    }
    // On open, return a promise
    if (this._ws!.readyState === WebSocket.OPEN) {
      return;
    }
    return new Promise((resolve, reject) => {
      this._ws!.onopen = () => {
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
    this._ws!.send(JSON.stringify({ messageType, ...data }));
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
    let resp = await this.send(messageType, message);
    return await this.receiveMessage(messageType);
  }

  async handleMessage(message: any) {
    switch (message.messageType) {
      case "highlightedCode":
        this.send("highlightedCode", {
          highlightedCode: this.getHighlightedCode(),
        });
        break;
      case "openFiles":
        this.send("openFiles", {
          openFiles: this.getOpenFiles(),
        });
        break;
      case "readFile":
        this.send("readFile", {
          contents: this.readFile(message.filepath),
        });
        break;
      case "editFile":
        let fileEdit = await this.editFile(message.edit);
        this.send("editFile", {
          fileEdit,
        });
        break;
      case "saveFile":
        this.saveFile(message.filepath);
        break;
      case "openNotebook":
      case "connected":
        break;
      default:
        throw Error("Unknown message type:" + message.messageType);
    }
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
    // Create a new file
  }

  // ------------------------------------ //
  // Respond to request

  getOpenFiles(): string[] {
    return vscode.window.visibleTextEditors.map((editor) => {
      return editor.document.uri.fsPath;
    });
  }

  saveFile(filepath: string) {
    vscode.window.visibleTextEditors.forEach((editor) => {
      if (editor.document.uri.fsPath === filepath) {
        editor.document.save();
      }
    });
  }

  readFile(filepath: string): string {
    let contents: string | undefined;
    vscode.window.visibleTextEditors.forEach((editor) => {
      if (editor.document.uri.fsPath === filepath) {
        contents = editor.document.getText();
      }
    });
    if (!contents) {
      contents = fs.readFileSync(filepath, "utf-8");
    }
    return contents;
  }

  editFile(edit: FileEdit): Promise<FileEditWithFullContents> {
    return new Promise((resolve, reject) => {
      openEditorAndRevealRange(
        edit.filepath,
        undefined,
        vscode.ViewColumn.One
      ).then((editor) => {
        let range = new vscode.Range(
          edit.range.start.line,
          edit.range.start.character + 1,
          edit.range.end.line,
          edit.range.end.character + 1
        );
        editor.edit((editBuilder) => {
          this._makingEdit += 2; // editBuilder.replace takes 2 edits: delete and insert
          editBuilder.replace(range, edit.replacement);
          resolve({
            fileEdit: edit,
            fileContents: editor.document.getText(),
          });
        });
      });
    });
  }

  getHighlightedCode(): RangeInFile[] {
    // TODO
    let rangeInFiles: RangeInFile[] = [];
    vscode.window.visibleTextEditors.forEach((editor) => {
      editor.selections.forEach((selection) => {
        if (!selection.isEmpty) {
          rangeInFiles.push({
            filepath: editor.document.uri.fsPath,
            range: {
              start: {
                line: selection.start.line,
                character: selection.start.character,
              },
              end: {
                line: selection.end.line,
                character: selection.end.character,
              },
            },
          });
        }
      });
    });
    return rangeInFiles;
  }
}

export default IdeProtocolClient;
