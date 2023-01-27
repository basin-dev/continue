import { randomBytes } from "crypto";
import * as vscode from "vscode";
import { editorToSuggestions } from "./textEditorDisplay";

export class MyCodeLensProvider implements vscode.CodeLensProvider {
  public provideCodeLenses(
    document: vscode.TextDocument,
    token: vscode.CancellationToken
  ): vscode.CodeLens[] | Thenable<vscode.CodeLens[]> {
    let suggestions = editorToSuggestions.get(document.fileName);
    if (!suggestions) {
      return [];
    }

    let codeLenses: vscode.CodeLens[] = [];
    for (let suggestion of suggestions) {
      let range = suggestion.newRange.union(suggestion.oldRange);
      codeLenses.push(
        new vscode.CodeLens(range, {
          title: "Accept",
          command: "autodebug.acceptSuggestion",
        }),
        new vscode.CodeLens(range, {
          title: "Reject",
          command: "autodebug.rejectSuggestion",
        })
      );
    }

    return codeLenses;
  }

  onDidChangeCodeLenses?: vscode.Event<void> | undefined;

  constructor(emitter?: vscode.EventEmitter<void>) {
    if (emitter) {
      this.onDidChangeCodeLenses = emitter.event;
      this.onDidChangeCodeLenses(() => {
        if (vscode.window.activeTextEditor) {
          this.provideCodeLenses(
            vscode.window.activeTextEditor.document,
            new vscode.CancellationTokenSource().token
          );
        }
      });
    }
  }
}
