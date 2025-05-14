#!/usr/bin/env python3

import os
import sys
import logging
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('app')

# Create Flask app
app = Flask(__name__, static_folder='static')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

@app.route('/')
def index():
    return jsonify({
        'message': 'Python converted application is running',
        'status': 'success'
    })

# Add your API routes here
# @app.route('/api/something', methods=['GET'])
# def get_something():
#     return jsonify({'data': 'value'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
