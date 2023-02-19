import * as Segment from "@segment/analytics-node";
import * as vscode from "vscode";

// Setup Segment
const SEGMENT_WRITE_KEY = "57yy2uYXH2bwMuy7djm9PorfFlYqbJL1";
const analytics = new Segment.Analytics({ writeKey: SEGMENT_WRITE_KEY });
analytics.identify({
  userId: vscode.env.machineId,
  //   traits: {
  //     name: "Michael Bolton",
  //     email: "mbolton@example.com",
  //     createdAt: new Date("2014-06-14T02:00:19.467Z"),
  //   },
});

// Enum of telemetry events
export enum TelemetryEvent {
  // User has started a debug session
  DebugSessionStarted = "DebugSessionStarted",
  // User has stopped a debug session
  DebugSessionStopped = "DebugSessionStopped",
  // Extension has been activated
  ExtensionActivated = "ExtensionActivated",
  // Suggestion has been accepted
  SuggestionAccepted = "SuggestionAccepted",
  // Suggestion has been rejected
  SuggestionRejected = "SuggestionRejected",
  // Queried universal prompt
  UniversalPromptQuery = "UniversalPromptQuery",
}

export function sendTelemetryEvent(
  event: TelemetryEvent,
  properties?: Record<string, any>
) {
  if (!vscode.env.isTelemetryEnabled) return;

  analytics.track({
    event,
    userId: vscode.env.machineId,
    properties,
  });
}
