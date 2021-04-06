from enum import Enum


class ClinicCode(Enum):
    Breast = "Breast"
    Endocrine = ("Endocrine",)
    GI = ("GI",)
    GIPancreatic = ("GI – Pancreatic",)
    GU = ("GU",)
    GYN = ("GYN",)
    HEME = ("HEME",)
    HEMESickleCell = ("HEME – Sickle Cell",)
    HNL = ("HNL",)
    Immunotherapy = ("Immunotherapy",)
    MelanomaRenal = ("Melanoma/Renal",)
    Neuro = ("Neuro",)
    NWHospital = ("NW Hospital",)
    Sarcoma = ("Sarcoma",)
    TransplantAuto = ("Transplant – Auto",)
    TransplantAllo = ("Transplant – Allo",)
    TransplantCART = ("Transplant – CAR-T",)
    TransplantLTFU = ("Transplant – LTFU",)
    TransplantTTC = ("Transplant – TTC",)


class PatientSex(Enum):
    Male = "Male"
    Female = "Female"


class DepressionTreatmentStatus(Enum):
    CoCM = "CoCM"
    CoCMRelapse = "CoCM Relapse Prevention"
    Discharged = "Discharged"
    Pending = "Pending"


class FollowupSchedule(Enum):
    OneWeek = "1-week follow-up"
    TwoWeeks = "2-week follow-up"
    FourWeeks = "4-week follow-up"


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


class Referral(Enum):
    NoReferral = "None"
    Psychiatry = "Psychiatry"
    Psychology = "Psychology"
    PtNavigation = "Pt Navigation"
    IntegrativeMedicine = "Integrative Medicine"
    SpiritualCare = "Spiritual Care"
    PalliativeCare = "Palliative Care"


class SessionType(Enum):
    InPerson = "In person at clinic"
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
    ContingencyManagement = "Contingency management"
    ManagingAvoidance = "Managing avoidance behaviors"
    ProblemSolving = "Problem-solving"


class AssessmentType(Enum):
    PHQ9 = "PHQ-9"
    GAD7 = "GAD-7"
    MoodLogging = "Mood Logging"


class AssessmentFrequency(Enum):
    Daily = "Daily"
    Weekly = "Once a week"
    Biweekly = "Every 2 weeks"
    Monthly = "Monthly"
