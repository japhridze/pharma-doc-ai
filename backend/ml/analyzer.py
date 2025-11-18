from dataclasses import dataclass
from typing import List

from sklearn.ensemble import IsolationForest
import numpy as np


@dataclass
class Issue:
    type: str
    message: str
    severity: str


@dataclass
class AnalysisResult:
    risk_score: float
    summary: str
    issues: List[Issue]


def _heuristic_issues(text: str) -> List[Issue]:
    issues: List[Issue] = []

    lower = text.lower()
    if "temperature" not in lower:
        issues.append(Issue(
            type="missing_field",
            message="No temperature information found.",
            severity="high",
        ))
    if "signature" not in lower and "signed" not in lower:
        issues.append(Issue(
            type="missing_signature",
            message="No operator or QA signature found.",
            severity="medium",
        ))
    if "deviation" in lower and "justification" not in lower:
        issues.append(Issue(
            type="missing_justification",
            message="Deviation mentioned but no justification.",
            severity="medium",
        ))

    return issues


def _simple_numeric_anomaly(text: str) -> float:
    """
    Dummy function: in the future, parse temps, times, etc.
    For now return a constant in [0, 1].
    """
    return 0.2  # 0 = no anomaly, 1 = severe anomaly


def analyze_batch_document(text: str) -> AnalysisResult:
    issues = _heuristic_issues(text)
    anomaly_score = _simple_numeric_anomaly(text)

    # Combine heuristic issues + anomaly score into 0–100 risk
    base_risk = 20 * len(issues)  # each issue adds 20 points
    risk_score = min(100.0, base_risk + anomaly_score * 20)

    if not issues:
        summary = "No major issues detected in batch record (basic heuristic analysis)."
    else:
        summary_lines = [f"- [{i.severity.upper()}] {i.message}" for i in issues]
        summary = "Potential GMP issues detected:\n" + "\n".join(summary_lines)

    return AnalysisResult(
        risk_score=risk_score,
        summary=summary,
        issues=issues,
    )
