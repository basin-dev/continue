import * as vscode from "vscode";
import { translate } from "./vscodeUtils";

interface SuggestionRanges {
  oldRange: vscode.Range;
  newRange: vscode.Range;
  newSelected: boolean;
}

let newDecorationType = vscode.window.createTextEditorDecorationType({
  backgroundColor: "rgb(0, 255, 0, 0.2)",
  isWholeLine: true,
});
let oldDecorationType = vscode.window.createTextEditorDecorationType({
  backgroundColor: "rgb(255, 0, 0, 0.2)",
  isWholeLine: true,
  cursor: "pointer",
});
let newSelDecorationType = vscode.window.createTextEditorDecorationType({
  backgroundColor: "rgb(0, 255, 0, 0.5)",
  isWholeLine: true,
  after: {
    contentText: "Press cmd+shift+enter to accept",
  },
});
let oldSelDecorationType = vscode.window.createTextEditorDecorationType({
  backgroundColor: "rgb(255, 0, 0, 0.5)",
  isWholeLine: true,
  after: {
    contentText: "Press cmd+shift+enter to reject",
  },
});

export const editorToSuggestions: Map<
  string, // URI of file
  SuggestionRanges[]
> = new Map();
export let currentSuggestion: Map<string, number> = new Map(); // Map from editor URI to index of current SuggestionRanges in editorToSuggestions

export function rerenderDecorations(editorUri: string) {
  let suggestions = editorToSuggestions.get(editorUri);
  let idx = currentSuggestion.get(editorUri);
  let editor = vscode.window.visibleTextEditors.find(
    (editor) => editor.document.uri.toString() === editorUri
  );
  if (!suggestions || !editor) return;

  let olds = [],
    news = [],
    oldSels = [],
    newSels = [];
  for (let i = 0; i < suggestions.length; i++) {
    let suggestion = suggestions[i];
    if (typeof idx != "undefined" && idx === i) {
      if (suggestion.newSelected) {
        olds.push(suggestion.oldRange);
        newSels.push(suggestion.newRange);
      } else {
        oldSels.push(suggestion.oldRange);
        news.push(suggestion.newRange);
      }
    } else {
      olds.push(suggestion.oldRange);
      news.push(suggestion.newRange);
    }
  }
  editor.setDecorations(oldDecorationType, olds);
  editor.setDecorations(newDecorationType, news);
  editor.setDecorations(oldSelDecorationType, oldSels);
  editor.setDecorations(newSelDecorationType, newSels);

  // Reveal the range in the editor
  if (idx === undefined) return;
  editor.revealRange(
    suggestions[idx].newRange,
    vscode.TextEditorRevealType.Default
  );
}

export function suggestionDownCommand() {
  let editor = vscode.window.activeTextEditor;
  if (!editor) return;
  let editorUri = editor.document.uri.toString();
  let suggestions = editorToSuggestions.get(editorUri);
  let idx = currentSuggestion.get(editorUri);
  if (!suggestions || idx === undefined) return;

  let suggestion = suggestions[idx];
  if (!suggestion.newSelected) {
    suggestion.newSelected = true;
  } else if (idx + 1 < suggestions.length) {
    currentSuggestion.set(editorUri, idx + 1);
  } else return;
  rerenderDecorations(editorUri);
}

export function suggestionUpCommand() {
  let editor = vscode.window.activeTextEditor;
  if (!editor) return;
  let editorUri = editor.document.uri.toString();
  let suggestions = editorToSuggestions.get(editorUri);
  let idx = currentSuggestion.get(editorUri);
  if (!suggestions || idx === undefined) return;

  let suggestion = suggestions[idx];
  if (suggestion.newSelected) {
    suggestion.newSelected = false;
  } else if (idx > 0) {
    currentSuggestion.set(editorUri, idx - 1);
  } else return;
  rerenderDecorations(editorUri);
}

