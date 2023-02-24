import * as vscode from "vscode";
import * as path from "path";
const axios = require("axios").default;
import { getExtensionUri, readFileAtRange } from "./util/vscode";
import { convertSingleToDoubleQuoteJSON } from "./util/util";
import { readFileSync } from "fs";
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
  // TODO: Need to make sure that the path to poetry is in the PATH and that it is installed in the first place. Realistically also need to install npm in some cases.
  const command = `export PATH="$PATH:/opt/homebrew/bin" && cd ${path.join(
    getExtensionUri().fsPath,
    "scripts"
  )} && poetry run python3 ${scriptName} ${listToCmdLineArgs(args)}`;

  const { stdout, stderr } = await exec(command);
  if (stderr) {
    throw new Error(stderr);
  }

  let jsonString = stdout.substring(
    stdout.indexOf("{"),
    stdout.lastIndexOf("}") + 1
  );
  jsonString = convertSingleToDoubleQuoteJSON(jsonString);
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
  console.log("API request: ", options.body);
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
  traceback?: string;
  description?: string;
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
        traceback: ctx.traceback,
        userid: vscode.env.machineId,
      },
      method: "POST",
    });
  } else {
    resp = await apiRequest("debug/suggestion", {
      query: {
        traceback: ctx.traceback,
      },
    });
  }

  ctx.suggestion = resp.completion;
  return ctx;
}

function codeSelectionsToVirtualFileSystem(codeSelections: CodeSelection[]): {
  [filepath: string]: string;
} {
  let virtualFileSystem: { [filepath: string]: string } = {};
  for (let cs of codeSelections) {
    if (!cs.filename) continue;
    if (cs.filename in virtualFileSystem) continue;
    let content = readFileSync(cs.filename, "utf8");
    virtualFileSystem[cs.filename] = content;
  }
  return virtualFileSystem;
}

export function serializeDebugContext(ctx: DebugContext): any {
  if (!ctx.codeSelections?.filter((cs) => cs.code !== undefined))
    return undefined;

  return {
    userid: vscode.env.machineId,
    traceback: ctx.traceback,
    description: ctx.description,
    filesystem: codeSelectionsToVirtualFileSystem(ctx.codeSelections),
    ranges_in_files: ctx.codeSelections.map((cs) => {
      return {
        filepath: cs.filename,
        range: cs.range,
      };
    }),
  };
}

export async function listTenThings(ctx: DebugContext): Promise<string> {
  let body = serializeDebugContext(ctx);
  if (!body) return "";

  let resp = await apiRequest("debug/list", {
    body,
    method: "POST",
  });

  return resp.completion;
}

export async function makeEdit(ctx: DebugContext): Promise<any[]> {
  let body = serializeDebugContext(ctx);
  if (!body) return [];

  let resp = await apiRequest("debug/edit", {
    body,
    method: "POST",
  });

  return resp.completion;
}

export interface CodeLocation {
  filename: string;
  range: vscode.Range;
  codee?: string;
}

export async function findSuspiciousCode(
  ctx: DebugContext
): Promise<CodeLocation[]> {
  if (!ctx.traceback) return [];
  let files = await getFileContents(
    getFilenamesFromPythonStacktrace(ctx.traceback)
  );
  let resp = await apiRequest("debug/find", {
    body: {
      traceback: ctx.traceback,
      description: ctx.description,
      filesystem: files,
    },
    method: "POST",
  });

  return await Promise.all(
    resp.response.map(async (loc: any) => {
      let range = new vscode.Range(
        loc.range.start.line,
        loc.range.start.character,
        loc.range.end.line,
        loc.range.end.character
      );
      let code = await readFileAtRange(range, loc.filepath);
      return {
        filename: loc.filepath,
        range,
        code,
      };
    })
  );
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
      userid: vscode.env.machineId,
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

function getFilenamesFromPythonStacktrace(traceback: string): string[] {
  let filenames: string[] = [];
  for (let line of traceback.split("\n")) {
    let match = line.match(/File "(.*)", line/);
    if (match) {
      filenames.push(match[1]);
    }
  }
  return filenames;
}
