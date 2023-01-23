import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import { writeUnitTestForFunction } from "./bridge";
import {
  decorationManager,
  highlightCode,
  openEditorAndRevealRange,
  showGutterSpinner,
} from "./textEditorDisplay";
import { getTestFile } from "./vscodeUtils";

export async function writeUnitTestCommand(
  editor: vscode.TextEditor,
  edit: vscode.TextEditorEdit
) {
  let selection = editor.selection.active;
  let gutterSpinnerKey = showGutterSpinner(editor, selection.line);

  let test = await writeUnitTestForFunction(
    editor.document.fileName,
    selection
  );

  decorationManager.deleteDecoration(gutterSpinnerKey);

  let testFilename = getTestFile(editor.document.fileName, true);
  vscode.workspace.openTextDocument(testFilename).then((doc) => {
    vscode.window
      .showTextDocument(doc, vscode.ViewColumn.Beside)
      .then((editor) => {
        let lastLine = editor.document.lineAt(editor.document.lineCount - 1);
        let testRange = new vscode.Range(
          lastLine.range.end,
          new vscode.Position(
            test.split("\n").length + lastLine.range.end.line,
            0
          )
        );
        editor
          .edit((edit) => {
            edit.insert(lastLine.range.end, test);
            return true;
          })
          .then((success) => {
            if (!success) return;
            highlightCode(editor, testRange);
          });
      });
  });
}
