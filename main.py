# main.py
import json
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

import models, scoring
from database import get_db

app = FastAPI(title="POW Platform API", version="1.0.0")

class InviteRequest(BaseModel):
    candidate_id: int
    vacancy_id: int
    offer_salary_min: int
    offer_salary_max: int
    message: str

@app.get("/api/candidates/search")
def search_candidates(
    specialization: str,
    grade: str,
    vacancy_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Поиск кандидатов по категории и расчет ранжирования."""
    query = db.query(models.Candidate).filter(
        models.Candidate.specialization == specialization,
        models.Candidate.confirmed_grade == grade
    )
    candidates = query.all()
    
    vacancy_stack = []
    if vacancy_id:
        vac = db.query(models.Vacancy).filter(models.Vacancy.id == vacancy_id).first()
        if vac:
            vacancy_stack = json.loads(vac.required_stack)
            
    scored = []
    for c in candidates:
        sc = scoring.calculate_candidate_score(c, vacancy_stack)
        
        # Проверяем, принят ли оффер, чтобы раскрыть контакты
        accepted_invite = db.query(models.Invite).filter(
            models.Invite.candidate_id == c.id,
            models.Invite.status == models.InviteStatusEnum.ACCEPTED
        ).first()
        
        scored.append({
            "id": c.id,
            "full_name": c.full_name,
            "specialization": c.specialization,
            "grade": c.confirmed_grade,
            "score": sc["total_score"],
            "breakdown": sc["breakdown"],
            "has_fsp": sc["breakdown"]["has_fsp_profile"],
            # Защита контактов
            "contacts": {
                "email": c.email if accepted_invite else "СКРЫТО ДО ПРИНЯТИЯ ОФФЕРА",
                "phone": c.phone if accepted_invite else "СКРЫТО ДО ПРИНЯТИЯ ОФФЕРА"
            }
        })
        
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"total": len(scored), "results": scored}

@app.post("/api/invites/send")
def send_invite(payload: InviteRequest, db: Session = Depends(get_db)):
    """Отправка приглашения с валидацией обязательной зарплаты."""
    if payload.offer_salary_min <= 0 or payload.offer_salary_max < payload.offer_salary_min:
        raise HTTPException(status_code=400, detail="Обязательно корректное указание диапазона зарплаты в рублях.")
        
    invite = models.Invite(
        candidate_id=payload.candidate_id,
        vacancy_id=payload.vacancy_id,
        offer_salary_min=payload.offer_salary_min,
        offer_salary_max=payload.offer_salary_max,
        message=payload.message,
        status=models.InviteStatusEnum.PENDING
    )
    db.add(invite)
    db.commit()
    return {"status": "SUCCESS", "invite_id": invite.id}

@app.post("/api/invites/{invite_id}/respond")
def respond_invite(invite_id: int, action: str = Query(..., regex="^(ACCEPT|REJECT)$"), db: Session = Depends(get_db)):
    invite = db.query(models.Invite).filter(models.Invite.id == invite_id).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Приглашение не найдено")
    
    invite.status = models.InviteStatusEnum.ACCEPTED if action == "ACCEPT" else models.InviteStatusEnum.REJECTED
    db.commit()
    return {"status": "UPDATED", "new_status": invite.status}
