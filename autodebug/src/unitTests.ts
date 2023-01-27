import * as vscode from "vscode";
import { writeUnitTestForFunction } from "./bridge";
import {
  decorationManager,
  showGutterSpinner,
  writeAndShowUnitTest,
} from "./textEditorDisplay";

export async function writeUnitTestCommand(editor: vscode.TextEditor) {
  let position = editor.selection.active;

  let gutterSpinnerKey = showGutterSpinner(editor, position.line);
  let test = await writeUnitTestForFunction(editor.document.fileName, position);

  decorationManager.deleteDecoration(gutterSpinnerKey);
  writeAndShowUnitTest(editor.document.fileName, test);
}
