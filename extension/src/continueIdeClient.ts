// import { ShowSuggestionRequest } from "../schema/ShowSuggestionRequest";
import { showSuggestion } from "./suggestions";
import { openEditorAndRevealRange, getRightViewColumn } from "./util/vscode";
import { FileEdit, RangeInFile } from "./client";
import * as vscode from "vscode";
import { acceptSuggestionCommand, rejectSuggestionCommand } from "./suggestions";
import { setupDebugPanel } from "./debugPanel";

// should this be moved here, exported by `suggestions.ts`, or just copied?
interface SuggestionRanges {
  oldRange: vscode.Range;
  newRange: vscode.Range;
  newSelected: boolean;
}

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
    )
  }

  openFile(filepath: string) {
    // vscode has a builtin open/get open files
    openEditorAndRevealRange(filepath, undefined, vscode.ViewColumn.One);
  }

  // ------------------------------------ //
  // Initiate Request

  closeNotebook() {
    // close the debug panel webview
    let panel: vscode.WebviewPanel | undefined;
    if (panel) {
      panel.dispose();
    }
    this._ws.close();
  }

  openNotebook() {
    // Open notebook is straightforward, just see debugPanel for how we do this
    // how to reference the notebook? same as the debug panel?
    (context: vscode.ExtensionContext) => {
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
      panel.webview.html = setupDebugPanel(panel, context);

    };
  }

  acceptRejectSuggestion(accept: boolean, key: SuggestionRanges) {
    // or should function definitions from `suggestions.ts` be moved / copied here?
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

  getHighlightedCode(): RangeInFile[] {
    
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      return [];
    }

    const selection = editor.selection;
    if (selection.isEmpty) {
      return [];
    }

    const selectedCodeRange: RangeInFile = {
      range: new vscode.Range(
        selection.start.line,
        selection.start.character,
        selection.end.line,
        selection.end.character,
      ),
      filepath: editor.document.fileName,
    };

    // 'RangeInFile' is missing the following properties: length, pop, push, concat, and 29 more??
    return selectedCodeRange;

  }
}

export default IdeProtocolClient;