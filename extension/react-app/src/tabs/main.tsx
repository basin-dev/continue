import React from "react";

function MainTab() {
  return (
    <>
      <h1>Debug Panel</h1>

      <h3>Code Sections</h3>
      <div className="multiselectContainer"></div>

      <h3>Bug Description</h3>
      <textarea
        id="bugDescription"
        name="bugDescription"
        className="bugDescription"
        rows={4}
        cols={50}
        placeholder="Describe your bug..."
      ></textarea>

      <h3>Stack Trace</h3>
      <textarea
        id="traceback"
        className="traceback"
        name="traceback"
        rows={4}
        cols={50}
        placeholder="Paste stack trace here"
      ></textarea>

      <select
        hidden
        id="relevantVars"
        className="relevantVars"
        name="relevantVars"
      ></select>

      <div className="buttonDiv">
        <button className="explainCodeButton">Explain Code</button>
        <button className="listTenThingsButton">Generate Ideas</button>
        <button disabled className="makeEditButton">
          Suggest Fix
        </button>
        <button disabled className="generateUnitTestButton">
          Create Test
        </button>
      </div>
      <div className="loader makeEditLoader" hidden></div>

      <pre className="fixSuggestion answer" hidden></pre>

      <br></br>
    </>
  );
}

export default MainTab;
