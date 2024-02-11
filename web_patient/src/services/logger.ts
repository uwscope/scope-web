export const logError = (component: string, error: string) => {
  console.error(`Error in ${component}: ${error}`);
};

export const logException = (component: string, exception: Error) => {
  console.error(`Exception in ${component}: ${exception}`);
};
