import * as vscode from "vscode";
import * as path from "path";
const axios = require("axios").default;
import { getExtensionUri } from "./vscodeUtils";
const util = require("util");
const exec = util.promisify(require("child_process").exec);

function get_python_path() {
  return path.join(getExtensionUri().fsPath, "..");
}

function get_api_url() {
  let extensionUri = getExtensionUri();
  let configFile = path.join(extensionUri.fsPath, "config/config.json");
  let config = require(configFile);
  console.log("Loaded config: ", config);
  if (config.API_URL) {
    return config.API_URL;
  }
  return "http://localhost:8000";
}
const API_URL = get_api_url();

function build_python_command(cmd: string): string {
  return `cd ${get_python_path()} && source env/bin/activate && ${cmd}`;
}

function listToCmdLineArgs(list: string[]): string {
  return list.map((el) => `"$(echo "${el}")"`).join(" ");
}

export async function runPythonScript(
  scriptName: string,
  args: string[]
): Promise<any> {
  const command = `cd ${path.join(
    getExtensionUri().fsPath,
    "scripts"
  )} && source env/bin/activate && python3 ${scriptName} ${listToCmdLineArgs(
    args
  )}`;

  const { stdout, stderr } = await exec(command);
  if (stderr) {
    throw new Error(stderr);
  }

  let jsonString = stdout.substring(
    stdout.indexOf("{"),
    stdout.lastIndexOf("}") + 1
  );
  jsonString = jsonString.replace(/'/g, '"').replace(/"/g, "'"); // This is problematic if you have any escaped quotes
  return JSON.parse(jsonString);
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

export async function apiRequest(
  endpoint: string,
  options: {
    method?: string;
    query?: { [key: string]: any };
    body?: { [key: string]: any };
  }
): Promise<any> {
  let defaults = {
    method: "GET",
    query: {},
    body: {},
  };
  options = Object.assign(defaults, options); // Second takes over first
  if (endpoint.startsWith("/")) endpoint = endpoint.substring(1);

  let resp = await axios({
    method: options.method,
    url: `${API_URL}/${endpoint}`,
    data: options.body,
    params: options.query,
  });

  return resp.data;
}

// Write a docstring for the most specific function or class at the current line in the given file
export async function writeDocstringForFunction(
  filename: string,
  position: vscode.Position
): Promise<{ lineno: number; docstring: string }> {
  let resp = await apiRequest("docstring/forline", {
    query: {
      filecontents: (
        await vscode.workspace.fs.readFile(vscode.Uri.file(filename))
      ).toString(),
      lineno: position.line.toString(),
    },
  });

  const lineno = resp.lineno;
  const docstring = resp.completion;
  if (lineno && docstring) {
    return { lineno, docstring };
  } else {
    throw new Error("Error: No docstring returned");
  }
}

// Should be "suggest fix given a line number and a file"
// and also "find sus line number and file given a problem"
// basically need to be able to go from any amount of information
// Even no stack trace, just description of problem -> sus lines of code -> fix
// Should have a series of functions that "enrich" the context, learning increasingly
// more about the bug

// Can be undefined because should be fine to just specify (filename, range & filename, code, code & filename, all three)
// Really don't want just range, that doesn't help (having range without filename is useless)
export interface CodeSelection {
  filename?: string;
  range?: vscode.Range;
  code?: string;
}
export interface CompleteCodeSelection {
  filename: string;
  range: vscode.Range;
  code: string;
}
export interface DebugContext {
  stacktrace?: string;
  explanation?: string;
  unitTest?: string;
  suggestion?: string;
  codeSelections?: CodeSelection[];
}

function completeCodeSelectionTypeguard(
  codeSelection: CodeSelection
): codeSelection is CompleteCodeSelection {
  return (
    codeSelection.filename !== undefined &&
    codeSelection.range !== undefined &&
    codeSelection.code !== undefined
  );
}

export async function getSuggestion(ctx: DebugContext): Promise<DebugContext> {
  let codeSelection = ctx.codeSelections?.at(0);
  let resp: any;
  if (codeSelection && completeCodeSelectionTypeguard(codeSelection)) {
    // Can utilize the fact that we know right where the bug is
    resp = await apiRequest("debug/inline", {
      body: {
        filecontents: (
          await vscode.workspace.fs.readFile(
            vscode.Uri.file(codeSelection.filename)
          )
        ).toString(),
        startline: codeSelection.range.start.line,
        endline: codeSelection.range.end.line,
        stacktrace: ctx.stacktrace,
      },
      method: "POST",
    });
  } else {
    resp = await apiRequest("debug/suggestion", {
      query: {
        stacktrace: ctx.stacktrace,
      },
    });
  }

  ctx.suggestion = resp.completion;
  return ctx;
}

export async function listTenThings(ctx: DebugContext): Promise<string> {
  if (!ctx.codeSelections?.filter((cs) => cs.code !== undefined)) return "";

  let resp = await apiRequest("debug/list", {
    body: {
      stacktrace: ctx.stacktrace,
      description: ctx.explanation,
      code: ctx.codeSelections.map((cs) => cs.code!),
    },
    method: "POST",
  });

  return resp.completion;
}

function parseMultipleFileSuggestion(suggestion: string): string[] {
  let suggestions: string[] = [];
  let currentFileLines: string[] = [];
  let lastWasFile = false;
  let insideFile = false;
  for (let line of suggestion.split("\n")) {
    if (line.trimStart().startsWith("File #")) {
      lastWasFile = true;
    } else if (lastWasFile && line.startsWith("```")) {
      lastWasFile = false;
      insideFile = true;
    } else if (insideFile) {
      if (line.startsWith("```")) {
        insideFile = false;
        suggestions.push(currentFileLines.join("\n"));
        currentFileLines = [];
      } else {
        currentFileLines.push(line);
      }
    }
  }
  return suggestions;
}

export async function makeEdit(ctx: DebugContext): Promise<string[]> {
  if (!ctx.codeSelections?.filter((cs) => cs.code !== undefined)) return [];

  let resp = await apiRequest("debug/edit", {
    body: {
      stacktrace: ctx.stacktrace,
      description: ctx.explanation,
      code: ctx.codeSelections.map((cs) => cs.code!),
    },
    method: "POST",
  });

  const suggestions = parseMultipleFileSuggestion(resp.completion);
  return suggestions;
}

export interface CodeLocation {
  filename: string;
  range: vscode.Range;
  codee?: string;
}

export async function findSuspiciousCode(
  ctx: DebugContext
): Promise<CodeLocation[]> {
  if (!ctx.stacktrace) return [];
  let files = await getFileContents(
    getFilenamesFromPythonStacktrace(ctx.stacktrace)
  );
  let resp = await apiRequest("debug/find", {
    body: {
      stacktrace: ctx.stacktrace,
      description: ctx.explanation,
      files,
    },
    method: "POST",
  });

  return resp.response.map((loc: any) => {
    return {
      filename: loc.filename,
      range: new vscode.Range(
        new vscode.Position(loc.startline - 1, 0),
        new vscode.Position(loc.endline - 1, loc.code.split("\n").at(-1).length) // - 1 because VSCode Ranges are 0-indexed. Last thing gets last char of line
      ),
      code: loc.code,
    };
  });
}

export async function writeUnitTestForFunction(
  filename: string,
  position: vscode.Position
): Promise<string> {
  let resp = await apiRequest("unittest/forline", {
    method: "POST",
    body: {
      filecontents: (
        await vscode.workspace.fs.readFile(vscode.Uri.file(filename))
      ).toString(),
      lineno: position.line,
    },
  });

  return resp.completion;
}

// TODO: This whole file shouldn't really exist, nor its functions. Should just be api calls made throughout the codebase
// UNLESS: You always pass the entire DebugContext object into all these functions so they have the same interface from the VSCode extensions,
// but then you strip out unecessary information here when you upgrade your backend capabilities. Then only have to edit that in a single spot,
// and a lot easier to keep track of.

async function getFileContents(
  files: string[]
): Promise<{ [key: string]: string }> {
  let contents = await Promise.all(
    files.map(async (file: string) => {
      return (
        await vscode.workspace.fs.readFile(vscode.Uri.file(file))
      ).toString();
    })
  );
  let fileContents: { [key: string]: string } = {};
  for (let i = 0; i < files.length; i++) {
    fileContents[files[i]] = contents[i];
  }
  return fileContents;
}

function getFilenamesFromPythonStacktrace(stacktrace: string): string[] {
  let filenames: string[] = [];
  for (let line of stacktrace.split("\n")) {
    let match = line.match(/File "(.*)", line/);
    if (match) {
      filenames.push(match[1]);
    }
  }
  return filenames;
}
