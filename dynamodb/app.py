import os
import json
import uuid
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME', 'TodoTable')
table = dynamodb.Table(TABLE_NAME)

def response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {"Content-Type": "application/json"}
    }

def lambda_handler(event, context):
    method = event.get('requestContext', {}).get('http', {}).get('method') or event.get('httpMethod')
    path_params = event.get('pathParameters') or {}
    body = None
    if event.get('body'):
        try:
            body = json.loads(event['body'])
        except:
            body = None

    # POST /todos  -> create
    if method == "POST" and event.get('rawPath', '').endswith('/todos') or (method == "POST" and event.get('path', '') == '/todos'):
        title = (body or {}).get('title')
        if not title:
            return response(400, {"message":"'title' is required"})
        item = {
            "id": str(uuid.uuid4()),
            "title": title,
            "done": bool(body.get('done', False))
        }
        table.put_item(Item=item)
        return response(201, item)

    # GET /todos -> list all
    if method == "GET" and (event.get('rawPath', '').endswith('/todos') or event.get('path', '') == '/todos'):
        resp = table.scan()
        items = resp.get('Items', [])
        return response(200, items)

    # For /todos/{id}
    todo_id = path_params.get('id') if path_params else None

    if todo_id:
        # GET /todos/{id}
        if method == "GET":
            resp = table.get_item(Key={"id": todo_id})
            item = resp.get('Item')
            if not item:
                return response(404, {"message":"Not found"})
            return response(200, item)

        # PUT /todos/{id} -> update (partial)
        if method == "PUT" or method == "PATCH":
            if not body:
                return response(400, {"message":"Missing JSON body"})
            update_expression = []
            expression_attribute_values = {}
            if 'title' in body:
                update_expression.append("title = :t")
                expression_attribute_values[":t"] = body['title']
            if 'done' in body:
                update_expression.append("done = :d")
                expression_attribute_values[":d"] = bool(body['done'])
            if not update_expression:
                return response(400, {"message":"Nothing to update"})
            ue = "SET " + ", ".join(update_expression)
            table.update_item(
                Key={"id": todo_id},
                UpdateExpression=ue,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )
            updated = table.get_item(Key={"id": todo_id}).get('Item')
            return response(200, updated if updated else {})

        # DELETE /todos/{id}
        if method == "DELETE":
            table.delete_item(Key={"id": todo_id})
            return response(204, {})

    return response(400, {"message":"Bad request"})
