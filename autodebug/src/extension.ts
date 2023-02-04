import * as vscode from "vscode";
import { setupExtensionEnvironment } from "./environmentSetup";

export function activate(context: vscode.ExtensionContext) {
  setupExtensionEnvironment().then(() => {
    import("./activate").then(({ activateExtension }) => {
      activateExtension(context);
    });
  });
}
