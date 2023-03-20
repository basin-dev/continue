import { getExtensionUri } from "../util/vscode";
const util = require("util");
const exec = util.promisify(require("child_process").exec);
import * as path from "path";
import * as fs from "fs";
import rebuild from "@electron/rebuild";

async function setupPythonEnv() {
  console.log("Setting up python env for Continue extension...");
  let command = `cd ${path.join(
    getExtensionUri().fsPath,
    "scripts"
  )} && python3 -m venv env && source env/bin/activate && pip3 install --upgrade pip && pip3 install -r requirements.txt`;
  const { stdout, stderr } = await exec(command);
  if (stderr) {
    throw new Error(stderr);
  }
  console.log(
    "Successfully set up python env at ",
    getExtensionUri().fsPath + "/scripts/env"
  );
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
  await Promise.all([setupPythonEnv(), installNodeModules()]);
}
