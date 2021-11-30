import { action, computed, makeAutoObservable } from 'mobx';
import { defaultAppConfig } from 'src/services/configs';
import { PromiseQuery, PromiseState } from 'src/services/promiseQuery';
import { useServices } from 'src/services/services';
import { IAppConfig, IAssessmentContent, ILifeAreaContent, IUser } from 'src/services/types';
import { AuthStore, IAuthStore } from 'src/stores/AuthStore';
import { IPatientStore, PatientStore } from 'src/stores/PatientStore';

export interface IRootStore {
    // Stores
    patientStore: IPatientStore;
    authStore: IAuthStore;

    // App metadata
    appTitle: string;
    appConfig: IAppConfig;

    // UI states
    loadState: PromiseState;
    loginState: PromiseState;
    inspirationalQuote: string;

    // Helpers
    getAssessmentContent: (assessmentId: string) => IAssessmentContent | undefined;
    getLifeAreaContent: (lifearea: string) => ILifeAreaContent | undefined;

    // Data load/save
    load: () => void;
}

export type NavigationPath = 'home' | 'careplan' | 'progress' | 'profile';

export class RootStore implements IRootStore {
    // Stores
    public patientStore: IPatientStore;
    public authStore: IAuthStore;

    // App metadata
    public appTitle = 'SCOPE for Patients';

    // UI states

    // Promise queries
    private readonly loginQuery: PromiseQuery<IUser | undefined>;
    private readonly configQuery: PromiseQuery<IAppConfig>;
    private readonly quoteQuery: PromiseQuery<string>;
    private readonly loadQuery: PromiseQuery<PromiseSettledResult<void>[]>;

    constructor() {
        this.patientStore = new PatientStore();
        this.authStore = new AuthStore();

        this.loginQuery = new PromiseQuery(undefined, 'loginQuery');
        this.configQuery = new PromiseQuery(defaultAppConfig, 'configQuery');
        this.quoteQuery = new PromiseQuery('', 'quoteQuery');
        this.loadQuery = new PromiseQuery([], 'loadQuery');

        makeAutoObservable(this);
    }

    @computed
    public get loginState() {
        return this.loginQuery.state;
    }

    @computed
    public get loadState() {
        if (this.loadQuery.state == 'Pending') {
            return this.loadQuery.state;
        } else {
            return this.patientStore.loadState;
        }
    }

    @computed
    public get appConfig() {
        return this.configQuery.value || defaultAppConfig;
    }

    @computed
    public get inspirationalQuote() {
        return this.quoteQuery.value || '';
    }

    @action.bound
    public getAssessmentContent(assessmentId: string) {
        return this.appConfig.assessments.find((s) => s.name.toLowerCase() == assessmentId.toLowerCase());
    }

    @action.bound
    public getLifeAreaContent(lifearea: string) {
        return this.appConfig.lifeAreas.find((la) => la.id == lifearea);
    }

    @action.bound
    public async load() {
        await this.loadQuery.fromPromise(
            Promise.allSettled([this.loadAppConfig(), this.loadQuotes(), this.patientStore.load()])
        );
    }

    @action.bound
    public async loadAppConfig() {
        const { appService } = useServices();
        const promise = appService.getAppConfig();
        await this.configQuery.fromPromise(promise);
    }

    @action.bound
    public async loadQuotes() {
        const { appService } = useServices();
        const promise = appService.getInspirationalQuote();
        await this.quoteQuery.fromPromise(promise);
    }
}
