import { ShowSuggestionRequest } from "../schema/ShowSuggestionRequest";
import { FileEdit, RangeInFile } from "./client";
import * as vscode from "vscode";

class IdeProtocolClient {
  private readonly _ws: WebSocket;

  constructor(serverUrl: string) {
    this._ws = new WebSocket(serverUrl);

    // Setup listeners for any file changes in open editors
    vscode.workspace.onDidChangeTextDocument((event) => {});
  }

  send(message: any) {
    this._ws.send(JSON.stringify(message));
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

  openNotebook() {
    // TODO
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
  }
}

export default IdeProtocolClient;
