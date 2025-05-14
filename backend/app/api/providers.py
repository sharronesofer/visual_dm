from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import CloudProvider
from .schemas import CloudProviderCreate, CloudProviderResponse, CloudProviderUpdate
from ..core.api.fastapi import APIResponse, APIError, NotFoundError

router = APIRouter(tags=["providers"])

@router.get("/", response_model=APIResponse[List[CloudProviderResponse]])
async def list_providers(db: Session = Depends(get_db)):
    """List all cloud providers."""
    try:
        providers = db.query(CloudProvider).all()
        return APIResponse.success(data=providers)
    except Exception as e:
        raise APIError(str(e))

@router.post("/", response_model=APIResponse[CloudProviderResponse])
async def create_provider(provider: CloudProviderCreate, db: Session = Depends(get_db)):
    """Create a new cloud provider."""
    try:
        db_provider = CloudProvider(**provider.dict())
        db.add(db_provider)
        db.commit()
        db.refresh(db_provider)
        return APIResponse.created(data=db_provider)
    except Exception as e:
        db.rollback()
        raise APIError(str(e))

@router.get("/{provider_id}", response_model=APIResponse[CloudProviderResponse])
async def get_provider(provider_id: int, db: Session = Depends(get_db)):
    """Get a specific cloud provider."""
    try:
        provider = db.query(CloudProvider).filter(CloudProvider.id == provider_id).first()
        if not provider:
            raise NotFoundError("Cloud provider not found")
        return APIResponse.success(data=provider)
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.put("/{provider_id}", response_model=APIResponse[CloudProviderResponse])
async def update_provider(
    provider_id: int,
    provider: CloudProviderUpdate,
    db: Session = Depends(get_db)
):
    """Update a cloud provider."""
    try:
        db_provider = db.query(CloudProvider).filter(CloudProvider.id == provider_id).first()
        if not db_provider:
            raise NotFoundError("Cloud provider not found")
        
        for key, value in provider.dict(exclude_unset=True).items():
            setattr(db_provider, key, value)
        
        db.commit()
        db.refresh(db_provider)
        return APIResponse.success(data=db_provider)
    except NotFoundError:
        raise
    except Exception as e:
        db.rollback()
        raise APIError(str(e))

@router.delete("/{provider_id}", response_model=APIResponse[dict])
async def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    """Delete a cloud provider."""
    try:
        db_provider = db.query(CloudProvider).filter(CloudProvider.id == provider_id).first()
        if not db_provider:
            raise NotFoundError("Cloud provider not found")
        
        db.delete(db_provider)
        db.commit()
        return APIResponse.success(data={"message": "Provider deleted successfully"})
    except NotFoundError:
        raise
    except Exception as e:
        db.rollback()
        raise APIError(str(e)) 