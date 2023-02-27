import DebugPanel from "./components/DebugPanel";
import MainTab from "./tabs/main";
import AdditionalContextTab from "./tabs/additionalContext";
import { Provider } from "react-redux";
import store from "../redux/store";

function App() {
  return (
    <>
      <Provider store={store}>
        <DebugPanel
          tabs={[
            { element: <MainTab />, title: "Debug Panel" },
            { element: <AdditionalContextTab />, title: "Additional Context" },
          ]}
        ></DebugPanel>
      </Provider>
    </>
  );
}

export default App;
