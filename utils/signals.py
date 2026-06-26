def extract_signals(agent_outputs: dict) -> list:
    signals = []

    a1 = agent_outputs.get("agent1", {})
    a2 = agent_outputs.get("agent2", {})
    a3 = agent_outputs.get("agent3", {})
    a4 = agent_outputs.get("agent4", {})

    # ── Agent 1 — Age Detective ──────────────────────────
    if a1.get("confidence", 0) > 0.4:
        if a1.get("manipulation_detected"):
            age = a1.get("real_age_days", 0)
            if age > 90:
                severity = "critical"
            elif age > 60:
                severity = "high"
            else:
                severity = "medium"

            signals.append({
                "signal": "date_manipulation",
                "severity": severity,
                "detail": f"Job is {age} days old but displayed as {a1.get('displayed_age_days', 0)} days old",
                "agent": "age_detective"
            })

        if a1.get("repost_count", 0) >= 2:
            signals.append({
                "signal": "multiple_reposts",
                "severity": "high",
                "detail": f"Job reposted {a1['repost_count']} times across platforms",
                "agent": "age_detective"
            })

    # ── Agent 2 — Clone Detector ─────────────────────────
    if a2.get("confidence", 0) > 0.4:
        if a2.get("clone_detected"):
            changes = a2.get("changes_detected", [])
            if changes:
                severity = "critical"
            else:
                severity = "high"

            signals.append({
                "signal": "clone_detected",
                "severity": severity,
                "detail": "Same JD found on multiple platforms with different dates",
                "agent": "clone_detector"
            })

            for change in changes:
                signals.append({
                    "signal": "suspicious_change",
                    "severity": "medium",
                    "detail": change,
                    "agent": "clone_detector"
                })

    # ── Agent 3 — Company Investigator ───────────────────
    if a3.get("confidence", 0) > 0.4:
        reg = a3.get("registration", {})
        hiring = a3.get("hiring_history", {})
        founder = a3.get("founder_credibility")

        if reg.get("registration_status") == "Struck Off":
            signals.append({
                "signal": "company_struck_off",
                "severity": "critical",
                "detail": "Company registration has been struck off",
                "agent": "company_investigator"
            })

        if not hiring.get("hiring_history_found"):
            # determine company age
            import dateparser
            from datetime import datetime
            inc_date = reg.get("incorporation_date")
            company_age_years = 0
            if inc_date:
                parsed = dateparser.parse(inc_date)
                if parsed:
                    company_age_years = (datetime.now() - parsed.replace(tzinfo=None)).days / 365

            severity = "high" if company_age_years > 2 else "medium"
            signals.append({
                "signal": "no_hiring_history",
                "severity": severity,
                "detail": "No verifiable hiring history found on any platform",
                "agent": "company_investigator"
            })

        elif hiring.get("intern_reviews", 0) == 0:
            signals.append({
                "signal": "no_intern_reviews",
                "severity": "medium",
                "detail": "No intern reviews found on AmbitionBox or Glassdoor",
                "agent": "company_investigator"
            })

        for flag in hiring.get("red_flags", []):
            signals.append({
                "signal": "hiring_red_flag",
                "severity": "medium",
                "detail": flag,
                "agent": "company_investigator"
            })

        if founder and founder.get("credibility_score", 10) < 4:
            signals.append({
                "signal": "low_founder_credibility",
                "severity": "high",
                "detail": f"Founder credibility score: {founder['credibility_score']}/10",
                "agent": "company_investigator"
            })


    return signals