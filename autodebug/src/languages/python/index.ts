export function lineIsFunctionDef(line: string): boolean {
  return line.startsWith("def ");
}

export function parseFunctionDefForName(line: string): string {
  return line.split("def ")[1].split("(")[0];
}

export function lineIsComment(line: string): boolean {
  return line.trim().startsWith("#");
}

const tracebackStart = "Traceback (most recent call last):";
const tracebackEnd = (buf: string): string | undefined => {
  let lines = buf
    .split("\n")
    .filter((line: string) => line.trim() !== "~~^~~")
    .filter((line: string) => line.trim() !== "");
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
export function parseFirstStacktrace(stdout: string): string | undefined {
  let startIdx = stdout.indexOf(tracebackStart);
  if (startIdx < 0) return undefined;
  stdout = stdout.substring(startIdx);
  return tracebackEnd(stdout);
}
