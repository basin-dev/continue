import * as vscode from "vscode";
import {
  getRightViewColumn,
  getTestFile,
  getViewColumnOfFile,
  translate,
} from "./vscodeUtils";
import * as path from "path";
import { sendTelemetryEvent, TelemetryEvent } from "./telemetry";

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
    contentText: "Press ctrl+shift+enter to accept",
    margin: "0 0 0 1em",
  },
});
let oldSelDecorationType = vscode.window.createTextEditorDecorationType({
  backgroundColor: "rgb(255, 0, 0, 0.25)",
  isWholeLine: true,
  after: {
    contentText: "Press ctrl+shift+enter to reject",
    margin: "0 0 0 1em",
  },
});

/* Keyed by editor.document.uri.toString() */
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

  let olds: vscode.Range[] = [],
    news: vscode.Range[] = [],
    oldSels: vscode.Range[] = [],
    newSels: vscode.Range[] = [];
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
function selectSuggestion(
  accept: SuggestionSelectionOption,
  key: SuggestionRanges | null = null
) {
  let editor = vscode.window.activeTextEditor;
  if (!editor) return;
  let editorUri = editor.document.uri.toString();
  let suggestions = editorToSuggestions.get(editorUri);

  if (!suggestions) return;

  let idx: number | undefined;
  if (key) {
    // Use the key to find a specific suggestion
    for (let i = 0; i < suggestions.length; i++) {
      if (
        suggestions[i].newRange === key.newRange &&
        suggestions[i].oldRange === key.oldRange
      ) {
        // Don't include newSelected in the comparison, because it can change
        idx = i;
        break;
      }
    }
  } else {
    // Otherwise, use the current suggestion
    idx = currentSuggestion.get(editorUri);
  }
  if (idx === undefined) return;

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

export function acceptSuggestionCommand(key: SuggestionRanges | null = null) {
  sendTelemetryEvent(TelemetryEvent.SuggestionAccepted);
  selectSuggestion("selected", key);
}

export async function rejectSuggestionCommand(
  key: SuggestionRanges | null = null
) {
  sendTelemetryEvent(TelemetryEvent.SuggestionRejected);
  selectSuggestion("old", key);
}

export async function showSuggestion(
  editorFilename: string,
  range: vscode.Range,
  suggestion: string
): Promise<boolean> {
  let editor = await openEditorAndRevealRange(editorFilename, range);
  if (!editor) return Promise.resolve(false);

  let existingCode = editor.document.getText(
    new vscode.Range(range.start, range.end)
  );

  // If any of the outside lines are the same, don't repeat them in the suggestion
  let slines = suggestion.split("\n");
  let elines = existingCode.split("\n");
  let linesRemovedBefore = 0;
  let linesRemovedAfter = 0;
  while (slines.length > 0 && elines.length > 0 && slines[0] === elines[0]) {
    slines.shift();
    elines.shift();
    linesRemovedBefore++;
  }

  while (
    slines.length > 0 &&
    elines.length > 0 &&
    slines[slines.length - 1] === elines[elines.length - 1]
  ) {
    slines.pop();
    elines.pop();
    linesRemovedAfter++;
  }

  suggestion = slines.join("\n");
  if (suggestion === "") return Promise.resolve(false); // Don't even make a suggestion if they are exactly the same

  range = new vscode.Range(
    new vscode.Position(range.start.line + linesRemovedBefore, 0),
    new vscode.Position(
      range.end.line - linesRemovedAfter,
      elines.at(-1)?.length || 0
    )
  );

  return new Promise((resolve, reject) => {
    editor!
      .edit((edit) => {
        if (range.end.line + 1 >= editor.document.lineCount) {
          suggestion = "\n" + suggestion;
        }
        edit.insert(
          new vscode.Position(range.end.line + 1, 0),
          suggestion + "\n"
        );
      })
      .then(
        (success) => {
          if (success) {
            let suggestionRange = new vscode.Range(
              new vscode.Position(range.end.line + 1, 0),
              new vscode.Position(
                range.end.line + suggestion.split("\n").length,
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

// Show unit test
const pythonImportDistinguisher = (line: string): boolean => {
  if (line.startsWith("from") || line.startsWith("import")) {
    return true;
  }
  return false;
};
const javascriptImportDistinguisher = (line: string): boolean => {
  if (line.startsWith("import")) {
    return true;
  }
  return false;
};
const importDistinguishersMap: {
  [fileExtension: string]: (line: string) => boolean;
} = {
  js: javascriptImportDistinguisher,
  ts: javascriptImportDistinguisher,
  py: pythonImportDistinguisher,
};
function getImportsFromFileString(
  fileString: string,
  importDistinguisher: (line: string) => boolean
): Set<string> {
  let importLines = new Set<string>();
  for (let line of fileString.split("\n")) {
    if (importDistinguisher(line)) {
      importLines.add(line);
    }
  }
  return importLines;
}
function removeRedundantLinesFrom(
  fileContents: string,
  linesToRemove: Set<string>
): string {
  let fileLines = fileContents.split("\n");
  fileLines = fileLines.filter((line: string) => {
    return !linesToRemove.has(line);
  });
  return fileLines.join("\n");
}

export async function writeAndShowUnitTest(
  filename: string,
  test: string
): Promise<DecorationKey> {
  return new Promise((resolve, reject) => {
    let testFilename = getTestFile(filename, true);
    vscode.workspace.openTextDocument(testFilename).then((doc) => {
      let column = getRightViewColumn();
      let fileContent = doc.getText();
      let existingImportLines = getImportsFromFileString(
        fileContent,
        importDistinguishersMap[doc.fileName.split(".").at(-1) || ".py"]
      );
      test = removeRedundantLinesFrom(test, existingImportLines);
      for (let line of test.split("\n"))
        vscode.window.showTextDocument(doc, column).then((editor) => {
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
              edit.insert(lastLine.range.end, "\n\n" + test);
              return true;
            })
            .then((success) => {
              if (!success) reject("Failed to insert test");
              let key = highlightCode(editor, testRange);
              resolve(key);
            });
        });
    });
  });
}
