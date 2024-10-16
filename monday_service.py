import requests
import os
import json


def get_column_value(token: str, item_id: str, column_id: str) -> str:
    query = """
    query($itemId: [ID!], $columnId: [String!]) {
        items (ids: $itemId) {
            column_values(ids:$columnId) {
                value
                text
            }
        }
    }
    """
    variables = {"columnId": column_id, "itemId": item_id}
    print(f"Variables: {json.dumps(variables, indent=2)}")

    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": token,
        "API-Version": "2024-10",
        "Content-Type": "application/json"
    }
    payload = {"query": query, "variables": variables}

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    if 'data' not in data:
        print("'data' key missing in response")
        raise ValueError("Unexpected response structure: 'data' key missing")

    items = data['data'].get('items', [])

    if not items:
        print(f"No items found for item_id: {item_id}")
        raise ValueError(
            f"No items found for item_id: {item_id}. Token: {token}")

    column_values = items[0].get('column_values', [])

    if not column_values:
        print(f"No column values found for column_id: {column_id}")
        raise ValueError(f"No column values found for column_id: {column_id}")

    text = column_values[0].get('text')

    if text is None:
        print(f"No text value found for column_id: {column_id}")
        raise ValueError(f"No text value found for column_id: {column_id}")

    return text


def change_column_value(token: str, board_id: str, item_id: str, column_id: str, value: str):
    query = """
  mutation change_column_value($boardId: ID!, $itemId: ID!, $columnId: String!, $value: JSON!) {
    change_column_value(board_id: $boardId, item_id: $itemId, column_id: $columnId, value: $value) {
      id
    }
  }
  """
    variables = {"boardId": board_id, "columnId": column_id,
                 "itemId": item_id, "value": value}

    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": query, "variables": variables},
        headers={"Authorization": token, "API-Version": "2024-04"}
    )

    return response.json()


def upload_file_to_column(token: str, item_id: str, column_id: str, file_path: str, upload_file_name: str):
    if not upload_file_name:
        upload_file_name = 'Edited PDF.pdf'

    query = f"""
    mutation add_file($file: File!){{add_file_to_column (item_id: {item_id}, column_id: "{column_id}", file: $file) {{id}} }}
    """

    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    input_file_path = os.path.join(project_root, 'output', file_path)

    files = [
        ('image', (f"{upload_file_name}.pdf", open(
            input_file_path, 'rb'), 'application/octet-stream'))
    ]
    data = {
        'query': query,
        'map': '{"image": "variables.file"}'
    }

    response = requests.post(
        "https://api.monday.com/v2/file",
        headers={"Authorization": token, "API-Version": "2024-10"},
        data=data,
        files=files
    )

    return response
