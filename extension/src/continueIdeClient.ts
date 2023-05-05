// import { ShowSuggestionRequest } from "../schema/ShowSuggestionRequest";
import { showSuggestion, SuggestionRanges } from "./suggestions";
import { openEditorAndRevealRange, getRightViewColumn } from "./util/vscode";
import { FileEdit } from "../schema/FileEdit";
import { RangeInFile } from "../schema/RangeInFile";
import * as vscode from "vscode";
import {
  acceptSuggestionCommand,
  rejectSuggestionCommand,
} from "./suggestions";
import { debugPanelWebview, setupDebugPanel } from "./debugPanel";
import { FileEditWithFullContents } from "../schema/FileEditWithFullContents";
const util = require("util");
const exec = util.promisify(require("child_process").exec);
const WebSocket = require("ws");
import fs = require("fs");

class IdeProtocolClient {
  private _ws: WebSocket | null = null;
  private _panels: Map<string, vscode.WebviewPanel> = new Map();
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
    let msg = JSON.stringify({ messageType, ...data });
    this._ws!.send(msg);
    console.log("Sent message", msg);
  }

  async receiveMessage(messageType: string): Promise<any> {
    await this.isConnected();
    console.log("Connected to websocket");
    return await new Promise((resolve, reject) => {
      if (!this._ws) {
        reject("Not connected to websocket");
      }
      this._ws!.onmessage = (event: any) => {
        let message = JSON.parse(event.data);
        console.log("RECEIVED MESSAGE", message);
        if (message.messageType === messageType) {
          resolve(message);
        }
      };
    });
  }

  async sendAndReceive(message: any, messageType: string): Promise<any> {
    try {
      await this.send(messageType, message);
      let msg = await this.receiveMessage(messageType);
      console.log("Received message", msg);
      return msg;
    } catch (e) {
      console.log("Error sending message", e);
    }
  }

  async handleMessage(message: any) {
    switch (message.messageType) {
      case "highlightedCode":
        this.send("highlightedCode", {
          highlightedCode: this.getHighlightedCode(),
        });
        break;
      case "workspaceDirectory":
        this.send("workspaceDirectory", {
          workspaceDirectory: this.getWorkspaceDirectory(),
        });
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
      case "setFileOpen":
        this.openFile(message.filepath);
        // TODO: Close file
        break;
      case "openNotebook":
      case "connected":
        break;
      default:
        throw Error("Unknown message type:" + message.messageType);
    }
  }
  getWorkspaceDirectory() {
    return vscode.workspace.workspaceFolders![0].uri.fsPath;
  }

  // ------------------------------------ //
  // On message handlers

  showSuggestion(edit: FileEdit) {
    // showSuggestion already exists
    showSuggestion(
      edit.filepath,
      new vscode.Range(
        edit.range.start.line,
        edit.range.start.character,
        edit.range.end.line,
        edit.range.end.character
      ),
      edit.replacement
    );
  }

  openFile(filepath: string) {
    // vscode has a builtin open/get open files
    openEditorAndRevealRange(filepath, undefined, vscode.ViewColumn.One);
  }

  // ------------------------------------ //
  // Initiate Request

  closeNotebook(sessionId: string) {
    this._panels.get(sessionId)?.dispose();
    this._panels.delete(sessionId);
  }

  async openNotebook() {
    console.log("OPENING NOTEBOOK");
    let resp = await this.sendAndReceive({}, "openNotebook");
    let sessionId = resp.sessionId;
    console.log("SESSION ID", sessionId);

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

    this._panels.set(sessionId, panel);
  }

  acceptRejectSuggestion(accept: boolean, key: SuggestionRanges) {
    if (accept) {
      acceptSuggestionCommand(key);
    } else {
      rejectSuggestionCommand(key);
    }
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
          edit.range.start.character,
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

  runCommand(command: string) {
    vscode.window.terminals[0].sendText(command, true);
    // But need to know when it's done executing...
  }
}

export default IdeProtocolClient;
