from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables from root directory
# Priority: .env.local -> .env -> .env.example
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = create_app()

if __name__ == '__main__':
    # Use PORT from environment (fly.io sets this to 8080)
    # Fallback to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # Configure logging for production
    if not debug:
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    app.run(host='0.0.0.0', port=port, debug=debug)