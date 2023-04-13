import DebugPanel from "./components/DebugPanel";
import MainTab from "./tabs/main";
import { Provider } from "react-redux";
import store from "./redux/store";
import WelcomeTab from "./tabs/welcome";
import ChatTab from "./tabs/chat";
import Notebook from "./tabs/notebook";

function App() {
  return (
    <>
      <Provider store={store}>
        {/* <Notebook apiBaseUrl="http://localhost:8000" /> */}
        <DebugPanel
          tabs={[
            {
              element: <Notebook apiBaseUrl="http://localhost:8000" />,
              title: "Notebook",
            },
            // { element: <MainTab />, title: "Debug Panel" },
            // { element: <WelcomeTab />, title: "Welcome" },
            // { element: <ChatTab />, title: "Chat" },
          ]}
        ></DebugPanel>
      </Provider>
    </>
  );
}

export default App;
