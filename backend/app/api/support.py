from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import SupportTicket, TicketResponse, TicketStatus, User
from app.services.support import SupportService
from app.dependencies import get_db, get_current_user, get_current_admin
from bson import ObjectId

router = APIRouter()

@router.post("/tickets/", response_model=SupportTicket)
async def create_ticket(
    subject: str,
    description: str,
    priority: int = 1,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    support_service = SupportService(db)
    return await support_service.create_ticket(
        current_user["id"],
        subject,
        description,
        priority
    )

@router.get("/tickets/", response_model=List[SupportTicket])
async def get_user_tickets(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    support_service = SupportService(db)
    return await support_service.get_user_tickets(current_user["id"])

@router.get("/tickets/{ticket_id}", response_model=SupportTicket)
async def get_ticket(
    ticket_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    support_service = SupportService(db)
    ticket = await support_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.user_id != current_user["id"] and not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")
    return ticket

@router.get("/admin/tickets/", response_model=List[SupportTicket])
async def get_all_tickets(
    status: Optional[TicketStatus] = None,
    priority: Optional[int] = None,
    current_user: dict = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    support_service = SupportService(db)
    return await support_service.get_all_tickets(status, priority)

@router.put("/admin/tickets/{ticket_id}/status", response_model=SupportTicket)
async def update_ticket_status(
    ticket_id: str,
    status: TicketStatus,
    assigned_to: Optional[str] = None,
    current_user: dict = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    support_service = SupportService(db)
    ticket = await support_service.update_ticket_status(ticket_id, status, assigned_to)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/tickets/{ticket_id}/responses", response_model=TicketResponse)
async def add_response(
    ticket_id: str,
    message: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    support_service = SupportService(db)
    ticket = await support_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.user_id != current_user["id"] and not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to respond to this ticket")
    
    return await support_service.add_response(
        ticket_id,
        current_user["id"],
        message,
        current_user["is_admin"]
    )

@router.get("/tickets/{ticket_id}/responses", response_model=List[TicketResponse])
async def get_ticket_responses(
    ticket_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    support_service = SupportService(db)
    ticket = await support_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.user_id != current_user["id"] and not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket's responses")
    
    return await support_service.get_ticket_responses(ticket_id) 