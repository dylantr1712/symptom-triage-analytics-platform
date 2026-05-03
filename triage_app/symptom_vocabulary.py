SUPPORTED_SYMPTOMS = {
    "abdominal_pain",
    "chest_pain",
    "confusion",
    "cough",
    "fever",
    "headache",
    "heavy_bleeding",
    "loss_of_consciousness",
    "nausea",
    "runny_nose",
    "seizure",
    "shortness_of_breath",
    "sore_throat",
    "vomiting",
    "worsening_symptoms",
}

SYMPTOM_ALIASES = {
    "breathless": "shortness_of_breath",
    "short_of_breath": "shortness_of_breath",
    "trouble_breathing": "shortness_of_breath",
    "hard_to_breathe": "shortness_of_breath",
    "tight_chest": "chest_pain",
    "chest_tightness": "chest_pain",
    "throwing_up": "vomiting",
    "temperature": "fever",
    "high_temperature": "fever",
}

LOW_RISK_SYMPTOMS = {
    "cough",
    "headache",
    "nausea",
    "runny_nose",
    "sore_throat",
}

SEVERE_CUE_KEYWORDS = {
    "severe",
    "worst",
    "unbearable",
    "tight chest",
    "hard to breathe",
    "cannot breathe",
    "can't breathe",
    "confused",
    "passing out",
}

MODERATE_CUE_KEYWORDS = {
    "moderate",
    "getting worse",
    "hard to manage",
    "interferes with sleep",
    "interferes with work",
    "persistent",
}
