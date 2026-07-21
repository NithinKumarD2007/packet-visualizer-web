from fastapi import APIRouter
from backend.app.services.analytics import get_intelligence_data

router = APIRouter()


@router.get("/intelligence")
def get_intelligence():

    return get_intelligence_data()