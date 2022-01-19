import { trim } from 'lodash';

export const combineUrl = (baseUrl: string, path: string) => {
    return [baseUrl, path].map((s) => trim(s, '/')).join('/');
};
