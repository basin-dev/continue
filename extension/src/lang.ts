import {
  LanguageClient,
  ServerOptions,
  LanguageClientOptions,
} from "vscode-languageclient/node";
import { ExtensionContext, workspace } from "vscode";
import * as path from "path";

function startLanguageServerClient(context: ExtensionContext) {
  let serverModule = context.asAbsolutePath(path.join("server", "server.js"));

  let debugOptions = { execArgv: ["--nolazy", "--debug=6004"] };
  let serverOptions: ServerOptions = {
    run: { module: serverModule },
    debug: { module: serverModule, options: debugOptions },
  };

  let clientOptions: LanguageClientOptions = {
    documentSelector: ["plaintext"],
    synchronize: {
      // Synchronize the setting section 'languageServerExample' to the server
      configurationSection: "languageServerExample",
      // Notify the server about file changes to '.clientrc files contain in the workspace
      fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
    },
  };

  // Create the language client and start the client.
  let disposable = new LanguageClient(
    "Language Server Example",
    serverOptions,
    clientOptions
  ).start();

  // Push the disposable to the context's subscriptions so that the
  // client can be deactivated on extension deactivation
  context.subscriptions.push(disposable);
}
