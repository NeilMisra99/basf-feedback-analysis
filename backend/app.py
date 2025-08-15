import os
import sys

# Load .env files in development or when not running in Azure
# In production (Azure), WEBSITE_SITE_NAME environment variable is automatically set
if not os.environ.get('WEBSITE_SITE_NAME'):
    from dotenv import load_dotenv
    # Get the root directory (parent of backend directory)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(backend_dir)
    
    # Load environment variables from root directory
    # Priority: .env.local -> .env
    load_dotenv(os.path.join(root_dir, '.env.local'))
    load_dotenv(os.path.join(root_dir, '.env'))
    
    # Verify critical environment variables are loaded (development only)
    required_vars = ['SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print(f"Please ensure .env.local exists in: {root_dir}")
        sys.exit(1)
    
    print("✅ Environment variables loaded successfully")

from app import create_app
app = create_app()

if __name__ == '__main__':
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