from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from app.config import get_config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Validate critical configuration
    config.validate_config()
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure CORS with security settings
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Initialize and start background processor
    from app.background_processor import background_processor
    from app.sse_manager import sse_manager
    
    # Connect background processor to SSE manager and app context for real-time updates
    background_processor.set_sse_manager(sse_manager)
    background_processor.set_app(app)
    background_processor.start()
    
    return app