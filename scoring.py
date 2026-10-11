# scoring.py
import json
from typing import List, Dict, Any

def normalize_fsp_score(fsp_rating: float, contests_count: int) -> float:
    """Нормализует рейтинг ФСП в диапазон 0-100 с бонусом за активность."""
    if not fsp_rating or fsp_rating <= 0:
        return 0.0
    # Базовый расчет: рейтинг 2000 берем за 85 баллов, контесты добавляют до 15 баллов
    base_rating_score = min(85.0, (fsp_rating / 2400.0) * 85.0)
    contest_bonus = min(15.0, contests_count * 3.0)
    return round(base_rating_score + contest_bonus, 2)

def calculate_stack_match(candidate_stack: List[str], required_stack: List[str]) -> float:
    if not required_stack:
        return 1.0
    c_set = set(s.lower() for s in candidate_stack)
    r_set = set(s.lower() for s in required_stack)
    match_count = len(c_set.intersection(r_set))
    return round(match_count / len(r_set), 2)

def calculate_candidate_score(candidate, vacancy_stack: List[str]) -> Dict[str, Any]:
    c_stack = json.loads(candidate.stack) if isinstance(candidate.stack, str) else candidate.stack

test_part = candidate.test_score
    fsp_norm = normalize_fsp_score(candidate.fsp_rating, candidate.fsp_contests_count)
    stack_part = calculate_stack_match(c_stack, vacancy_stack) * 100.0
    recency_part = (candidate.recency_bonus or 1.0) * 100.0
    
    total_score = (
        0.4 * test_part +
        0.3 * fsp_norm +
        0.2 * stack_part +
        0.1 * recency_part
    )
    
    return {
        "candidate_id": candidate.id,
        "total_score": round(total_score, 2),
        "breakdown": {
            "test_score_contrib": round(0.4 * test_part, 2),
            "fsp_score_contrib": round(0.3 * fsp_norm, 2),
            "stack_match_contrib": round(0.2 * stack_part, 2),
            "recency_contrib": round(0.1 * recency_part, 2),
            "fsp_rating_raw": candidate.fsp_rating,
            "has_fsp_profile": bool(candidate.fsp_id and candidate.fsp_rating > 0)
        }
    }