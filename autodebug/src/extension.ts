import * as vscode from "vscode";
import { setupExtensionEnvironment } from "./environmentSetup";

export function activate(context: vscode.ExtensionContext) {
  vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: "Setting up AutoDebug extension...",
      cancellable: false,
    },
    async () => {
      await setupExtensionEnvironment();
      const { activateExtension } = await import("./activate");
      activateExtension(context);
    }
  );
}
