import os
import sys

if os.environ.get('FLASK_ENV') != 'production':
    from dotenv import load_dotenv
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(backend_dir)
    
    load_dotenv(os.path.join(root_dir, '.env.local'))
    load_dotenv(os.path.join(root_dir, '.env'))
    
    required_vars = [
        'SECRET_KEY',
        'AZURE_STORAGE_CONNECTION_STRING',
        'AZURE_TEXT_ANALYTICS_ENDPOINT',
        'AZURE_TEXT_ANALYTICS_KEY',
        'AZURE_SPEECH_KEY',
        'AZURE_SPEECH_REGION',
        'OPENAI_API_KEY',
    ]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print(f"Please ensure .env.local exists in: {root_dir}")
        hints = {
            'SECRET_KEY': 'Set a development secret, e.g., SECRET_KEY=dev-secret',
            'AZURE_STORAGE_CONNECTION_STRING': 'Required for serving generated audio locally.',
            'AZURE_TEXT_ANALYTICS_ENDPOINT': 'Azure Text Analytics endpoint URL is required.',
            'AZURE_TEXT_ANALYTICS_KEY': 'Azure Text Analytics API key is required.',
            'AZURE_SPEECH_KEY': 'Azure Speech API key is required for TTS audio.',
            'AZURE_SPEECH_REGION': 'Azure Speech region (e.g., eastus) is required.',
            'OPENAI_API_KEY': 'OpenAI API key is required to generate AI responses.',
        }
        for var in missing_vars:
            if var in hints:
                print(f" - {var}: {hints[var]}")
        sys.exit(1)
    
else:
    required_vars = [
        'SECRET_KEY',
        'AZURE_TEXT_ANALYTICS_ENDPOINT',
        'AZURE_TEXT_ANALYTICS_KEY',
        'AZURE_SPEECH_KEY',
        'AZURE_SPEECH_REGION',
        'AZURE_STORAGE_CONNECTION_STRING',
        'OPENAI_API_KEY',
        'CORS_ORIGINS',
    ]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables in production: {', '.join(missing_vars)}")
        print("Please check Container Apps environment variable configuration")
        sys.exit(1)
    
from app import create_app
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    if not debug:
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    app.run(host='0.0.0.0', port=port, debug=debug)