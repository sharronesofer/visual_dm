from fastapi import APIRouter, HTTPException
from .schemas import RumorTransformationRequest, RumorTransformationResponse
from .gpt_client import GPTClient
from .rumor_transformer import RumorTransformer
from .truth_tracker import TruthTracker
from utils.cache import async_cached

router = APIRouter()
gpt_client = GPTClient()
transformer = RumorTransformer(gpt_client)

@router.post("/transform", response_model=RumorTransformationResponse)
@async_cached(ttl=120)  # Cache for 2 minutes
async def transform_rumor(req: RumorTransformationRequest):
    try:
        transformed = await transformer.transform_rumor(
            event=req.event,
            rumor=req.rumor,
            traits=req.traits,
            distortion_level=req.distortion_level
        )
        new_truth = TruthTracker.calculate_truth_value(req.event, transformed)
        return RumorTransformationResponse(transformed_rumor=transformed, new_truth_value=new_truth)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
