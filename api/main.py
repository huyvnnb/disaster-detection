from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from ultralytics import YOLO

from api import router
from api.exception import validation_exception_handler, generic_exception_handler

app = FastAPI()
app.include_router(router.router)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

@app.get("/")
async def hello():
    return {'welcome': 'hello'}