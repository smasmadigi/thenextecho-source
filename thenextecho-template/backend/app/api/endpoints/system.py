from fastapi import APIRouter
# Add endpoints for model management, integrations etc. here
router = APIRouter()
@router.get("/health")
def health_check():
    return {"status": "healthy"}
