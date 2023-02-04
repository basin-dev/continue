import { getExtensionUri } from "./vscodeUtils";
const util = require("util");
const exec = util.promisify(require("child_process").exec);
import * as path from "path";

async function setupPythonEnv() {
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
  console.log("Installing node modules for autodebug extension...");
  const { stdout, stderr } = await exec(
    `cd ${getExtensionUri().fsPath} && npm install && npm run rebuild`
  );
  console.log("Standard out from installing node modules: ", stdout);
  console.log("Standard error from installing node modules: ", stderr);
}

export async function setupExtensionEnvironment() {
  await Promise.all([setupPythonEnv(), installNodeModules()]);
}
