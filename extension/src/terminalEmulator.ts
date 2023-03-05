/* Terminal emulator */

import * as vscode from "vscode";
import { extensionContext } from "./activation/activate";
import pty = require("node-pty");
import os = require("os");
import { debugPanelWebview } from "./debugPanel"; // Need to consider having multiple panels, where to store this state.

abstract class TerminalSnooper {
  abstract onData(data: string): void;
  abstract onWrite(data: string): void;
}

abstract class CommandCaptureSnooper extends TerminalSnooper {
  stdinBuffer = "";
  cursorPos = 0;
  stdoutHasInterrupted = false;

  abstract onCommand(data: string): void;

  static RETURN_KEY = "\r";
  static DEL_KEY = "\x7F";
  static UP_KEY = "\x1B[A";
  static DOWN_KEY = "\x1B[B";
  static RIGHT_KEY = "\x1B[C";
  static LEFT_KEY = "\x1B[D";
  static CONTROL_KEYS = new Set([
    CommandCaptureSnooper.RETURN_KEY,
    CommandCaptureSnooper.DEL_KEY,
    CommandCaptureSnooper.UP_KEY,
    CommandCaptureSnooper.DOWN_KEY,
    CommandCaptureSnooper.RIGHT_KEY,
    CommandCaptureSnooper.LEFT_KEY,
  ]);

  private _cursorLeft() {
    this.cursorPos = Math.max(0, this.cursorPos - 1);
  }
  private _cursorRight() {
    this.cursorPos = Math.min(this.stdinBuffer.length, this.cursorPos + 1);
  }
  // Known issue: This does not handle autocomplete.
  // Would be preferable to find a way that didn't require this all, just parsing by command prompt
  // but that has it's own challenges
  private handleControlKey(data: string): void {
    switch (data) {
      case CommandCaptureSnooper.DEL_KEY:
        this.stdinBuffer =
          this.stdinBuffer.slice(0, this.cursorPos - 1) +
          this.stdinBuffer.slice(this.cursorPos);
        this._cursorLeft();
        break;
      case CommandCaptureSnooper.RETURN_KEY:
        this.onCommand(this.stdinBuffer);
        this.stdinBuffer = "";
        break;
      case CommandCaptureSnooper.UP_KEY:
      case CommandCaptureSnooper.DOWN_KEY:
        this.stdinBuffer = "";
        break;
      case CommandCaptureSnooper.RIGHT_KEY:
        this._cursorRight();
        break;
      case CommandCaptureSnooper.LEFT_KEY:
        this._cursorLeft();
        break;
    }
  }

  onWrite(data: string): void {
    if (CommandCaptureSnooper.CONTROL_KEYS.has(data)) {
      this.handleControlKey(data);
    } else {
      this.stdinBuffer =
        this.stdinBuffer.substring(0, this.cursorPos) +
        data +
        this.stdinBuffer.substring(this.cursorPos);
      this._cursorRight();
    }
  }

  onData(data: string): void {}
}

class PythonTracebackSnooper extends TerminalSnooper {
  static tracebackStart = "Traceback (most recent call last):";
  tracebackBuffer = "";

  constructor() {
    super();
  }

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
  override onWrite(data: string): void {}
  override onData(data: string): void {
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
        this.tracebackBuffer = "";

        if (debugPanelWebview) {
          debugPanelWebview.postMessage({
            type: "traceback",
            value: wholeTraceback,
          });
        } else {
          vscode.commands
            .executeCommand("continue.openDebugPanel", extensionContext)
            .then(() => {
              // TODO: Waiting for the webview to load, but should add a hook to the onLoad message event. Same thing in autodebugTest command in commands.ts
              setTimeout(() => {
                debugPanelWebview?.postMessage({
                  type: "traceback",
                  value: wholeTraceback,
                });
              }, 500);
            });
        }
      }
    }
  }
}

class PyTestSnooper extends CommandCaptureSnooper {
  constructor() {
    super();
  }

  override onCommand(data: string): void {
    if (data.trim().startsWith("pytest ")) {
      let fileAndFunctionSpecifier = data.split(" ")[1];
      vscode.commands.executeCommand(
        "continue.debugTest",
        fileAndFunctionSpecifier
      );
    }
  }
}

const DEFAULT_SNOOPERS = [new PythonTracebackSnooper(), new PyTestSnooper()];

// Whenever a user opens a terminal, replace it with ours
vscode.window.onDidOpenTerminal((terminal) => {
  if (terminal.name != "Continue") {
    terminal.dispose();
    openCapturedTerminal();
  }
});

function getDefaultShell(): string {
  if (process.platform !== "win32") {
    return os.userInfo().shell;
  }
  switch (process.platform) {
    case "win32":
      return process.env.COMSPEC || "cmd.exe";
    // case "darwin":
    //   return process.env.SHELL || "/bin/zsh";
    // default:
    //   return process.env.SHELL || "/bin/sh";
  }
}

function getRootDir(): string | undefined {
  var isWindows = os.platform() === "win32";
  let cwd = isWindows ? process.env.USERPROFILE : process.env.HOME;
  if (
    vscode.workspace.workspaceFolders &&
    vscode.workspace.workspaceFolders.length > 0
  ) {
    cwd = vscode.workspace.workspaceFolders[0].uri.fsPath;
  }
  return cwd;
}

export function openCapturedTerminal(
  snoopers: TerminalSnooper[] = DEFAULT_SNOOPERS
) {
  // If there is another existing, non-Continue terminal, delete it
  let terminals = vscode.window.terminals;
  for (let i = 0; i < terminals.length; i++) {
    if (terminals[i].name != "Continue") {
      terminals[i].dispose();
    }
  }

  let env = { ...(process.env as any) };
  if (os.platform() !== "win32") {
    env["PATH"] += ":" + ["/opt/homebrew/bin", "/opt/homebrew/sbin"].join(":");
  }

  var ptyProcess = pty.spawn(getDefaultShell(), [], {
    name: "xterm-256color",
    cols: 160, // TODO: Get size of vscode terminal, and change with resize
    rows: 26,
    cwd: getRootDir(),
    env,
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

  const newPty: vscode.Pseudoterminal = {
    onDidWrite: writeEmitter.event,
    open: () => {},
    close: () => {},
    handleInput: (data) => {
      for (let snooper of snoopers) {
        snooper.onWrite(data);
      }
      ptyProcess.write(data);
    },
  };
  const terminal = vscode.window.createTerminal({
    name: "Continue",
    pty: newPty,
  });
  terminal.show();

  setTimeout(() => {
    ptyProcess.write("clear\r");
  }, 500);
}
