import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootStore } from "./store";
import { selectDebugContextValue } from "./selectors/debugContextSelectors";
import { updateValue } from "./slices/debugContexSlice";

function useReduxState(
  selector: (state: RootStore, ...args: any[]) => any,
  action: any
): [any, (value: any) => void] {
  const dispatch = useDispatch();
  const state = useSelector(selector);
  const boundAction = useCallback(
    (...args: any[]) => dispatch(action(...args)),
    [dispatch, action]
  );
  return [state, boundAction];
}

export function useDebugContextValue(
  key: string,
  defaultValue: any
): [any, (value: any) => void] {
  const dispatch = useDispatch();
  const state =
    useSelector((state: RootStore) => selectDebugContextValue(state, key)) ||
    defaultValue;
  const boundAction = useCallback(
    (value: any) => dispatch(updateValue({ key, value })),
    [dispatch, key]
  );
  return [state, boundAction];
}
