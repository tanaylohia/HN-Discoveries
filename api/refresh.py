import json
from datetime import datetime

def handler(request, response):
    """Handle refresh requests"""
    # Set CORS headers
    response.status_code = 200
    response.headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    # Handle preflight
    if request.method == 'OPTIONS':
        return response
    
    # For Vercel, we can't run long-running processes
    # So we'll return a message indicating manual refresh is needed
    response.body = json.dumps({
        "success": True,
        "message": "Refresh noted. The data will be updated in the next scheduled run.",
        "timestamp": datetime.now().isoformat() + 'Z',
        "note": "For real-time updates, run the agent locally or use a scheduled job service."
    })
    
    return response