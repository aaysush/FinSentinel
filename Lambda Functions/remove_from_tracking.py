import json
import boto3
import os

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb")
table_name = os.environ["PRICE_TRACKER_DB"]
table = dynamodb.Table(table_name)

# CORS Headers - Fixed for S3 bucket specific access
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "https://pricetracker-20jun2025.s3.ap-south-1.amazonaws.com",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Credentials": "true",
    "Content-Type": "application/json"
}

# Caesar Cipher for encryption
def encrypt_password(password, shift=3):
    encrypted = ''
    for char in password:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            encrypted += chr((ord(char) - base + shift) % 26 + base)
        elif char.isdigit():
            encrypted += chr((ord(char) - ord('0') + shift) % 10 + ord('0'))
        else:
            encrypted += char
    return encrypted

# Lambda handler
def lambda_handler(event, context):
    # Handle CORS Preflight
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "CORS preflight OK"})
        }

    # Log the incoming event for debugging
    print("Received event:", json.dumps(event))

    try:
        # Parse incoming body - FIXED to handle direct payload
        body = event.get("body", '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        print("Parsed body:", body)
        
        # Extract values directly (no nested body handling)
        email = body.get("email")
        figi = body.get("figi") 
        password = body.get("password")

        # Validate inputs
        if not all([email, figi, password]):
            missing_fields = [field for field in ['email', 'figi', 'password'] if not body.get(field)]
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": f"Missing required fields: {', '.join(missing_fields)}"})
            }

        # Encrypt password
        encrypted_password = encrypt_password(password)

        # Fetch item from DynamoDB
        response = table.get_item(Key={"email": email, "figi": figi})
        item = response.get("Item")

        if not item:
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Stock not found in your portfolio"})
            }

        # Password mismatch check
        if item.get("password") != encrypted_password:
            return {
                "statusCode": 401,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Password mismatch"})
            }

        # Delete item
        table.delete_item(Key={"email": email, "figi": figi})

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "Stock deleted successfully"})
        }

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "Invalid JSON format"})
        }
    except Exception as e:
        # Catch-all for internal errors
        print(f"Internal server error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }
