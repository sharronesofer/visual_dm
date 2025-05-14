import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Network Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5050')

# API Endpoints
ENDPOINTS = {
    'character_create': f'{BACKEND_URL}/character/create',
    'character_load': f'{BACKEND_URL}/character/load',
    'region_generate': f'{BACKEND_URL}/region/generate',
    'world_generate': f'{BACKEND_URL}/world/generate',
}

# Request timeouts in seconds
REQUEST_TIMEOUT = 30

# Maximum retries for failed requests
MAX_RETRIES = 3 