import { getExtensionUri } from "../util/vscode";
const util = require("util");
const exec = util.promisify(require("child_process").exec);
const { spawn } = require("child_process");
import * as path from "path";
import * as fs from "fs";
import rebuild from "@electron/rebuild";
import * as vscode from "vscode";
import { getContinueServerUrl } from "../bridge";

async function setupPythonEnv() {
  console.log("Setting up python env for Continue extension...");
  // First check that python3 is installed

  var { stdout, stderr } = await exec("python3 --version");
  if (stderr) {
    console.log("Python3 not found, downloading...");
    await downloadPython3();
  }

  let command = `cd ${path.join(
    getExtensionUri().fsPath,
    "scripts"
  )} && python3 -m venv env && source env/bin/activate && pip3 install --upgrade pip && pip3 install -r requirements.txt`;
  var { stdout, stderr } = await exec(command);
  if (stderr) {
    throw new Error(stderr);
  }
  console.log(
    "Successfully set up python env at ",
    getExtensionUri().fsPath + "/scripts/env"
  );

  await startContinuePythonServer();
}

function readEnvFile(path: string) {
  if (!fs.existsSync(path)) {
    return {};
  }
  let envFile = fs.readFileSync(path, "utf8");

  let env: { [key: string]: string } = {};
  envFile.split("\n").forEach((line) => {
    let [key, value] = line.split("=");
    if (typeof key === "undefined" || typeof value === "undefined") {
      return;
    }
    env[key] = value.replace(/"/g, "");
  });
  return env;
}

function writeEnvFile(path: string, key: string, value: string) {
  if (!fs.existsSync(path)) {
    fs.writeFileSync(path, `${key}=${value}`);
    return;
  }

  let env = readEnvFile(path);
  env[key] = value;

  let newEnvFile = "";
  for (let key in env) {
    newEnvFile += `${key}="${env[key]}"\n`;
  }
  fs.writeFileSync(path, newEnvFile);
}

export async function startContinuePythonServer() {
  // Check vscode settings
  let serverUrl = getContinueServerUrl();
  if (serverUrl !== "http://localhost:8000") {
    return;
  }

  let envFile = path.join(getExtensionUri().fsPath, "scripts", ".env");
  let openai_api_key: string | undefined =
    readEnvFile(envFile)["OPENAI_API_KEY"];
  while (typeof openai_api_key === "undefined" || openai_api_key === "") {
    openai_api_key = await vscode.window.showInputBox({
      prompt: "Enter your OpenAI API key",
      placeHolder: "Enter your OpenAI API key",
    });
    // Write to .env file
  }
  writeEnvFile(envFile, "OPENAI_API_KEY", openai_api_key);

  console.log("Starting Continue python server...");
  // Kill any existing python server
  try {
    await exec(
      "lsof -i tcp:8000 | grep LISTEN | awk '{print $2}' | xargs kill -9"
    );
  } catch (e) {
    console.log("Failed to kill existing Continue python server", e);
  }

  let command = `cd ${path.join(
    getExtensionUri().fsPath,
    "scripts"
  )} && source env/bin/activate && cd .. && python3 -m scripts.run_continue_server`;
  try {
    // exec(command);
    let child = spawn(command, {
      shell: true,
    });
    child.stdout.on("data", (data: any) => {
      console.log(`stdout: ${data}`);
    });
    child.stderr.on("data", (data: any) => {
      console.log(`stderr: ${data}`);
    });
    child.on("error", (error: any) => {
      console.log(`error: ${error.message}`);
    });
  } catch (e) {
    console.log("Failed to start Continue python server", e);
  }
  // Sleep for 3 seconds to give the server time to start
  await new Promise((resolve) => setTimeout(resolve, 3000));
  console.log("Successfully started Continue python server");
}

async function installNodeModules() {
  console.log("Rebuilding node-pty for Continue extension...");
  await rebuild({
    buildPath: getExtensionUri().fsPath, // Folder containing node_modules
    electronVersion: "19.1.8",
    onlyModules: ["node-pty"],
  });
  console.log("Successfully rebuilt node-pty");
}

export function isPythonEnvSetup(): boolean {
  let pathToEnvCfg = getExtensionUri().fsPath + "/scripts/env/pyvenv.cfg";
  return fs.existsSync(path.join(pathToEnvCfg));
}

export async function setupExtensionEnvironment() {
  console.log("Setting up environment for Continue extension...");
  await Promise.all([setupPythonEnv(), installNodeModules()]);
}

export async function downloadPython3() {
  let os = process.platform;
  let command: string = "";
  if (os === "darwin") {
    throw new Error("python3 not found");
  } else if (os === "linux") {
    command =
      "sudo apt update && upgrade && sudo apt install python3 python3-pip";
  } else if (os === "win32") {
    throw new Error("python3 not found");
  }

  const { stdout, stderr } = await exec(command);
  if (stderr) {
    throw new Error(stderr);
  }
  console.log("Successfully downloaded python3");
}
