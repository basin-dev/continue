import { Configuration, DebugApi, UnittestApi } from "../../../src/client";
import { useSelector } from "react-redux";
import { useEffect, useState } from "react";

export function useApi() {
  const apiUrl = useSelector((state: any) => state.apiUrl);
  const vscMachineId = useSelector((state: any) => state.vscMachineId);
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
