import re

RULES = {
    "UNSUBSCRIBE": [
        r"unsubscribe",
        r"remove me",
        r"stop sending",
        r"no longer work",
        r"left the company",
        r"wrong contact"
    ],
    "COMPLAINT": [
        r"spam",
        r"too many emails",
        r"complaint"
    ],
    "ENGAGED": [
        r"share rates",
        r"let'?s discuss",
        r"call me",
        r"we have shipments",
        r"next week"
    ],
    "NOT_RELEVANT_NOW": [
        r"no shipments",
        r"not applicable",
        r"nothing planned"
    ],
    "ACKNOWLEDGED": [
        r"thanks",
        r"noted",
        r"received",
        r"ok"
    ],
    "AUTO_REPLY": [
        r"out of office",
        r"auto[- ]reply",
        r"on leave"
    ]
}

PRIORITY = [
    "UNSUBSCRIBE",
    "COMPLAINT",
    "AUTO_REPLY",
    "ENGAGED",
    "NOT_RELEVANT_NOW",
    "ACKNOWLEDGED"
]

def categorize_reply(text: str):
    text = text.lower()

    for category in PRIORITY:
        for pattern in RULES[category]:
            if re.search(pattern, text):
                return category

    return "ACKNOWLEDGED"
