import io
from typing import List

from PIL import Image
from fastapi import APIRouter, UploadFile, Depends, File

from api.schema import ModelResponse, PredictResponse
from api.service import ProcessService, get_process_service
from api.util import run_in_threadpool

router = APIRouter(
    prefix="/yolo",
    tags=["Tools"]
)


@router.post("/predict",
             status_code=200,
             response_model=ModelResponse[List[PredictResponse]],
             response_model_exclude_none=True
             )
async def predict(file: UploadFile = File(...), service: ProcessService = Depends(get_process_service)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    response = await run_in_threadpool(service.inference, image)
    return ModelResponse(
        message="Xử lý thành công",
        data=response
    )
