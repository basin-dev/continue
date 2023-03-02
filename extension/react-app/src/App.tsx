import DebugPanel from "./components/DebugPanel";
import MainTab from "./tabs/main";
import { Provider } from "react-redux";
import store from "../redux/store";
import WelcomeTab from "./tabs/welcome";

function App() {
  return (
    <>
      <Provider store={store}>
        <DebugPanel
          tabs={[
            { element: <MainTab />, title: "Debug Panel" },
            { element: <WelcomeTab />, title: "Welcome to Continue" },
          ]}
        ></DebugPanel>
      </Provider>
    </>
  );
}

export default App;
