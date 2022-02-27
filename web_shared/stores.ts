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
