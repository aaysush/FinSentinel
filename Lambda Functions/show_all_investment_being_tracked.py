import boto3
import json
import os
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('PRICE_TRACKER_DB')
table = dynamodb.Table(table_name)

# CORS Headers - Fixed for S3 bucket specific access
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "https://pricetracker-20jun2025.s3.ap-south-1.amazonaws.com",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Credentials": "true",
    "Content-Type": "application/json"
}

def decimal_encoder(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def caesar_encrypt(text, shift=3):
    encrypted = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            encrypted += chr((ord(char) - base + shift) % 26 + base)
        elif char.isdigit():
            encrypted += str((int(char) + shift) % 10)
        else:
            encrypted += char
    return encrypted

def lambda_handler(event, context):
    # Handle CORS preflight request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': ''
        }

    # Log the incoming event for debugging
    print("Received event:", json.dumps(event))
    
    try:
        # Handle different body formats
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)

        print("Parsed body:", body)
        
        email = body.get('email')
        password = body.get('password')

        if not email or not password:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Email and password are required'})
            }

        encrypted_password = caesar_encrypt(password)

        # Use scan with filter instead of query for better compatibility
        response = table.scan(
            FilterExpression=Attr('email').eq(email)
        )
        user_items = response.get('Items', [])

        if not user_items:
            return {
                'statusCode': 404,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'No records found for this email'})
            }

        # Filter items that match the password
        matching_rows = [item for item in user_items if item.get('password') == encrypted_password]

        if not matching_rows:
            return {
                'statusCode': 401,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'Password mismatch'})
            }

        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'message': 'Data retrieved successfully',
                'data': matching_rows
            }, default=decimal_encoder)
        }

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Invalid JSON format'})
        }
    except Exception as e:
        print(f"Server error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': f'Server error: {str(e)}'
            })
        }
