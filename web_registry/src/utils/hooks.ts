import React, { RefObject } from "react";

import debounce from "lodash.debounce";

export const useResize = (elementRef: RefObject<HTMLElement>) => {
  const [size, setSize] = React.useState([0, 0]);
  const debounceSetSize = debounce(setSize, 500);

  const updateSize = React.useCallback(() => {
    if (elementRef && elementRef.current) {
      const { width, height } = elementRef.current.getBoundingClientRect();
      debounceSetSize([width, height]);
    }
  }, [elementRef]);

  React.useEffect(() => {
    updateSize();
    window.addEventListener("resize", updateSize);
    return () => {
      window.removeEventListener("resize", updateSize);
    };
  }, [updateSize]);

  const [width, height] = size;
  return { width, height };
};
