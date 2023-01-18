import { exec } from "child_process";
import path = require("path");

function get_python_path() {
  return "/Users/natesesti/Desktop/basin/unit-test-experiments";
}

function build_python_command(cmd: string): string {
  return `cd ${get_python_path()} && source env/bin/activate && ${cmd}`;
}

export function askQuestion(
  question: string,
  workspacePath: string
): Promise<string> {
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
      const answer = stdout;
      resolve(answer);
    });
  });
}
