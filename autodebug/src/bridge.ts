import * as vscode from "vscode";
import path = require("path");
import * as dotenv from 'dotenv';

dotenv.config({ path: __dirname+'/.env' });
const util = require("util");
const exec = util.promisify(require("child_process").exec);

function get_python_path() {
  return String(process.env.PYTHON_PATH);
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

// Should be "suggest fix given a line number and a file"
// and also "find sus line number and file given a problem"
// basically need to be able to go from any amount of information
// Even no stack trace, just description of problem -> sus lines of code -> fix
// Should have a series of functions that "enrich" the context, learning increasingly
// more about the bug
export interface DebugContext {
  filename?: string;
  range?: vscode.Range;
  stacktrace?: string;
  explanation?: string;
  unitTest?: string;
  suggestion?: string;
  code?: string;
}
export async function getSuggestion(ctx: DebugContext): Promise<DebugContext> {
  let command: string;
  if (ctx.range && ctx.filename) {
    // Can utilize the fact that we know right where the bug is
    command = build_python_command(
      `python3 ${path.join(get_python_path(), "debug.py")} inline ${
        ctx.filename
      } ${ctx.range.start.line} ${ctx.range.end.line} "$(echo "${
        ctx.stacktrace
      }")"`
    );
  } else {
    command = build_python_command(
      `python3 ${path.join(
        get_python_path(),
        "debug.py"
      )} suggestion "$(echo "${ctx.stacktrace}")" "$(echo "${ctx.code}")"`
    );
  }
  const { stdout, stderr } = await exec(command);
  if (stderr) {
    throw new Error(stderr);
  }
  const suggestion = parseStdout(stdout, "Suggestion", true);
  ctx.suggestion = suggestion;
  return ctx;
}

export async function listTenThings(ctx: DebugContext): Promise<string> {
  let command = build_python_command(
    `python3 ${path.join(get_python_path(), "debug.py")} listten "$(echo "${
      ctx.stacktrace
    }")" "$(echo "${ctx.code}")" "$(echo "${ctx.explanation}")"`
  );
  const { stdout, stderr } = await exec(command);
  if (stderr) {
    throw new Error(stderr);
  }
  const tenThings = parseStdout(stdout, "Ten Things", true);
  return tenThings;
}

export async function makeEdit(ctx: DebugContext): Promise<string> {
  let command = build_python_command(
    `python3 ${path.join(get_python_path(), "debug.py")} edit "$(echo "${
      ctx.stacktrace
    }")" "$(echo "${ctx.code}")" "$(echo "${ctx.explanation}")"`
  );
  const { stdout, stderr } = await exec(command);
  if (stderr) {
    throw new Error(stderr);
  }
  const editedCode = parseStdout(stdout, "Edited Code", true);
  return editedCode;
}

export interface CodeLocation {
  filename: string;
  range: vscode.Range;
  codee?: string;
}

export async function findSuspiciousCode(
  ctx: DebugContext
): Promise<CodeLocation[]> {
  if (ctx.filename && ctx.range) return [];

  let command = build_python_command(
    `python3 ${path.join(get_python_path(), "debug.py")} findcode "$(echo "${
      ctx.stacktrace
    }")"`
  );
  const { stdout, stderr } = await exec(command);
  if (stderr) {
    throw new Error(stderr);
  }
  return [];
}

async function fullyEnrichContext(ctx: DebugContext): Promise<DebugContext> {
  if (!ctx.unitTest) {
    // generate unit test
  }
  if (!ctx.suggestion) {
    ctx = await getSuggestion(ctx);
  }
  return ctx;
}

export async function writeUnitTestForFunction(
  filename: string,
  position: vscode.Position
): Promise<string> {
  const command = build_python_command(
    `python3 ${path.join(
      get_python_path(),
      "test_gen.py"
    )} forline ${filename} ${position.line}`
  );

  const { stdout, stderr } = await exec(command);
  if (stderr) {
    throw new Error(stderr);
  }

  const unitTest = parseStdout(stdout, "Test", true);
  if (unitTest) {
    return unitTest;
  } else {
    throw new Error("Error: No unit test found");
  }
}
