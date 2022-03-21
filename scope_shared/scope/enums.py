from enum import Enum


class ActivitySuccessType(Enum):
    Yes = "Yes"
    SomethingElse = "SomethingElse"
    No = "No"


class ClinicCode(Enum):
    Breast = "Breast"
    Endocrine = "Endocrine"
    GI = "GI"
    GIPancreatic = "GI – Pancreatic"
    GU = "GU"
    GYN = "GYN"
    HEME = "HEME"
    HEMESickleCell = "HEME – Sickle Cell"
    HNL = "HNL"
    Immunotherapy = "Immunotherapy"
    MelanomaRenal = "Melanoma/Renal"
    Neuro = "Neuro"
    Sarcoma = "Sarcoma"
    TransplantAuto = "Transplant – Auto"
    TransplantAllo = "Transplant – Allo"
    TransplantCART = "Transplant – CAR-T"
    TransplantLTFU = "Transplant – LTFU"
    TransplantTTC = "Transplant – TTC"
    Other = "Other"


class PatientSex(Enum):
    Male = "Male"
    Female = "Female"
    Intersex = "Intersex"


class PatientGender(Enum):
    Male = "Male"
    Female = "Female"
    Transgender = "Transgender"
    NonBinary = "Non-binary/Non-conforming"
    Other = "Other"


class PatientRace(Enum):
    Native = "American Indian or Alaska Native"
    Asian = "Asian or Asian American"
    Black = "Black or African American"
    Pacific = "Native Hawaiian or Other Pacific Islander"
    White = "White"
    Unknown = "Unknown"


class PatientEthnicity(Enum):
    Hispanic = "Hispanic or Latino/Latina/Latinx"
    NotHispanic = "Not Hispanic or Latino/Latina/Latinx"
    Unknown = "Unknown"


class PatientPronoun(Enum):
    HeHim = "He/Him"
    SheHer = "She/Her"
    TheyThem = "They/Them"


class DepressionTreatmentStatus(Enum):
    CoCM = "CoCM"
    CoCMRelapse = "CoCM RP"
    Discharged = "D/C"
    Other = "Other"
    End = "End"


class FollowupSchedule(Enum):
    OneWeek = "1-week follow-up"
    TwoWeeks = "2-week follow-up"
    ThreeWeeks = "3-week follow-up"
    FourWeeks = "4-week follow-up"
    SixWeeks = "6-week follow-up"
    EightWeeks = "8-week follow-up"


class DiscussionFlag(Enum):
    SafetyRisk = "Flag as safety risk"
    Discussion = "Flag for discussion"


class CancerTreatmentRegimen(Enum):
    Surgery = "Surgery"
    Chemotherapy = "Chemotherapy"
    Radiation = "Radiation"
    StemCellTransplant = "Stem Cell Transplant"
    Immunotherapy = "Immunotherapy"
    CART = "CAR-T"
    Endocrine = "Endocrine"
    Surveillance = "Surveillance"
    Other = "Other"


class ProviderRole(Enum):
    SocialWorker = "socialWorker"
    Psychiatrist = "psychiatrist"
    StudyStaff = "studyStaff"


class Referral(Enum):
    Psychiatry = "Psychiatry"
    Psychology = "Psychology"
    PatienttNavigation = "Patient Navigation"
    IntegrativeMedicine = "Integrative Medicine"
    SpiritualCare = "Spiritual Care"
    PalliativeCare = "Palliative Care"
    Other = "Other"


class ReferralStatus(Enum):
    NotReferral = "Not Referred"
    Pending = "Pending"
    Active = "Active"
    Completed = "Completed"


class SessionType(Enum):
    InPerson = "In person"
    Telehealth = "Telehealth"
    Phone = "Phone"
    Group = "Group"
    Home = "Home"


class TreatmentPlan(Enum):
    MaintainPlan = "Maintain current treatment"
    AdjustPlan = "Adjust treatment plan"
    MonitorOnly = "Monitor only"
    NoFollowup = "No further follow-up"
    ReferToCommunity = "Refer to community"


class TreatmentChange(Enum):
    NoChange = "None"
    Medication = "Medication"
    Counseling = "Counseling"


class BehavioralActivationChecklist(Enum):
    ReviewModel = "Review of the BA model"
    ValuesGoals = "Values and goals assessment"
    ActivityScheduling = "Activity scheduling"
    MoodActivityMonitoring = "Mood and activity monitoring"
    Relaxation = "Relaxation"
    PositiveReinforcement = "Positive reinforcement"
    ManagingAvoidance = "Managing avoidance behaviors"
    ProblemSolving = "Problem-solving"


class BehavioralStrategyChecklist(Enum):
    BehavioralActivation = "Behavioral Activation"
    MotivationalInterviewing = "Motivational Interviewing"
    ProblemSolvingTherapy = "Problem Solving Therapy"
    CognitiveTherapy = "Cognitive Therapy"
    MindfulnessStrategies = "Mindfulness Strategies"
    SupportiveTherapy = "Supportive Therapy"
    Other = "Other"


class AssessmentType(Enum):
    PHQ9 = "phq-9"
    GAD7 = "gad-7"
    MoodLogging = "mood"
    Medication = "medication"


class ScheduledItemFrequency(Enum):
    Daily = "Daily"
    Weekly = "Once a week"
    Biweekly = "Every 2 weeks"
    Monthly = "Every 4 weeks"


class DayOfWeek(Enum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    Sunday = "Sunday"


class DueType(Enum):
    Exact = "Exact"
    ChunkOfDay = "ChunkOfDay"
    Day = "Day"
    Week = "Week"


class Site(Enum):
    SCCASLU = "SCCA – SLU"
    SCCAUWNW = "SCCA – UW-NW"
    SCCAPEN = "SCCA – PEN"
    MultiCareTacoma = "MultiCare – Tacoma"
    MultiCareGigHarbor = "MultiCare – Gig Harbor"
