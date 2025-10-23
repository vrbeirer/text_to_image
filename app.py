from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import time
import requests
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)

# Store generated images
images = {}

# Serve Landing Page (home.html) as default
@app.route('/')
def home():
    with open('home.html', 'r', encoding='utf-8') as f:
        return f.read()

# Serve Generator Page (index.html)
@app.route('/generator')
def generator():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/generate', methods=['POST'])
def generate_image():
    """Generate image using FREE Pollinations AI API (No API key needed!)"""
    try:
        data = request.json
        prompt = data.get('prompt')
        style = data.get('style', 'cinematic')

        print(f"✨ Generating image: {prompt[:50]}...")

        # Enhanced prompt with style
        enhanced_prompt = f"{prompt}. {get_style_description(style)}"
        
        # Use Pollinations.ai FREE API (no limits, no API key!)
        api_url = "https://image.pollinations.ai/prompt/"
        encoded_prompt = requests.utils.quote(enhanced_prompt)
        image_url = f"{api_url}{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        # Download the image
        response = requests.get(image_url, timeout=30)
        
        if response.status_code == 200:
            # Save image
            image_id = str(int(time.time() * 1000))
            os.makedirs('images', exist_ok=True)
            image_path = f'images/{image_id}.png'
            
            # Save downloaded image
            img = Image.open(BytesIO(response.content))
            img.save(image_path)

            images[image_id] = {
                'prompt': prompt,
                'image_path': image_path,
                'status': 'completed',
                'created_at': time.time()
            }

            print(f"✅ Image saved: {image_path}")

            return jsonify({
                'operation_id': image_id,
                'status': 'completed',
                'image_url': f'/image/{image_id}'
            })
        else:
            return jsonify({'error': 'Image generation failed'}), 500

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error: {error_msg}")
        return jsonify({'error': f'Image generation failed: {error_msg}'}), 500


@app.route('/status/<operation_id>', methods=['GET'])
def check_status(operation_id):
    """Check image generation status"""
    try:
        if operation_id not in images:
            return jsonify({'error': 'Image not found'}), 404

        return jsonify({
            'status': 'completed',
            'image_url': f'/image/{operation_id}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/image/<operation_id>', methods=['GET'])
def get_image(operation_id):
    """Get generated image"""
    try:
        if operation_id not in images:
            return jsonify({'error': 'Image not found'}), 404

        stored = images[operation_id]
        
        if not os.path.exists(stored['image_path']):
            return jsonify({'error': 'Image file not found'}), 404

        return send_file(stored['image_path'], mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/enhance', methods=['POST'])
def enhance_prompt():
    """Enhance prompt - Simple version without API"""
    try:
        data = request.json
        prompt = data.get('prompt', '')

        # Simple enhancement without API
        enhancements = [
            "highly detailed",
            "professional photography",
            "dramatic lighting",
            "vibrant colors",
            "8k resolution",
            "masterpiece"
        ]
        
        enhanced = f"{prompt}, {', '.join(enhancements)}"

        return jsonify({'enhanced_prompt': enhanced})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/suggestions', methods=['POST'])
def get_suggestions():
    """Get AI suggestions - Predefined suggestions"""
    try:
        suggestions = [
            'Add dramatic lighting effects',
            'Include vibrant color palette',
            'Enhance with cinematic composition',
            'Add atmospheric details',
            'Increase visual depth',
            'Include realistic textures'
        ]
        
        import random
        selected = random.sample(suggestions, 3)
        
        return jsonify({'suggestions': selected})

    except Exception as e:
        return jsonify({
            'suggestions': [
                'Add dramatic lighting',
                'Include vibrant colors',
                'Enhance composition'
            ]
        })


def get_style_description(style):
    """Get style description for image generation"""
    styles = {
        'cinematic': 'cinematic photography, professional, dramatic composition',
        'sci-fi': 'futuristic sci-fi aesthetic, cyberpunk, neon lights',
        'fantasy': 'magical fantasy atmosphere, enchanting, mystical',
        'noir': 'film noir style, dramatic shadows, high contrast',
        'anime': 'anime art style, vibrant colors, detailed',
        'cartoon': 'cartoon illustration, playful, colorful',
        'documentary': 'realistic documentary photography, natural',
        'horror': 'dark horror atmosphere, eerie, suspenseful',
        'comedy': 'bright and cheerful, funny, lighthearted',
        'drama': 'dramatic with emotional depth, intense',
        'action': 'dynamic action, energy, movement',
        'thriller': 'thriller atmosphere, suspenseful'
    }
    return styles.get(style, '')


if __name__ == '__main__':
    os.makedirs('images', exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

