import { useState } from "react";

function useArrayState<T>(initialValue: T[]) {
  const [value, setValue] = useState(initialValue);

  function add(item: any) {
    setValue((prev) => [...prev, item]);
  }

  function remove(index: number) {
    setValue((prev) => prev.filter((_, i) => i !== index));
  }

  function edit(editFn: (prev: T[]) => T[]) {
    setValue((prev) => editFn(prev));
  }

  return { value, add, remove, edit };
}

export default useArrayState;
