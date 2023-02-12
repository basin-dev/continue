import { parseFirstStacktrace as parseFirstStacktracePython } from "../python";

export function parseFirstStacktrace(stdout: string) {
  return parseFirstStacktracePython(stdout);
}
