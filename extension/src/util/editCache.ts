import { debugApi } from "../bridge";
import { FileEdit, SerializedDebugContext } from "../client";
import { addFileSystemToDebugContext } from "./util";

/**
 * Stores preloaded edits, invalidating based off of debug context changes
 */
export class EditCache {
  private _lastDebugContext: SerializedDebugContext | undefined;
  private _cachedEdits: FileEdit[] | undefined;

  private _debugContextChanged(debugContext: SerializedDebugContext): boolean {
    if (!this._lastDebugContext) {
      return true;
    }

    return (
      JSON.stringify(this._lastDebugContext) !== JSON.stringify(debugContext)
    );
  }

  private async _fetchNewEdit(
    debugContext: SerializedDebugContext
  ): Promise<FileEdit[]> {
    debugContext = addFileSystemToDebugContext(debugContext);
    let suggestedEdits = (
      await debugApi.editEndpointDebugEditPost({
        serializedDebugContext: debugContext,
      })
    ).completion;
    return suggestedEdits;
  }

  public async preloadEdit(debugContext: SerializedDebugContext) {
    if (this._debugContextChanged(debugContext)) {
      this._cachedEdits = await this._fetchNewEdit(debugContext);
      this._lastDebugContext = debugContext;
    }
  }

  public async getEdit(
    debugContext: SerializedDebugContext
  ): Promise<FileEdit[]> {
    if (this._debugContextChanged(debugContext)) {
      console.log("Cache miss");
      this._cachedEdits = await this._fetchNewEdit(debugContext);
    } else {
      console.log("Cache hit");
    }

    return this._cachedEdits!;
  }
}
