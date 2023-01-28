/* Terminal emulator */

import * as vscode from "vscode";
const pty = require("node-pty");
const os = require("os");
import { debugPanelWebview } from "./debugPanel"; // Need to consider having multiple panels, where to store this state.

abstract class TerminalSnooper {
  abstract onData(data: string): void;
}

class PythonTracebackSnooper {
  static tracebackStart = "Traceback (most recent call last):";
  tracebackBuffer = "";

  constructor() {}

  static tracebackEnd = (buf: string): string | undefined => {
    let lines = buf.split("\n");
    for (let i = 0; i < lines.length; i++) {
      if (
        lines[i].startsWith("  File") &&
        i + 2 < lines.length &&
        lines[i + 2][0] != " "
      ) {
        return lines.slice(0, i + 3).join("\n");
      }
    }
    return undefined;
  };

  onData(data: string): void {
    // Snoop for traceback
    let idx = data.indexOf(PythonTracebackSnooper.tracebackStart);
    if (idx >= 0) {
      this.tracebackBuffer = data.substr(idx);
    } else if (this.tracebackBuffer.length > 0) {
      this.tracebackBuffer += data;
    }
    // End of traceback, send to webview
    if (idx > 0 || this.tracebackBuffer.length > 0) {
      let wholeTraceback = PythonTracebackSnooper.tracebackEnd(
        this.tracebackBuffer
      );
      if (wholeTraceback) {
        debugPanelWebview.postMessage({
          type: "traceback",
          traceback: wholeTraceback,
        });
      }
    }
  }
}

const DEFAULT_SNOOPERS = [new PythonTracebackSnooper()];

// Whenever a user opens a terminal, replace it with ours
vscode.window.onDidOpenTerminal((terminal) => {
  if (terminal.name != "AutoDebug") {
    terminal.dispose();
    openCapturedTerminal();
  }
});

export function openCapturedTerminal(
  snoopers: TerminalSnooper[] = DEFAULT_SNOOPERS
) {
  // A lot of basic setup for the terminal emulator
  let workspaceFolders = vscode.workspace.workspaceFolders;
  if (!workspaceFolders) return;

  // If there is another existing, non-AutoDebug terminal, delete it
  let terminals = vscode.window.terminals;
  for (let i = 0; i < terminals.length; i++) {
    if (terminals[i].name != "AutoDebug") {
      terminals[i].dispose();
    }
  }

  var isWindows = os.platform() === "win32";
  var shell = isWindows ? "powershell.exe" : "zsh";

  var ptyProcess = pty.spawn(shell, [], {
    name: "xterm-256color",
    cols: 100, // TODO: Get size of vscode terminal, and change with resize
    rows: 26,
    cwd: isWindows ? process.env.USERPROFILE : process.env.HOME,
    env: Object.assign({ TEST: "Environment vars work" }, process.env),
    useConpty: true,
  });

  const writeEmitter = new vscode.EventEmitter<string>();

  ptyProcess.onData((data: any) => {
    // Let each of the snoopers see the new data
    for (let snooper of snoopers) {
      snooper.onData(data);
    }

    // Pass data through to terminal
    writeEmitter.fire(data);
  });
  process.on("exit", () => ptyProcess.kill());

  setTimeout(() => {
    ptyProcess.write("cd " + workspaceFolders![0].uri.fsPath + " && clear\r");
    // setTimeout(() => {
    //   writeEmitter.fire(
    //     "This terminal will parse stdout to automatically detect stacktraces\r\n"
    //   );
    // }, 200);
  }, 1000);

  const newPty: vscode.Pseudoterminal = {
    onDidWrite: writeEmitter.event,
    open: () => {},
    close: () => {},
    handleInput: (data) => {
      ptyProcess.write(data);
    },
  };
  const terminal = vscode.window.createTerminal({
    name: "AutoDebug",
    pty: newPty,
  });
  terminal.show();
}
