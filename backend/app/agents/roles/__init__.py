from app.agents.roles.assessment_assistant import ASSESSMENT_ASSISTANT_CONFIG
from app.agents.roles.competition_advisor import COMPETITION_ADVISOR_CONFIG
from app.agents.roles.instructor_assistant import INSTRUCTOR_ASSISTANT_CONFIG
from app.agents.roles.project_coach import PROJECT_COACH_CONFIG
from app.agents.roles.student_tutor import STUDENT_TUTOR_CONFIG
from app.agents.roles.profile_evaluator import PROFILE_EVALUATOR_CONFIG

ROLE_CONFIG_REGISTRY = {
    "student_tutor": STUDENT_TUTOR_CONFIG,
    "project_coach": PROJECT_COACH_CONFIG,
    "competition_advisor": COMPETITION_ADVISOR_CONFIG,
    "instructor_assistant": INSTRUCTOR_ASSISTANT_CONFIG,
    "assessment_assistant": ASSESSMENT_ASSISTANT_CONFIG,
    "profile_evaluator": PROFILE_EVALUATOR_CONFIG,
}

MODE_TO_ROLE_ID = {
    "learning": "student_tutor",
    "project": "project_coach",
    "competition": "competition_advisor",
    "instructor": "instructor_assistant",
    "teacher": "instructor_assistant",
    "assessment": "assessment_assistant",
    "grading": "assessment_assistant",
    "profile_evaluator": "profile_evaluator",
}