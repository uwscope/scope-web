import { AxiosResponse } from 'axios';
import { IServiceBase, ServiceBase } from 'shared/serviceBase';
import { IPatientListResponse } from 'shared/serviceTypes';
import { IAssessment, IAssessmentLog, ICaseReview, IPatient, ISafetyPlan, ISession } from 'shared/types';

export interface IRegistryService extends IServiceBase {
    getPatients(): Promise<IPatient[]>;
    addPatient(patient: Partial<IPatient>): Promise<IPatient>;

    updatePatientSafetyPlan(recordId: string, safetyPlan: Partial<ISafetyPlan>): Promise<IPatient>;

    getPatientSession(recordId: string, session: Partial<ISession>): Promise<ISession>;
    updatePatientSession(recordId: string, session: Partial<ISession>): Promise<ISession>;

    addPatientCaseReview(recordId: string, caseReview: Partial<ICaseReview>): Promise<ICaseReview>;
    getPatientCaseReview(recordId: string, caseReview: Partial<ICaseReview>): Promise<ICaseReview>;
    updatePatientCaseReview(recordId: string, caseReview: Partial<ICaseReview>): Promise<ICaseReview>;

    updatePatientAssessment(recordId: string, assessment: Partial<IAssessment>): Promise<IAssessment>;

    addPatientAssessmentLog(recordId: string, assessmentLog: IAssessmentLog): Promise<IAssessmentLog>;
    updatePatientAssessmentLog(recordId: string, assessmentLog: IAssessmentLog): Promise<IAssessmentLog>;
}

class RegistryService extends ServiceBase implements IRegistryService {
    // // Singletons
    // profile
    // clinicalHistory
    // valuesInventory
    // safetyPlan

    // // Arrays
    // sessions
    // caseReviews
    // assessments
    // scheduledAssessments
    // assessmentLogs
    // activities
    // scheduledActivities
    // activityLogs

    constructor(baseUrl: string) {
        super(baseUrl);
    }

    public async getPatients(): Promise<IPatient[]> {
        const response = await this.axiosInstance.get<IPatientListResponse>('/patients');
        return response.data && response.data.patients;
    }

    public async addPatient(patient: Partial<IPatient>): Promise<IPatient> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.post<IPatient, AxiosResponse<IPatient>>('/patients', patient);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return patient as IPatient;
        }
    }

    public async updatePatientSafetyPlan(recordId: string, safetyPlan: Partial<ISafetyPlan>): Promise<IPatient> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IPatient>(`/patient/${recordId}`, {
                safetyPlan,
            });
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return { safetyPlan } as IPatient;
        }
    }

    public async getPatientSession(recordId: string, session: Partial<ISession>): Promise<ISession> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<ISession>(
                `/patient/${recordId}/session/${session.sessionId}`,
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return session as ISession;
        }
    }

    public async updatePatientSession(recordId: string, session: Partial<ISession>): Promise<ISession> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<ISession>(
                `/patient/${recordId}/session/${session.sessionId}`,
                session,
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return session as ISession;
        }
    }

    public async addPatientCaseReview(recordId: string, caseReview: Partial<ICaseReview>): Promise<ICaseReview> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.post<ICaseReview>(`/patient/${recordId}/casereviews`, caseReview);
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return caseReview as ICaseReview;
        }
    }

    public async getPatientCaseReview(recordId: string, caseReview: Partial<ICaseReview>): Promise<ICaseReview> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.get<ICaseReview>(
                `/patient/${recordId}/casereview/${caseReview.caseReviewId}`,
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return caseReview as ICaseReview;
        }
    }

    public async updatePatientCaseReview(recordId: string, caseReview: Partial<ICaseReview>): Promise<ICaseReview> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<ICaseReview>(
                `/patient/${recordId}/casereview/${caseReview.caseReviewId}`,
                caseReview,
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return caseReview as ICaseReview;
        }
    }

    public async updatePatientAssessment(recordId: string, assessment: Partial<IAssessment>): Promise<IAssessment> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IAssessment>(
                `/patient/${recordId}/assessment/${assessment.assessmentId}`,
                assessment,
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return assessment as IAssessment;
        }
    }

    public async addPatientAssessmentLog(recordId: string, assessmentLog: IAssessmentLog): Promise<IAssessmentLog> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.post<IAssessmentLog>(
                `/patient/${recordId}/assessmentlogs`,
                assessmentLog,
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return assessmentLog;
        }
    }

    public async updatePatientAssessmentLog(recordId: string, assessmentLog: IAssessmentLog): Promise<IAssessmentLog> {
        // Work around since backend doesn't exist
        try {
            const response = await this.axiosInstance.put<IAssessmentLog>(
                `/patient/${recordId}/assessmentlog/${assessmentLog.logId}`,
                assessmentLog,
            );
            return response.data;
        } catch (error) {
            await new Promise((resolve) => setTimeout(() => resolve(null), 500));
            return assessmentLog;
        }
    }
}

export const getRegistryServiceInstance = (baseUrl: string) => new RegistryService(baseUrl) as IRegistryService;
