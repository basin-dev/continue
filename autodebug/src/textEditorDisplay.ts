import * as vscode from "vscode";
import { getViewColumnOfFile, translate } from "./vscodeUtils";
import * as path from "path";

// SUGGESTIONS INTERFACE //

interface SuggestionRanges {
  oldRange: vscode.Range;
  newRange: vscode.Range;
  newSelected: boolean;
}

let newDecorationType = vscode.window.createTextEditorDecorationType({
  backgroundColor: "rgb(0, 255, 0, 0.1)",
  isWholeLine: true,
});
let oldDecorationType = vscode.window.createTextEditorDecorationType({
  backgroundColor: "rgb(255, 0, 0, 0.1)",
  isWholeLine: true,
  cursor: "pointer",
});
let newSelDecorationType = vscode.window.createTextEditorDecorationType({
  backgroundColor: "rgb(0, 255, 0, 0.25)",
  isWholeLine: true,
  after: {
    contentText: "Press cmd+shift+enter to accept",
  },
});
let oldSelDecorationType = vscode.window.createTextEditorDecorationType({
  backgroundColor: "rgb(255, 0, 0, 0.25)",
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

// When tab is reopened, rerender the decorations:
vscode.window.onDidChangeActiveTextEditor((editor) => {
  if (!editor) return;
  rerenderDecorations(editor.document.uri.toString());
});
vscode.workspace.onDidOpenTextDocument((doc) => {
  rerenderDecorations(doc.uri.toString());
});

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

type SuggestionSelectionOption = "old" | "new" | "selected";
function selectSuggestion(accept: SuggestionSelectionOption) {
  let editor = vscode.window.activeTextEditor;
  if (!editor) return;
  let editorUri = editor.document.uri.toString();
  let suggestions = editorToSuggestions.get(editorUri);
  let idx = currentSuggestion.get(editorUri);

  if (!suggestions || idx === undefined) return;

  let [suggestion] = suggestions.splice(idx, 1);

  var rangeToDelete: vscode.Range;
  switch (accept) {
    case "old":
      rangeToDelete = suggestion.newRange;
      break;
    case "new":
      rangeToDelete = suggestion.oldRange;
      break;
    case "selected":
      rangeToDelete = suggestion.newSelected
        ? suggestion.oldRange
        : suggestion.newRange;
  }

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

export function acceptSuggestionCommand() {
  selectSuggestion("selected");
}

export async function rejectSuggestionCommand() {
  selectSuggestion("old");
}

export async function showSuggestion(
  editorFilename: string,
  range: vscode.Range,
  suggestion: string
): Promise<boolean> {
  let editor = await openEditorAndRevealRange(editorFilename, range);
  if (!editor) return Promise.resolve(false);
  return new Promise((resolve, reject) => {
    editor!
      .edit((edit) => {
        if (range.end.line + 1 === editor.document.lineCount) {
          suggestion = "\n" + suggestion;
        }
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

            const filename = editor!.document.uri.toString();
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

// EVERYTHING ELSE //

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

export function showLintingError() {}

type DecorationKey = {
  editorUri: string;
  options: vscode.DecorationOptions;
  decorationType: vscode.TextEditorDecorationType;
};

function rerenderDecorationType(
  editor: vscode.TextEditor,
  type: vscode.TextEditorDecorationType
) {}

class DecorationManager {
  private editorToDecorations = new Map<
    string,
    Map<vscode.TextEditorDecorationType, vscode.DecorationOptions[]>
  >();

  constructor() {}

  private rerenderDecorations(
    editorUri: string,
    decorationType: vscode.TextEditorDecorationType
  ) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      return;
    }

    const decorationTypes = this.editorToDecorations.get(editorUri);
    if (!decorationTypes) {
      return;
    }

    const decorations = decorationTypes.get(decorationType);
    if (!decorations) {
      return;
    }

    editor.setDecorations(decorationType, decorations);
  }

  addDecoration(key: DecorationKey) {
    let decorationTypes = this.editorToDecorations.get(key.editorUri);
    if (!decorationTypes) {
      decorationTypes = new Map();
      decorationTypes.set(key.decorationType, [key.options]);
      this.editorToDecorations.set(key.editorUri, decorationTypes);
    }

    const decorations = decorationTypes.get(key.decorationType);
    if (!decorations) {
      decorationTypes.set(key.decorationType, [key.options]);
    } else {
      decorations.push(key.options);
    }
    this.rerenderDecorations(key.editorUri, key.decorationType);
  }

  deleteDecoration(key: DecorationKey) {
    let decorationTypes = this.editorToDecorations.get(key.editorUri);
    if (!decorationTypes) {
      return;
    }

    let decorations = decorationTypes?.get(key.decorationType);
    if (!decorations) {
      return;
    }

    decorations = decorations.filter((decOpts) => decOpts !== key.options);
    decorationTypes.set(key.decorationType, decorations);
    this.rerenderDecorations(key.editorUri, key.decorationType);
  }

  deleteAllDecorations(editorUri: string) {
    let decorationTypes = this.editorToDecorations.get(editorUri)?.keys();
    if (!decorationTypes) {
      return;
    }
    this.editorToDecorations.delete(editorUri);
    for (let decorationType of decorationTypes) {
      this.rerenderDecorations(editorUri, decorationType);
    }
  }
}

export const decorationManager = new DecorationManager();

function constructBaseKey(
  editor: vscode.TextEditor,
  lineno: number,
  decorationType?: vscode.TextEditorDecorationType
): DecorationKey {
  return {
    editorUri: editor.document.uri.toString(),
    options: {
      range: new vscode.Range(lineno, 0, lineno, 0),
    },
    decorationType:
      decorationType || vscode.window.createTextEditorDecorationType({}),
  };
}

const gutterSpinnerDecorationType =
  vscode.window.createTextEditorDecorationType({
    gutterIconPath: vscode.Uri.file(
      path.join(__dirname, "..", "media", "spinner.gif")
    ),
    gutterIconSize: "contain",
  });

export function showGutterSpinner(
  editor: vscode.TextEditor,
  lineno: number
): DecorationKey {
  const key = constructBaseKey(editor, lineno, gutterSpinnerDecorationType);
  decorationManager.addDecoration(key);
  return key;
}

export function showLintMessage(
  editor: vscode.TextEditor,
  lineno: number,
  msg: string
): DecorationKey {
  const key = constructBaseKey(editor, lineno);
  key.decorationType = vscode.window.createTextEditorDecorationType({
    after: {
      contentText: "Linting error",
      color: "rgb(255, 0, 0, 0.6)",
    },
    gutterIconPath: vscode.Uri.file(
      path.join(__dirname, "..", "media", "error.png")
    ),
    gutterIconSize: "contain",
  });
  key.options.hoverMessage = msg;
  decorationManager.addDecoration(key);
  return key;
}

export function highlightCode(
  editor: vscode.TextEditor,
  range: vscode.Range,
  removeOnClick: boolean = true
): DecorationKey {
  const decorationType = vscode.window.createTextEditorDecorationType({
    backgroundColor: "rgb(255, 255, 0, 0.1)",
  });
  const key = {
    editorUri: editor.document.uri.toString(),
    options: {
      range,
    },
    decorationType,
  };
  decorationManager.addDecoration(key);

  if (removeOnClick) {
    vscode.window.onDidChangeTextEditorSelection((e) => {
      if (e.textEditor === editor) {
        decorationManager.deleteDecoration(key);
      }
    });
  }

  return key;
}

export function insertSuggestionSnippet(
  editor: vscode.TextEditor,
  options: string[],
  location: vscode.Position | vscode.Range
) {
  let opts = options.map((opt: string) => opt.replace(",", "\\,"));
  editor.insertSnippet(
    new vscode.SnippetString(`\${1|${opts.join(",")}|}`),
    location,
    { undoStopBefore: false, undoStopAfter: false }
  );
}

export function selectSurroundingFunction(
  editor: vscode.TextEditor,
  pos: vscode.Position
) {
  // TODO: I think there should be some way to get language server information, like that which defines code folding
  editor.selection = new vscode.Selection(
    new vscode.Position(pos.line - 1, 0),
    new vscode.Position(pos.line + 1, 0)
  );
}

export function openEditorAndRevealRange(
  editorFilename: string,
  range?: vscode.Range
): Promise<vscode.TextEditor> {
  return new Promise((resolve, _) => {
    // Check if the editor is already open
    let viewColumn = getViewColumnOfFile(editorFilename);

    vscode.workspace.openTextDocument(editorFilename).then((doc) => {
      vscode.window.showTextDocument(doc, viewColumn).then((editor) => {
        if (range) {
          editor.revealRange(range);
        }
        resolve(editor);
      });
    });
  });
}
