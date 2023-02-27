import React from "react";
import { H3, TextArea } from "../components";

function AdditionalContextTab() {
  return (
    <>
      <H3>Additional Context</H3>
      <TextArea
        rows={8}
        placeholder="Copy and paste information related to the bug from GitHub Issues, Slack threads, or other notes here."
        className="additionalContextTextarea"
      ></TextArea>
      <br></br>
    </>
  );
}

export default AdditionalContextTab;
