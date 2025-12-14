import boto3
import json
import time
import uuid
import os
from random import randint
from datetime import datetime

# ---------- CORS ----------
def get_cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'OPTIONS,POST'
    }

# ---------- Base64 Size ----------
def calculate_base64_size(base64_string):
    try:
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        padding = base64_string.count('=')
        return (len(base64_string) * 3 // 4) - padding
    except Exception:
        return 0

# ---------- DynamoDB Logger ----------
def log_to_dynamodb(job_id, user_id, vehicle, customization, status,
                    input_size, output_size, generation_time_ms,
                    error_message=None):

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('VehicleImageGenerationTable')

    # 🔑 THIS DICTIONARY MUST CONTAIN "id"
    item = {
        'id': job_id,  # ✅ PRIMARY KEY (MANDATORY)
        'timestamp': datetime.utcnow().isoformat(),

        # Business data
        'userId': user_id,
        'vehicle': vehicle,
        'customization': customization,
        'status': status,

        # Metrics
        'input_image_size_bytes': input_size,
        'output_image_size_bytes': output_size,
        'generation_time_ms': generation_time_ms
    }

    if error_message:
        item['error_message'] = error_message[:500]

    # ✅ WRITE TO DYNAMODB
    table.put_item(Item=item)



# ---------- Bedrock Request ----------
def prepare_bedrock_request(prompt, image_base64):
    return json.dumps({
        "taskType": "IMAGE_EDIT",
        "imageGenerationConfig": {
            "numberOfImages": 2,
            "height": 1024,
            "width": 1024,
            "quality": "premium",
            "cfgScale": 8.0,
            "seed": randint(0, 100000)
        },
        "imageEditParams": {
            "image": image_base64,
            "text": prompt
        }
    })

# ---------- Lambda Handler ----------
def lambda_handler(event, context):
    job_id = str(uuid.uuid4())
    start_time = time.time()

    # ---------- SAFE BODY PARSING (FIX) ----------
    if 'body' not in event or event['body'] is None:
        return {
            'statusCode': 400,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Missing request body'})
        }

    try:
        body = event['body']
        if isinstance(body, str):
            body = json.loads(body)
    except Exception:
        return {
            'statusCode': 400,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Invalid JSON'})
        }

    # ---------- SAFE FIELD EXTRACTION ----------
    vehicle = body.get('vehicle', {
        "type": "UNKNOWN",
        "brand": "UNKNOWN"
    })

    customization = body.get('customization')
    if not customization:
        return {
            'statusCode': 400,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Missing field: customization'})
        }

    base_image = body.get('base_image')
    if not base_image:
        return {
            'statusCode': 400,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Missing field: base_image'})
        }

    user_id = (
        event.get('requestContext', {})
             .get('authorizer', {})
             .get('claims', {})
             .get('sub', 'anonymous')
    )

    image_base64 = base_image.split(",")[1] if "," in base_image else base_image
    input_size = calculate_base64_size(base_image)

    # ---------- PROMPT ENGINEERING ----------
    prompt = f"""
    Edit the vehicle image realistically:
    - Change body color to {customization.get('color')}
    - Replace wheels with {customization.get('rims')}
    - Add decals: {customization.get('decals')}
    Maintain original lighting, reflections, proportions, and background.
    """

    # ---------- BEDROCK CALL ----------
    try:
        bedrock = boto3.client('bedrock-runtime')

        request_body = prepare_bedrock_request(prompt, image_base64)
        model_id = "amazon.titan-image-generator-v2:0"

        bedrock_start = time.time()
        response = bedrock.invoke_model(
            body=request_body,
            modelId=model_id,
            contentType="application/json",
            accept="application/json"
        )

        generation_time_ms = int((time.time() - bedrock_start) * 1000)

        output = json.loads(response['body'].read())
        images = output.get('images', [])

        output_size = sum(calculate_base64_size(img) for img in images)

        log_to_dynamodb(
            job_id=job_id,
            user_id=user_id,
            vehicle=vehicle,
            customization=customization,
            status="COMPLETED",
            input_size=input_size,
            output_size=output_size,
            generation_time_ms=generation_time_ms
        )

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'job_id': job_id,
                'images': images,
                'generation_time_ms': generation_time_ms
            })
        }

    except Exception as e:
        generation_time_ms = int((time.time() - start_time) * 1000)

        log_to_dynamodb(
            job_id=job_id,
            user_id=user_id,
            vehicle=vehicle,
            customization=customization,
            status="FAILED",
            input_size=input_size,
            output_size=0,
            generation_time_ms=generation_time_ms,
            error_message=str(e)
        )

        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': str(e),
                'job_id': job_id
            })
        }
