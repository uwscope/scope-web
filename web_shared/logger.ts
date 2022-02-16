import { isDev } from 'shared/env';

type TelemetryLog<T> = { eventName: string; getLog?: (error?: Error, result?: T) => LogData };

export type LogData = { [key in string]: string | number | boolean };

export interface ILogger {
    // For tracing
    debug(message: string, data?: LogData): void;
    error(error: Error, data?: LogData): void;
    // For telemetry
    assert(condition: boolean, message: string): void;
    event(name: string, data?: LogData): void;
    startEvent(name: string): void;
    endEvent(name: string, failed: boolean, data?: LogData): void;
    logFunction: <T = void>(logs: TelemetryLog<T>) => (fn: () => Promise<T>) => Promise<T>;
}

export const getLogger = (logSource: string): ILogger => {
    const buildMessage = (message: string) => `${logSource}: ${message}`;

    const convertToProperties = (data?: LogData) => {
        const propData = data || {};
        return Object.keys(propData).reduce(
            (total, key) => {
                total[key] = `${propData[key]}`;
                return total;
            },
            <LogData>{ logSource },
        );
    };

    const logError = (error: Error, data?: LogData, handledAt?: string) => {
        if (!!data && !!handledAt) {
            data['handledAt'] = handledAt;
        }

        const properties = convertToProperties(data);

        // TODO: send data to telemetry

        if (isDev) {
            console.error(error, properties);
        }
    };

    const startEvent = (name: string) => {
        // TODO: send data to telemetry

        if (isDev) {
            name = buildMessage(name);
            console.log(`Event start: ${name}`);
        }
    };

    const endEvent = (name: string, failed: boolean, data?: LogData) => {
        let properties = convertToProperties(data);

        if (failed) {
            properties = { ...properties, ...{ failed: failed.toString() } };
        }

        // TODO: send data to telemetry

        if (isDev) {
            name = buildMessage(name);
            console.log(`Event end: ${name}`, properties);
        }
    };

    const logFunction =
        <T>(logs: TelemetryLog<T>) =>
        async (fn: () => Promise<T>) => {
            const { eventName, getLog } = logs;

            try {
                startEvent(eventName);
                const result = await fn();
                const successLog = getLog && getLog(undefined, result);
                endEvent(eventName, false, successLog);
                return result;
            } catch (error) {
                const errorInstance = error instanceof Error ? error : new Error(`${error}`);
                const failureLog = getLog && getLog(errorInstance, undefined);
                logError(errorInstance, failureLog);
                endEvent(eventName, true, failureLog);
                throw error;
            }
        };

    const debug = (message: string, data?: LogData) => {
        if (isDev) {
            if (data) {
                console.debug(buildMessage(message), data);
            } else {
                console.debug(buildMessage(message));
            }
        }
    };

    const event = (name: string, data?: LogData) => {
        const properties = convertToProperties(data);

        // TODO: send data to telemetry

        if (isDev) {
            name = buildMessage(name);
            console.log(`Event: ${name}`, properties);
        }
    };

    const assert = (condition: boolean, message: string) => {
        if (!condition) {
            logError(new Error(message));
        }
    };

    return {
        debug,
        error: logError,
        event,
        startEvent,
        endEvent,
        logFunction,
        assert,
    };
};
