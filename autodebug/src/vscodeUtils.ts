import * as vscode from "vscode";
import * as path from "path";

export function translate(range: vscode.Range, lines: number): vscode.Range {
  return new vscode.Range(
    range.start.line + lines,
    range.start.character,
    range.end.line + lines,
    range.end.character
  );
}

export function getNonce() {
  let text = "";
  const possible =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (let i = 0; i < 32; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}

export function getTestFile(filename: string): string {
  let basename = path.basename(filename).split(".")[0];
  switch (path.extname(filename)) {
    case ".py":
      basename += "_test";
      break;
    case ".js":
    case ".jsx":
    case ".ts":
    case ".tsx":
      basename += ".test";
      break;
    default:
      basename += "_test";
  }

  return path.join(
    path.dirname(filename),
    "tests",
    basename + path.extname(filename)
  );
}
