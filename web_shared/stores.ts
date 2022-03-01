import { when } from 'mobx';
import { ILogger } from 'shared/logger';
import { PromiseQuery } from 'shared/promiseQuery';

export const getLoadAndLogQuery =
    (logger: ILogger, bindArg?: unknown) =>
    async <T>(queryCall: () => Promise<T>, promiseQuery: PromiseQuery<T>, onConflict?: (responseData?: any) => T) => {
        const effect = async () => {
            const loggedCall = logger.logFunction<T>({ eventName: promiseQuery.name })(queryCall.bind(bindArg));
            await promiseQuery.fromPromise(loggedCall, onConflict);
        };

        if (promiseQuery.state == 'Pending') {
            when(
                () => {
                    return promiseQuery.state != 'Pending';
                },
                async () => {
                    await effect();
                },
            );
        } else {
            await effect();
        }
    };



export const onSingletonConflict =
    (fieldName: string) =>
    <T>(responseData?: any) => {
        return responseData?.[fieldName] as T;
    };

export const onArrayConflict =
    <T>(itemName: string, idName: string, getArray: () => T[], logger: ILogger) =>
    (responseData: any | undefined) => {
        const updatedLog = responseData?.[itemName];
        if (!!updatedLog) {
            const array = getArray();
            const existing = array.find((l) => (l as any)[idName] == updatedLog[idName]);
            logger.assert(!!existing, 'Log not found when expected');

            if (!!existing) {
                Object.assign(existing, updatedLog);
                return array;
            } else {
                return array.slice().concat([updatedLog]);
            }
        }

        return getArray();
    };
