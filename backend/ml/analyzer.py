from dataclasses import dataclass
from typing import List
import hashlib
import math


@dataclass
class BatchIssue:
    """Single issue found during heuristic analysis."""
    label: str
    detail: str
    severity: int  # 1–10


@dataclass
class BatchAnalysisResult:
    """Result of analyzing one batch record."""
    risk_score: float
    summary: str
    issues: List[BatchIssue]


# ---------------------------------------------------------------------
# Heuristic text analysis
# ---------------------------------------------------------------------
def analyze_batch_document(text: str) -> BatchAnalysisResult:
    """
    Very simple rule-based analyzer for GMP batch records.

    It looks for keywords like:
      - deviation / non-conformance
      - OOS (out of specification)
      - missing / not recorded / no signature
      - temperature excursions

    You can extend this later with ML / LLM logic.
    """
    lower = text.lower()
    issues: List[BatchIssue] = []
    risk = 0

    def add_issue(label: str, detail: str, severity: int):
        nonlocal risk
        issues.append(BatchIssue(label=label, detail=detail, severity=severity))
        risk += severity

    # A few very basic rules
    if "deviation" in lower or "non-conformance" in lower or "nonconformance" in lower:
        add_issue(
            "Deviation",
            "Text mentions a deviation / non-conformance.",
            severity=4,
        )

    if "oos" in lower or "out of specification" in lower:
        add_issue(
            "Out of Specification",
            "Possible OOS (out of specification) result.",
            severity=6,
        )

    if "no signature" in lower or "missing signature" in lower or "no operator" in lower:
        add_issue(
            "Missing signature",
            "Operator / QA signature may be missing.",
            severity=5,
        )

    if "temperature" in lower and ("high" in lower or "low" in lower or "excursion" in lower):
        add_issue(
            "Temperature excursion",
            "Temperature excursion or abnormal temperature mentioned.",
            severity=5,
        )

    if "without justification" in lower or "no justification" in lower:
        add_issue(
            "Missing justification",
            "Deviation or change without written justification.",
            severity=3,
        )

    # Normalise risk_score to 0–10 range
    risk_score = max(0.0, min(10.0, float(risk)))

    if not issues:
        summary = "No major issues detected in batch record (basic heuristic analysis)."
    else:
        summary = f"{len(issues)} potential issue(s) detected in batch record."

    return BatchAnalysisResult(
        risk_score=risk_score,
        summary=summary,
        issues=issues,
    )


# ---------------------------------------------------------------------
# Lightweight, deterministic "embeddings" (no external services)
# ---------------------------------------------------------------------
def get_embedding_vector(text: str, dim: int = 64) -> list[float]:
    """
    Produce a small deterministic embedding vector from text using SHA-256.

    This is **not** a real semantic embedding, but it's:
      - fast
      - deterministic
      - requires no external API
    Good enough for local experimentation with a vector store.
    """
    # Hash to 32 bytes
    h = hashlib.sha256(text.encode("utf-8")).digest()

    # Repeat/truncate to desired dimension
    raw = (h * ((dim + len(h) - 1) // len(h)))[:dim]

    # Convert bytes -> floats in [0, 1]
    vec = [b / 255.0 for b in raw]

    # L2 normalise
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]
