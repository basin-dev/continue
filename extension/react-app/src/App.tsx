import DebugPanel from "../components/DebugPanel";
import MainTab from "./tabs/main";
import AdditionalContextTab from "./tabs/additionalContext";

function App() {
  return (
    <>
      <DebugPanel
        tabs={[
          { element: <MainTab />, title: "Debug Panel" },
          { element: <AdditionalContextTab />, title: "Additional Context" },
        ]}
      ></DebugPanel>
    </>
  );
}

export default App;
