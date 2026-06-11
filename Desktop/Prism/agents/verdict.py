from utils.signals import extract_signals
from utils.scoring import calculate_score, get_verdict_label
from utils.summary import generate_summary

def run(agent_outputs: dict, job_data: dict) -> dict:
    # Step 1 — extract signals
    signals = extract_signals(agent_outputs)

    # Step 2 — calculate score
    ghost_score = calculate_score(signals)

    # Step 3 — get verdict label
    verdict = get_verdict_label(ghost_score)

    # Step 4 — generate summary
    summary = generate_summary(signals, ghost_score, job_data)

    # Step 5 — overall confidence
    agent_confidences = [
        agent_outputs.get("agent1", {}).get("confidence", 0),
        agent_outputs.get("agent2", {}).get("confidence", 0),
        agent_outputs.get("agent3", {}).get("confidence", 0),
        agent_outputs.get("agent4", {}).get("confidence", 0)
    ]
    active_agents = [c for c in agent_confidences if c > 0]
    overall_confidence = round(
        sum(active_agents) / max(len(active_agents), 1), 2
    )

    return {
        "status": "success",
        "ghost_probability": ghost_score,
        "verdict": verdict,
        "summary": summary,
        "signals": signals,
        "overall_confidence": overall_confidence,
        "agents_used": len(active_agents)
    }