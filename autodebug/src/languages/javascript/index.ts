import * as stackTraceParser from "stacktrace-parser";

export function parseFirstStacktrace(stdout: string): string | undefined {
  let stacktrace = stackTraceParser.parse(stdout);
  if (stacktrace.length > 0) return stacktrace.toString();
  return undefined;
}
