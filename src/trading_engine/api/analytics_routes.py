"""
Analytics, A/B Testing, and Usability Testing Endpoints

Provides backend support for:
- Analytics event tracking
- A/B test management and analysis
- Usability session recording and analysis
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["analytics"])

# Data storage directories
DATA_DIR = Path("data/analytics")
DATA_DIR.mkdir(parents=True, exist_ok=True)

ANALYTICS_FILE = DATA_DIR / "events.jsonl"
AB_ASSIGNMENTS_FILE = DATA_DIR / "ab_assignments.jsonl"
AB_CONVERSIONS_FILE = DATA_DIR / "ab_conversions.jsonl"
AB_EVENTS_FILE = DATA_DIR / "ab_events.jsonl"
USABILITY_SESSIONS_FILE = DATA_DIR / "usability_sessions.jsonl"


# ===== Models =====


class AnalyticsEvent(BaseModel):
    """Single analytics event"""

    eventName: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    sessionId: str
    userId: str
    timestamp: int
    url: str
    pathname: str
    referrer: Optional[str] = None
    userAgent: str
    screenSize: str
    language: str


class AnalyticsBatch(BaseModel):
    """Batch of analytics events"""

    events: List[AnalyticsEvent]
    meta: Dict[str, Any] = Field(default_factory=dict)


class ABAssignment(BaseModel):
    """A/B test variant assignment"""

    userId: str
    experiment: str
    variant: str
    timestamp: int
    userAgent: str
    screenSize: str


class ABConversion(BaseModel):
    """A/B test conversion event"""

    userId: str
    experiment: str
    variant: str
    conversionType: str = "default"
    value: float = 1.0
    timestamp: int


class ABEvent(BaseModel):
    """A/B test custom event"""

    userId: str
    experiment: str
    variant: str
    eventName: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: int


class UsabilityEvent(BaseModel):
    """Single usability tracking event"""

    type: str
    timestamp: int
    data: Dict[str, Any] = Field(default_factory=dict)


class UsabilitySession(BaseModel):
    """Complete usability testing session"""

    id: str
    startTime: int
    endTime: Optional[int] = None
    duration: Optional[int] = None
    userAgent: str
    screenSize: str
    viewport: str
    language: str
    events: List[Dict[str, Any]]
    statistics: Optional[Dict[str, Any]] = None


# ===== Helper Functions =====


def append_to_jsonl(file_path: Path, data: dict):
    """Append data as JSON line to file"""
    with open(file_path, "a") as f:
        f.write(json.dumps(data) + "\n")


def read_jsonl(file_path: Path) -> List[dict]:
    """Read all JSON lines from file"""
    if not file_path.exists():
        return []

    with open(file_path, "r") as f:
        return [json.loads(line) for line in f if line.strip()]


def calculate_conversion_rate(conversions: int, impressions: int) -> float:
    """Calculate conversion rate percentage"""
    if impressions == 0:
        return 0.0
    return round((conversions / impressions) * 100, 2)


# ===== Analytics Endpoints =====


@router.post("/analytics/events")
async def track_analytics_events(batch: AnalyticsBatch):
    """
    Track batch of analytics events

    Stores events in JSONL format for later analysis
    """
    try:
        for event in batch.events:
            event_data = {
                **event.dict(),
                "receivedAt": int(datetime.now().timestamp() * 1000),
                "batchId": batch.meta.get("flushTime"),
            }
            append_to_jsonl(ANALYTICS_FILE, event_data)

        return {
            "success": True,
            "eventsReceived": len(batch.events),
            "message": f"Tracked {len(batch.events)} events",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track events: {str(e)}")


@router.get("/analytics/summary")
async def get_analytics_summary():
    """
    Get analytics summary statistics
    """
    try:
        events = read_jsonl(ANALYTICS_FILE)

        # Calculate statistics
        total_events = len(events)
        unique_users = len(set(e.get("userId") for e in events))
        unique_sessions = len(set(e.get("sessionId") for e in events))

        # Group by event name
        event_counts = {}
        for event in events:
            name = event.get("eventName", "unknown")
            event_counts[name] = event_counts.get(name, 0) + 1

        # Top events
        top_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "totalEvents": total_events,
            "uniqueUsers": unique_users,
            "uniqueSessions": unique_sessions,
            "topEvents": [
                {"event": name, "count": count} for name, count in top_events
            ],
            "eventTypes": event_counts,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


# ===== A/B Testing Endpoints =====


@router.post("/ab-test/assignment")
async def track_ab_assignment(assignment: ABAssignment):
    """Track A/B test variant assignment"""
    try:
        data = {
            **assignment.dict(),
            "receivedAt": int(datetime.now().timestamp() * 1000),
        }
        append_to_jsonl(AB_ASSIGNMENTS_FILE, data)

        return {
            "success": True,
            "message": f"Assignment tracked: {assignment.experiment} -> {assignment.variant}",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to track assignment: {str(e)}"
        )


@router.post("/ab-test/conversion")
async def track_ab_conversion(conversion: ABConversion):
    """Track A/B test conversion"""
    try:
        data = {
            **conversion.dict(),
            "receivedAt": int(datetime.now().timestamp() * 1000),
        }
        append_to_jsonl(AB_CONVERSIONS_FILE, data)

        return {
            "success": True,
            "message": f"Conversion tracked: {conversion.experiment}",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to track conversion: {str(e)}"
        )


@router.post("/ab-test/event")
async def track_ab_event(event: ABEvent):
    """Track A/B test custom event"""
    try:
        data = {**event.dict(), "receivedAt": int(datetime.now().timestamp() * 1000)}
        append_to_jsonl(AB_EVENTS_FILE, data)

        return {"success": True, "message": f"Event tracked: {event.eventName}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track event: {str(e)}")


@router.get("/ab-test/results")
async def get_ab_test_results():
    """
    Get A/B test results and analysis
    """
    try:
        assignments = read_jsonl(AB_ASSIGNMENTS_FILE)
        conversions = read_jsonl(AB_CONVERSIONS_FILE)

        # Group by experiment
        experiments = {}

        # Count impressions (assignments)
        for assignment in assignments:
            exp = assignment.get("experiment")
            variant = assignment.get("variant")

            if exp not in experiments:
                experiments[exp] = {}

            if variant not in experiments[exp]:
                experiments[exp][variant] = {"impressions": 0, "conversions": 0}

            experiments[exp][variant]["impressions"] += 1

        # Count conversions
        for conversion in conversions:
            exp = conversion.get("experiment")
            variant = conversion.get("variant")

            if exp in experiments and variant in experiments[exp]:
                experiments[exp][variant]["conversions"] += 1

        # Calculate conversion rates
        results = {}
        for exp, variants in experiments.items():
            results[exp] = {}
            for variant, data in variants.items():
                results[exp][variant] = {
                    **data,
                    "conversionRate": calculate_conversion_rate(
                        data["conversions"], data["impressions"]
                    ),
                }

        return {
            "experiments": results,
            "totalAssignments": len(assignments),
            "totalConversions": len(conversions),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")


# ===== Usability Testing Endpoints =====


@router.post("/usability/sessions")
async def track_usability_session(session: UsabilitySession):
    """
    Track usability testing session
    """
    try:
        data = {**session.dict(), "receivedAt": int(datetime.now().timestamp() * 1000)}
        append_to_jsonl(USABILITY_SESSIONS_FILE, data)

        return {
            "success": True,
            "sessionId": session.id,
            "message": f"Session tracked: {len(session.events)} events",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to track session: {str(e)}"
        )


@router.get("/usability/sessions")
async def get_usability_sessions(limit: int = 50):
    """
    Get recent usability sessions
    """
    try:
        sessions = read_jsonl(USABILITY_SESSIONS_FILE)

        # Sort by start time (newest first)
        sessions.sort(key=lambda s: s.get("startTime", 0), reverse=True)

        return {"sessions": sessions[:limit], "total": len(sessions)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")


@router.get("/usability/analysis")
async def get_usability_analysis():
    """
    Get usability analysis and insights
    """
    try:
        sessions = read_jsonl(USABILITY_SESSIONS_FILE)

        if not sessions:
            return {
                "totalSessions": 0,
                "averageDuration": 0,
                "totalClicks": 0,
                "totalErrors": 0,
                "topClickTargets": [],
                "errorPatterns": [],
            }

        # Calculate statistics
        total_sessions = len(sessions)
        total_duration = sum(s.get("duration", 0) for s in sessions)
        avg_duration = total_duration / total_sessions if total_sessions > 0 else 0

        # Analyze events across all sessions
        all_events = []
        for session in sessions:
            all_events.extend(session.get("events", []))

        click_events = [e for e in all_events if e.get("type") == "click"]
        error_events = [e for e in all_events if e.get("type") == "error"]

        # Top click targets
        click_targets = {}
        for click in click_events:
            target = click.get("target", {})
            key = f"{target.get('tag', 'unknown')}.{target.get('className', '')}"
            click_targets[key] = click_targets.get(key, 0) + 1

        top_clicks = sorted(click_targets.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]

        # Error patterns
        error_patterns = {}
        for error in error_events:
            msg = error.get("message", "Unknown error")
            error_patterns[msg] = error_patterns.get(msg, 0) + 1

        top_errors = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]

        return {
            "totalSessions": total_sessions,
            "averageDuration": round(avg_duration / 1000, 2),  # in seconds
            "totalClicks": len(click_events),
            "totalErrors": len(error_events),
            "topClickTargets": [{"target": t, "count": c} for t, c in top_clicks],
            "errorPatterns": [{"error": e, "count": c} for e, c in top_errors],
            "sessionsAnalyzed": total_sessions,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze usability: {str(e)}"
        )
