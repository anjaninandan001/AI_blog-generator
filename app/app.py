from flask import Flask, render_template, request, jsonify
import requests
import json
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ollama API configuration
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api')
DEFAULT_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_blog():
    """Generate a blog post based on the given topic."""
    data = request.get_json()
    topic = data.get('topic', '')
    tone = data.get('tone', 'informative')
    length = data.get('length', 500)
    
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    
    try:
        # Create a prompt for the blog post
        prompt = f"""Write a {tone} blog post about {topic}. 
        The blog post should be approximately {length} words. 
        Include a catchy title, an introduction, several paragraphs with subheadings, and a conclusion."""
        
        # Prepare request to Ollama API
        logger.info(f"Generating blog post about: {topic}")
        payload = {
            "model": DEFAULT_MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        # Call Ollama API
        response = requests.post(
            f"{OLLAMA_API_URL}/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        # Process the response
        if response.status_code == 200:
            result = response.json()
            blog_post = result.get('response', '')
            return jsonify({'blog_post': blog_post})
        else:
            logger.error(f"Error from Ollama API: {response.text}")
            return jsonify({'error': 'Failed to generate content'}), 500
    
    except Exception as e:
        logger.error(f"Error generating blog post: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/models', methods=['GET'])
def get_models():
    """Get a list of available models from Ollama."""
    try:
        # Call Ollama API to list models
        response = requests.get(f"{OLLAMA_API_URL}/tags")
        
        if response.status_code == 200:
            models_data = response.json()
            models = [model['name'] for model in models_data.get('models', [])]
            return jsonify({'models': models})
        else:
            # Fallback to default models if API call fails
            default_models = [DEFAULT_MODEL]
            return jsonify({'models': default_models})
    except Exception as e:
        logger.error(f"Error getting models: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
