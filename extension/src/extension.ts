/**
 * This is the entry point for the extension.
 */

import * as vscode from "vscode";
import {
  setupExtensionEnvironment,
  isPythonEnvSetup,
} from "./activation/environmentSetup";

async function dynamicImportAndActivate(
  context: vscode.ExtensionContext,
  showTutorial: boolean
) {
  const { activateExtension } = await import("./activation/activate");
  activateExtension(context, showTutorial);
}

export function activate(context: vscode.ExtensionContext) {
  // Only show progress if we have to setup
  if (isPythonEnvSetup()) {
    dynamicImportAndActivate(context, false);
  } else {
    vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "Setting up AutoDebug extension...",
        cancellable: false,
      },
      async () => {
        await setupExtensionEnvironment();
        dynamicImportAndActivate(context, true);
      }
    );
  }
}
