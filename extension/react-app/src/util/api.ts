import { Configuration, DebugApi, UnittestApi } from "../../../src/client";
import { useSelector } from "react-redux";
import { useEffect, useState } from "react";
import { RootStore } from "../redux/store";

export function useApi() {
  const apiUrl = useSelector((state: RootStore) => state.config.apiUrl);
  const vscMachineId = useSelector(
    (state: RootStore) => state.config.vscMachineId
  );
  const [debugApi, setDebugApi] = useState<DebugApi>();
  const [unittestApi, setUnittestApi] = useState<UnittestApi>();

  useEffect(() => {
    if (apiUrl && vscMachineId) {
      let config = new Configuration({
        basePath: apiUrl,
        middleware: [
          {
            pre: async (context) => {
              context.init.headers = {
                ...context.init.headers,
                "x-vsc-machine-code": vscMachineId,
              };
            },
          },
        ],
      });
      setDebugApi(new DebugApi(config));
      setUnittestApi(new UnittestApi(config));
    }
  }, [apiUrl, vscMachineId]);

  return { debugApi, unittestApi };
}
