SEVERITY_WEIGHTS = {
    "critical": 30,
    "high": 20,
    "medium": 10
}

def calculate_score(signals: list) -> int:
    if not signals:
        return 0
    
    raw_score = sum(SEVERITY_WEIGHTS.get(s["severity"], 0) for s in signals)
    return min(raw_score, 100)

def get_verdict_label(score: int) -> str:
    if score >= 70:
        return "GHOST"
    elif score >= 40:
        return "SUSPICIOUS"
    else:
        return "LEGITIMATE"