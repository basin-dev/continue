import * as vscode from "vscode";
import { exec } from "child_process";
import path = require("path");

function get_python_path() {
  return "/Users/natesesti/Desktop/basin/unit-test-experiments";
}

function build_python_command(cmd: string): string {
  return `cd ${get_python_path()} && source env/bin/activate && ${cmd}`;
}

function parseStdout(stdout: string, key: string): string {
  const prompt = `${key}=`;
  let lines = stdout.split("\n");
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith(prompt)) {
      return lines[i].substring(prompt.length);
    }
  }
  return "";
}

export function askQuestion(
  question: string,
  workspacePath: string
): Promise<{ answer: string; range: vscode.Range; filename: string }> {
  const command = build_python_command(
    `python3 ${path.join(
      get_python_path(),
      "ask.py"
    )} ask ${workspacePath} "${question}"`
  );

  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        reject(error);
        return;
      }
      if (stderr) {
        reject(stderr);
        return;
      }
      // Use the output
      const answer = parseStdout(stdout, "Answer");
      const filename = parseStdout(stdout, "Filename");
      const startLineno = parseInt(parseStdout(stdout, "Start lineno"));
      const EndLineno = parseInt(parseStdout(stdout, "End lineno"));
      const range = new vscode.Range(
        new vscode.Position(startLineno, 0),
        new vscode.Position(EndLineno, 0)
      );
      if (answer && filename && startLineno && EndLineno) {
        resolve({ answer, filename, range });
      } else {
        reject("Error: No answer found");
      }
    });
  });
}
