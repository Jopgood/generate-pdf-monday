# monday_controller.py
from fastapi import Request
from fastapi.responses import JSONResponse
from document_service import edit_docx_convert_to_pdf_and_save, DocxEditOptions
from monday_service import get_column_value, upload_file_to_column


async def execute_generate_document(request: Request):
    session = request.state.session
    payload_json = await request.json()
    payload = payload_json['payload']

    try:
        input_fields = payload['inputFields']
        item_id = input_fields['itemId']
        source_column_id = input_fields['sourceColumnId']
        upload_column_id = input_fields['uploadColumnId']
        file_name = input_fields['text']

        text = get_column_value(
            session['shortLivedToken'], item_id, source_column_id)
        if not text:
            return JSONResponse(
                status_code=400,
                content={
                    "severityCode": 4000,
                    "notificationErrorTitle": "Failed to get column value",
                    "notificationErrorDescription": "Unable to retrieve the column value for document generation",
                    "runtimeErrorDescription": f"Failed to get column value for item {item_id}, column {source_column_id}"
                }
            )

        options = DocxEditOptions(
            input_file_name="Letter template.docx",
            output_file_name="output",
            placeholders={"{insertSection}": text}
        )

        edit_docx_convert_to_pdf_and_save(options)

        upload_file_to_column(
            session['shortLivedToken'], item_id, upload_column_id, 'output.pdf', file_name)
        return {}

    except ValueError as ve:
        return JSONResponse(
            status_code=400,
            content={
                "severityCode": 4000,
                "notificationErrorTitle": "Failed to get column value",
                "notificationErrorDescription": str(ve),
                "runtimeErrorDescription": f"Failed to get column value for item {item_id}, column {source_column_id}: {str(ve)}"
            }
        )

    except Exception as e:
        error_code = 500
        error_message = str(e)

        if isinstance(e, FileNotFoundError):
            error_code = 404
            error_message = "Required file not found"
        elif isinstance(e, PermissionError):
            error_code = 403
            error_message = "Permission denied when accessing file"

        return JSONResponse(
            status_code=error_code,
            content={
                "severityCode": 4000,
                "notificationErrorTitle": "Document Generation Failed",
                "notificationErrorDescription": "An error occurred during document generation",
                "runtimeErrorDescription": f"Error: {error_message}"
            }
        )
