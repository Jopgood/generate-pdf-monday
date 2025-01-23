from fastapi import APIRouter, Request
from monday_controller import execute_generate_document
import logging
from logging_config import LoggerAdapter, setup_logging

logger = LoggerAdapter(setup_logging(), "monday_routes")
monday_router = APIRouter()


@monday_router.post("/generate-document")
async def route_execute_generate_document(request: Request):
    logger.log_operation(
        logging.INFO,
        "generate_document",
        "Received document generation request"
    )
    return await execute_generate_document(request)
