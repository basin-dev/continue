import * as vscode from "vscode";

export class MyCodeLensProvider implements vscode.CodeLensProvider {
  public provideCodeLenses(
    document: vscode.TextDocument,
    token: vscode.CancellationToken
  ): vscode.CodeLens[] | Thenable<vscode.CodeLens[]> {
    let range = new vscode.Range(0, 0, 5, 0);
    return [
      new vscode.CodeLens(range, {
        title: "test",
        command: "autodebug.acceptSuggestion",
      }),
      new vscode.CodeLens(range, {
        title: "test2",
        command: "autodebug.acceptSuggestion",
      }),
    ];
  }
}
