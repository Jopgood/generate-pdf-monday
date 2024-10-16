# monday_routes.py
from fastapi import APIRouter, Request
from monday_controller import execute_generate_document
import logging

monday_router = APIRouter()


@monday_router.post("/generate-document")
async def route_execute_generate_document(request: Request):
    logging.info("Received request to generate document")
    return await execute_generate_document(request)
