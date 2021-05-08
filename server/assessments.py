phq9Assessment = {
    "name": "PHQ-9",
    "instruction": "Over the last 2 weeks, how often have you been bothered by any of the following problems?",
    "questions": [
        {"question": "Little interest or pleasure in doing things", "id": "Interest"},
        {"question": "Feeling down, depressed, or hopeless", "id": "Mood"},
        {
            "question": "Trouble falling or staying asleep, or sleeping too much",
            "id": "Sleep",
        },
        {"question": "Feeling tired or having little energy", "id": "Energy"},
        {"question": "Poor appetite or overeating", "id": "Apetite"},
        {
            "question": "Feeling bad about yourself or that you are a failure or have let yourself or your family down",
            "id": "Guilt",
        },
        {
            "question": "Trouble concentrating on things, such as reading the newspaper or watching television",
            "id": "Concentration",
        },
        {
            "question": "Moving or speaking so slowly that other people could have noticed. Or the opposite being so figety or restless that you have been moving around a lot more than usual",
            "id": "Motor",
        },
        {
            "question": "Thoughts that you would be better off dead, or of hurting yourself",
            "id": "Suicidality",
        },
    ],
    "options": [
        {
            "text": "Not at all",
            "value": 0,
        },
        {
            "text": "Several days",
            "value": 1,
        },
        {
            "text": "More than half the days",
            "value": 2,
        },
        {
            "text": "Nearly every day",
            "value": 3,
        },
    ],
}

gad7Assessment = {
    "name": "GAD-7",
    "instruction": "Over the last 2 weeks, how often have you been bothered by any of the following problems?",
    "questions": [
        {"question": "Feeling nervous, anxious or on edge", "id": "Anxious"},
        {
            "question": "Not being able to stop or control worrying",
            "id": "Constant worrying",
        },
        {
            "question": "Worrying too much about different things",
            "id": "Worrying too much",
        },
        {"question": "Trouble relaxing", "id": "Trouble relaxing"},
        {
            "question": "Being so restless that it is hard to sit still",
            "id": "Restless",
        },
        {"question": "Becoming easily annoyed or irritated", "id": "Irritable"},
        {
            "question": "Feeling afraid as if something awful might happen",
            "id": "Afraid",
        },
    ],
    "options": [
        {
            "text": "Not at all",
            "value": 0,
        },
        {
            "text": "Several days",
            "value": 1,
        },
        {
            "text": "More than half the days",
            "value": 2,
        },
        {
            "text": "Nearly every day",
            "value": 3,
        },
    ],
}

moodAssessment = {
    "name": "Mood Logging",
    "questions": [{"question": "Please rate your mood", "id": "Mood"}],
    "options": [
        {
            "text": "Awful",
            "value": 1,
        },
        {
            "text": "Bad",
            "value": 2,
        },
        {
            "text": "Okay",
            "value": 3,
        },
        {
            "text": "Great",
            "value": 4,
        },
        {
            "text": "Awesome",
            "value": 5,
        },
    ],
}


def get_supported_assessments():
    return [phq9Assessment, gad7Assessment, moodAssessment]
