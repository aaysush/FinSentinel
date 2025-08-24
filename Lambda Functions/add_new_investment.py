from decimal import Decimal
import json
import boto3
from boto3.dynamodb.conditions import Key
import os

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['PRICE_TRACKER_DB'])

# CORS Headers - Fixed for S3 bucket specific access
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "https://pricetracker-20jun2025.s3.ap-south-1.amazonaws.com",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Credentials": "true",
    "Content-Type": "application/json"
}

def caesar_encrypt(text: str, shift: int = 3) -> str:
    result = ''
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        elif char.isdigit():
            result += chr((ord(char) - ord('0') + shift) % 10 + ord('0'))
        else:
            result += char
    return result

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
        
        # Extract required fields
        email = body.get('email')
        password = body.get('password')
        figi = body.get('figi')
        price = body.get('price')
        display_symbol = body.get('display_symbol')
        
        # Validate required fields
        if not all([email, password, figi, price, display_symbol]):
            missing_fields = [field for field in ['email', 'password', 'figi', 'price', 'display_symbol'] 
                            if not body.get(field)]
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': f'Missing required fields: {", ".join(missing_fields)}'})
            }
        
        # Encrypt password and convert price to Decimal
        encrypted_password = caesar_encrypt(password)
        decimal_price = Decimal(str(price))
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Invalid JSON format'})
        }
    except (ValueError, TypeError) as e:
        print(f"Data conversion error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': f'Invalid data format: {str(e)}'})
        }
    except Exception as e:
        print(f"Request parsing error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': f'Request parsing error: {str(e)}'})
        }

    try:
        # Check if specific item (email + figi) already exists
        response = table.get_item(Key={'email': email, 'figi': figi})
        item = response.get('Item')

        if item:
            # Item exists, update it if password matches
            if item['password'] == encrypted_password:
                table.update_item(
                    Key={'email': email, 'figi': figi},
                    UpdateExpression="SET price = :p, display_symbol = :d",
                    ExpressionAttributeValues={
                        ':p': decimal_price,
                        ':d': display_symbol
                    }
                )
                return {
                    'statusCode': 200,
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'message': 'Stock updated successfully'})
                }
            else:
                return {
                    'statusCode': 403,
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': 'Password mismatch'})
                }
        else:
            # Item doesn't exist, check if user exists with other stocks
            query_response = table.query(KeyConditionExpression=Key('email').eq(email))
            user_items = query_response.get('Items', [])

            if user_items:
                # User exists, verify password with any existing record
                if any(item['password'] == encrypted_password for item in user_items):
                    # Password matches, add new stock
                    table.put_item(Item={
                        'email': email,
                        'figi': figi,
                        'password': encrypted_password,
                        'price': decimal_price,
                        'display_symbol': display_symbol
                    })
                    return {
                        'statusCode': 200,
                        'headers': CORS_HEADERS,
                        'body': json.dumps({'message': 'New stock added successfully'})
                    }
                else:
                    return {
                        'statusCode': 403,
                        'headers': CORS_HEADERS,
                        'body': json.dumps({'error': 'Password mismatch'})
                    }
            else:
                # New user, create first entry
                table.put_item(Item={
                    'email': email,
                    'figi': figi,
                    'password': encrypted_password,
                    'price': decimal_price,
                    'display_symbol': display_symbol
                })
                return {
                    'statusCode': 200,
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'message': 'New user and stock created successfully'})
                }

    except Exception as e:
        print(f"Database operation error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': f'Database operation failed: {str(e)}'})
        }
