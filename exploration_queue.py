"""Durable, auditable queue for outward research selected by the worker.

Records model-selected topics separately from verified discoveries. A topic is
not marked verified merely because the model proposes it.
"""
from datetime import datetime, timezone


def _clean_list(value, limit=5, width=500):
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        text = str(item or "").strip()
        if text and text not in result:
            result.append(text[:width])
        if len(result) >= limit:
            break
    return result


def update_exploration_queue(state, reflection, cycle, timestamp_utc=None):
    """Persist considered topics, selected topic, and only substantiated discoveries."""
    reflection = reflection if isinstance(reflection, dict) else {}
    update = reflection.get("exploration_update", {})
    update = update if isinstance(update, dict) else {}
    prior = state.get("exploration_queue", {})
    prior = prior if isinstance(prior, dict) else {}
    topics = prior.get("topics", [])
    topics = list(topics) if isinstance(topics, list) else []

    considered = _clean_list(update.get("considered_topics"), limit=5)
    selected = str(update.get("selected_topic", "") or "").strip()[:500]
    now = timestamp_utc or datetime.now(timezone.utc).isoformat()

    for topic in considered:
        if not any(isinstance(item, dict) and item.get("topic") == topic for item in topics):
            topics.append({
                "topic": topic,
                "status": "considered",
                "first_considered_cycle": int(cycle),
                "last_updated_utc": now,
            })

    if selected:
        match = next((item for item in topics
                      if isinstance(item, dict) and item.get("topic") == selected), None)
        if match is None:
            match = {
                "topic": selected,
                "first_considered_cycle": int(cycle),
            }
            topics.append(match)
        match["status"] = "selected_pending_verification"
        match["selected_cycle"] = int(cycle)
        match["last_updated_utc"] = now

    discovery = update.get("discovery")
    if isinstance(discovery, dict) and selected:
        title = str(discovery.get("title", "") or "").strip()[:300]
        urls = _clean_list(discovery.get("source_urls"), limit=8, width=1000)
        facts = _clean_list(discovery.get("verified_facts"), limit=8, width=1000)
        # Require at least a title, one HTTPS source, and one concrete verified fact.
        https_urls = [url for url in urls if url.startswith("https://")]
        if title and https_urls and facts:
            match = next((item for item in topics
                          if isinstance(item, dict) and item.get("topic") == selected), None)
            if match is None:
                match = {"topic": selected, "first_considered_cycle": int(cycle)}
                topics.append(match)
            match.update({
                "status": "discovery_recorded",
                "discovery": {
                    "title": title,
                    "source_urls": https_urls,
                    "verified_facts": facts,
                    "why_worth_attention": str(discovery.get("why_worth_attention", "") or "")[:1200],
                    "public_benefit": str(discovery.get("public_benefit", "") or "")[:1200],
                    "risks": str(discovery.get("risks", "") or "")[:1200],
                    "follow_up": str(discovery.get("follow_up", "") or "")[:800],
                    "recorded_cycle": int(cycle),
                    "recorded_utc": now,
                    "verification_note": "Model-reported evidence; verify source URLs and facts independently before relying on them.",
                },
                "last_updated_utc": now,
            })

    state["exploration_queue"] = {
        "schema_version": 1,
        "description": "Persistent outward-research queue; model-selected topics are distinct from source-backed discovery records.",
        "topics": topics[-50:],
        "last_updated_cycle": int(cycle),
        "last_updated_utc": now,
    }
    return state["exploration_queue"]