export function acceptSuggestionCommand() {
  let editor = vscode.window.activeTextEditor;
  if (!editor) return;
  let editorUri = editor.document.uri.toString();
  let suggestions = editorToSuggestions.get(editorUri);
  let idx = currentSuggestion.get(editorUri);

  if (!suggestions || idx === undefined) return;

  let [suggestion] = suggestions.splice(idx, 1);
  var rangeToDelete = suggestion.newSelected
    ? suggestion.oldRange
    : suggestion.newRange;
  rangeToDelete = new vscode.Range(
    rangeToDelete.start,
    new vscode.Position(rangeToDelete.end.line + 1, 0)
  );
  editor.edit((edit) => {
    edit.delete(rangeToDelete);
  });

  // Shift the below suggestions up
  let linesToShift = rangeToDelete.end.line - rangeToDelete.start.line;
  for (let below of suggestions) {
    // Assumes there should be no crossover between suggestions. Might want to enforce this.
    if (
      below.oldRange.union(below.newRange).start.line >
      suggestion.oldRange.union(suggestion.newRange).start.line
    ) {
      below.oldRange = translate(below.oldRange, -linesToShift);
      below.newRange = translate(below.newRange, -linesToShift);
    }
  }

  if (suggestions.length === 0) {
    currentSuggestion.delete(editorUri);
  } else {
    currentSuggestion.set(editorUri, Math.min(idx, suggestions.length - 1));
  }
  rerenderDecorations(editorUri);
}

export function showSuggestion(
  editor: vscode.TextEditor,
  range: vscode.Range,
  suggestion: string
): Promise<boolean> {
  return new Promise((resolve, reject) => {
    editor
      .edit((edit) => {
        edit.insert(new vscode.Position(range.end.line + 1, 0), suggestion);
      })
      .then(
        (success) => {
          if (success) {
            let suggestionRange = new vscode.Range(
              new vscode.Position(range.end.line + 1, 0),
              new vscode.Position(
                range.end.line + suggestion.split("\n").length - 1,
                0
              )
            );

            const filename = editor.document.uri.toString();
            if (editorToSuggestions.has(filename)) {
              let suggestions = editorToSuggestions.get(filename)!;
              suggestions.push({
                oldRange: range,
                newRange: suggestionRange,
                newSelected: true,
              });
              editorToSuggestions.set(filename, suggestions);
              currentSuggestion.set(filename, suggestions.length - 1);
            } else {
              editorToSuggestions.set(filename, [
                {
                  oldRange: range,
                  newRange: suggestionRange,
                  newSelected: true,
                },
              ]);
              currentSuggestion.set(filename, 0);
            }

            rerenderDecorations(filename);
          }
          resolve(success);
        },
        (reason) => reject(reason)
      );
  });
}

export function showAnswerInTextEditor(
  filename: string,
  range: vscode.Range,
  answer: string
) {
  vscode.workspace.openTextDocument(vscode.Uri.file(filename)).then((doc) => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      return;
    }

    // Open file, reveal range, show decoration
    vscode.window.showTextDocument(doc).then((new_editor) => {
      new_editor.revealRange(
        new vscode.Range(range.end, range.end),
        vscode.TextEditorRevealType.InCenter
      );

      let decorationType = vscode.window.createTextEditorDecorationType({
        after: {
          contentText: answer + "\n",
          color: "rgb(0, 255, 0, 0.8)",
        },
        backgroundColor: "rgb(0, 255, 0, 0.2)",
      });
      new_editor.setDecorations(decorationType, [range]);
      vscode.window.showInformationMessage("Answer found!");

      // Remove decoration when user moves cursor
      vscode.window.onDidChangeTextEditorSelection((e) => {
        if (
          e.textEditor === new_editor &&
          e.selections[0].active.line !== range.end.line
        ) {
          new_editor.setDecorations(decorationType, []);
        }
      });
    });
  });
}
