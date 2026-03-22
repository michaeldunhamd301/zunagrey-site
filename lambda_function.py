import json
import base64

def lambda_handler(event, context):
    """
    Serve the index.html file as a static webpage.
    """
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'  # For dev; change to 'max-age=3600' for prod
            },
            'body': html_content
        }
    except FileNotFoundError:
        print("Error: index.html not found in Lambda package")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Static content not found', 'details': 'index.html missing from deployment package'})
        }
    except Exception as e:
        print(f"Error serving content: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }
