import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

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

export function getTestFile(
  filename: string,
  createFile: boolean = false
): string {
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

  const directory = path.join(path.dirname(filename), "tests");
  const testFilename = path.join(directory, basename + path.extname(filename));

  // Optionally, create the file if it doesn't exist
  if (createFile && !fs.existsSync(testFilename)) {
    if (!fs.existsSync(directory)) {
      fs.mkdirSync(directory);
    }
    fs.writeFileSync(testFilename, "");
  }

  return testFilename;
}
