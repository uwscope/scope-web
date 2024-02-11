import React, { FunctionComponent } from "react";

import styled from "styled-components";

const Container = styled.div<{ disabled: boolean }>((props) => ({
  opacity: props.disabled ? 0.2 : 1,
  pointerEvents: props.disabled ? "none" : "inherit",
}));

export interface IDisableProps {
  disabled: boolean;
}

export const Disable: FunctionComponent<IDisableProps> = (props) => {
  const { disabled = false, children } = props;

  return <Container disabled={disabled}>{children}</Container>;
};

export default Disable;
