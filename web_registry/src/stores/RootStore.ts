import { action, makeAutoObservable } from 'mobx';
import { IAppConfig, IAppContentConfig, IAssessmentContent } from 'shared/types';
import { AuthStore, IAuthStore } from 'src/stores/AuthStore';
import { IPatientsStore, PatientsStore } from 'src/stores/PatientsStore';

export interface IRootStore {
    // Stores
    patientsStore: IPatientsStore;
    authStore: IAuthStore;

    // App metadata
    appTitle: string;
    appContentConfig: IAppContentConfig;

    // Helpers
    getAssessmentContent: (assessmentId: string) => IAssessmentContent | undefined;
    reset: () => void;
}

export class RootStore implements IRootStore {
    // Stores
    public patientsStore: IPatientsStore;
    public authStore: IAuthStore;

    // App metadata
    public appTitle = 'SCOPE Registry';
    public appContentConfig: IAppContentConfig;

    constructor(serverConfig: IAppConfig) {
        this.appContentConfig = serverConfig.content;
        this.patientsStore = new PatientsStore();
        this.authStore = new AuthStore(serverConfig.auth);

        makeAutoObservable(this);
    }

    @action.bound
    public getAssessmentContent(assessmentId: string) {
        return this.appContentConfig.assessments.find((s) => s.id.toLowerCase() == assessmentId.toLowerCase());
    }

    @action.bound
    public reset() {
        this.patientsStore = new PatientsStore();
    }
}
