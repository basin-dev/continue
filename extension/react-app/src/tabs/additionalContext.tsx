import React from "react";

function AdditionalContextTab() {
  return (
    <>
      <h3>Additional Context</h3>
      <textarea
        rows={8}
        placeholder="Copy and paste information related to the bug from GitHub Issues, Slack threads, or other notes here."
        className="additionalContextTextarea"
      ></textarea>
      <br></br>
    </>
  );
}

export default AdditionalContextTab;
