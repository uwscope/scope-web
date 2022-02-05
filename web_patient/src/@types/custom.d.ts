declare module '*.png' {
    const content: any;
    export default content;
}

declare module '*.jpeg' {
    const content: any;
    export default content;
}

// NodeJS overrides
declare function setTimeout(callback: () => void, ms: number): number;
declare function clearTimeout(timeoutId: number): void;

// Expected client configuration
declare var CLIENT_CONFIG: {
    flaskBaseUrl: string;
};
