import * as vscode from "vscode";
import path = require("path");
const util = require("util");
const exec = util.promisify(require("child_process").exec);

function get_python_path() {
  return "/Users/natesesti/Desktop/basin/unit-test-experiments";
}

function build_python_command(cmd: string): string {
  return `cd ${get_python_path()} && source env/bin/activate && ${cmd}`;
}

function parseStdout(
  stdout: string,
  key: string,
  until_end: boolean = false
): string {
  const prompt = `${key}=`;
  let lines = stdout.split("\n");

  let value: string = "";
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith(prompt)) {
      if (until_end) {
        return lines.slice(i).join("\n").substring(prompt.length);
      } else {
        return lines[i].substring(prompt.length);
      }
    }
  }
  return "";
}

export async function askQuestion(
  question: string,
  workspacePath: string
): Promise<{ answer: string; range: vscode.Range; filename: string }> {
  const command = build_python_command(
    `python3 ${path.join(
      get_python_path(),
      "ask.py"
    )} ask ${workspacePath} "${question}"`
  );

  const { stdout, stderr } = await exec(command);
  if (stderr) {
    throw new Error(stderr);
  }
  // Use the output
  const answer = parseStdout(stdout, "Answer");
  const filename = parseStdout(stdout, "Filename");
  const startLineno = parseInt(parseStdout(stdout, "Start lineno"));
  const endLineno = parseInt(parseStdout(stdout, "End lineno"));
  const range = new vscode.Range(
    new vscode.Position(startLineno, 0),
    new vscode.Position(endLineno, 0)
  );
  if (answer && filename && startLineno && endLineno) {
    return { answer, filename, range };
  } else {
    throw new Error("Error: No answer found");
  }
}

// Write a docstring for the most specific function or class at the current line in the given file
export async function writeDocstringForFunction(
  filename: string,
  position: vscode.Position
): Promise<{ lineno: number; docstring: string }> {
  const command = build_python_command(
    `python3 ${path.join(get_python_path(), "ds_gen.py")} forline ${filename} ${
      position.line
    }`
  );

  const { stdout, stderr } = await exec(command);
  if (stderr) {
    throw new Error(stderr);
  }

  const lineno = parseInt(parseStdout(stdout, "Line number"));
  const docstring = parseStdout(stdout, "Docstring", true);
  if (lineno && docstring) {
    return { lineno, docstring };
  } else {
    throw new Error("Error: No docstring found");
  }
}
