export abstract class TerminalSnooper<T> {
  abstract onData(data: string): void;
  abstract onWrite(data: string): void;
  callback: (data: T) => void;

  constructor(callback: (data: T) => void) {
    this.callback = callback;
  }
}

function stripAnsi(data: string) {
  const pattern = [
    "[\\u001B\\u009B][[\\]()#;?]*(?:(?:(?:(?:;[-a-zA-Z\\d\\/#&.:=?%@~_]+)*|[a-zA-Z\\d]+(?:;[-a-zA-Z\\d\\/#&.:=?%@~_]*)*)?\\u0007)",
    "(?:(?:\\d{1,4}(?:;\\d{0,4})*)?[\\dA-PR-TZcf-ntqry=><~]))",
  ].join("|");

  let regex = new RegExp(pattern, "g");
  return data.replace(regex, "");
}

export class CommandCaptureSnooper extends TerminalSnooper<string> {
  stdinBuffer = "";
  cursorPos = 0;
  stdoutHasInterrupted = false;

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
        this.callback(this.stdinBuffer);
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

export class PythonTracebackSnooper extends TerminalSnooper<string> {
  static tracebackStart = "Traceback (most recent call last):";
  tracebackBuffer = "";

  static tracebackEnd = (buf: string): string | undefined => {
    let lines = buf
      .split("\n")
      .filter((line: string) => line.trim() !== "~~^~~")
      .filter((line: string) => line.trim() !== "");
    
    // Find the last "File" line to identify where the error message starts
    let lastFileLineIndex = -1;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].startsWith("  File")) {
        lastFileLineIndex = i;
      }
    }
    
    if (lastFileLineIndex === -1) {
      return undefined;
    }
    
    // The error line should be at lastFileLineIndex + 2 (after the code line)
    // We need to ensure there's at least an error line
    if (lastFileLineIndex + 2 >= lines.length) {
      return undefined;
    }
    
    // Check that the error line doesn't start with a space (it's the exception line)
    if (lines[lastFileLineIndex + 2][0] === " ") {
      return undefined;
    }
    
    // Now capture all lines from the error line onwards that are part of the error message
    // Error continuation lines typically start with spaces or are non-empty text
    let endIndex = lastFileLineIndex + 3;
    while (endIndex < lines.length) {
      const line = lines[endIndex];
      // Stop if we hit what looks like a new prompt or unrelated output
      // Error message continuation lines typically don't start with common prompt patterns
      // and don't look like new tracebacks or file references
      if (line.startsWith("Traceback ") || 
          line.startsWith("  File") ||
          line.match(/^[a-zA-Z]:\\/) ||  // Windows path
          line.match(/^\$\s/) ||  // Shell prompt
          line.match(/^>>>\s/) ||  // Python REPL prompt
          line.match(/^\(.*\)\s*\$/) ||  // Virtualenv prompt
          line.match(/^\[.*\]\s*\$/)) {  // Other prompt patterns
        break;
      }
      endIndex++;
    }
    
    return lines.slice(0, endIndex).join("\n");
  };
  override onWrite(data: string): void {}
  override onData(data: string): void {
    let strippedData = stripAnsi(data);
    // Strip fully blank and squiggle lines
    strippedData = strippedData
      .split("\n")
      .filter((line) => line.trim().length > 0 && line.trim() !== "~~^~~")
      .join("\n");
    // Snoop for traceback
    let idx = strippedData.indexOf(PythonTracebackSnooper.tracebackStart);
    if (idx >= 0) {
      this.tracebackBuffer = strippedData.substr(idx);
    } else if (this.tracebackBuffer.length > 0) {
      this.tracebackBuffer += "\n" + strippedData;
    }
    // End of traceback, send to webview
    if (this.tracebackBuffer.length > 0) {
      let wholeTraceback = PythonTracebackSnooper.tracebackEnd(
        this.tracebackBuffer
      );
      if (wholeTraceback) {
        this.callback(wholeTraceback);
        this.tracebackBuffer = "";
      }
    }
  }
}
