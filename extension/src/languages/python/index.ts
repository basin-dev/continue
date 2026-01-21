import path = require("path");
import { LanguageLibrary } from "../index.d";

const tracebackStart = "Traceback (most recent call last):";
const tracebackEnd = (buf: string): string | undefined => {
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

function parseFirstStacktrace(stdout: string): string | undefined {
  let startIdx = stdout.indexOf(tracebackStart);
  if (startIdx < 0) return undefined;
  stdout = stdout.substring(startIdx);
  return tracebackEnd(stdout);
}

function lineIsFunctionDef(line: string): boolean {
  return line.startsWith("def ");
}

function parseFunctionDefForName(line: string): string {
  return line.split("def ")[1].split("(")[0];
}

function lineIsComment(line: string): boolean {
  return line.trim().startsWith("#");
}

function writeImport(
  sourcePath: string,
  pathToImport: string,
  namesToImport: string[] | undefined = undefined
): string {
  let segs = path.relative(sourcePath, pathToImport).split(path.sep);
  let importFrom = "";
  for (let seg of segs) {
    if (seg === "..") {
      importFrom = "." + importFrom;
    } else {
      if (!importFrom.endsWith(".")) {
        importFrom += ".";
      }
      importFrom += seg.split(".").slice(0, -1).join(".");
    }
  }

  return `from ${importFrom} import ${
    namesToImport ? namesToImport.join(", ") : "*"
  }`;
}

const pythonLangaugeLibrary: LanguageLibrary = {
  language: "python",
  fileExtensions: [".py"],
  parseFirstStacktrace,
  lineIsFunctionDef,
  parseFunctionDefForName,
  lineIsComment,
  writeImport,
};

export default pythonLangaugeLibrary;
