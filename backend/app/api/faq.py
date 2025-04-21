from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import FAQ, FAQCategory
from app.services.faq import FAQService
from app.dependencies import get_db, get_current_admin

router = APIRouter()

@router.get("/faqs/", response_model=List[FAQ])
async def get_faqs(
    category: Optional[FAQCategory] = None,
    active_only: bool = True,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    faq_service = FAQService(db)
    return await faq_service.get_all_faqs(category, active_only)

@router.get("/faqs/search", response_model=List[FAQ])
async def search_faqs(
    query: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    faq_service = FAQService(db)
    return await faq_service.search_faqs(query)

@router.post("/admin/faqs/", response_model=FAQ)
async def create_faq(
    question: str,
    answer: str,
    category: FAQCategory,
    current_user: dict = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    faq_service = FAQService(db)
    return await faq_service.create_faq(question, answer, category)

@router.get("/admin/faqs/{faq_id}", response_model=FAQ)
async def get_faq(
    faq_id: str,
    current_user: dict = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    faq_service = FAQService(db)
    faq = await faq_service.get_faq(faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq

@router.put("/admin/faqs/{faq_id}", response_model=FAQ)
async def update_faq(
    faq_id: str,
    question: Optional[str] = None,
    answer: Optional[str] = None,
    category: Optional[FAQCategory] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    faq_service = FAQService(db)
    faq = await faq_service.update_faq(faq_id, question, answer, category, is_active)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq

@router.delete("/admin/faqs/{faq_id}")
async def delete_faq(
    faq_id: str,
    current_user: dict = Depends(get_current_admin),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    faq_service = FAQService(db)
    success = await faq_service.delete_faq(faq_id)
    if not success:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return {"message": "FAQ deleted successfully"} 