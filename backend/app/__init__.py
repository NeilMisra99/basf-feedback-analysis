from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from app.config import get_config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    config = get_config()
    app.config.from_object(config)
    
    config.validate_config()
    
    db.init_app(app)
    
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    with app.app_context():
        db.create_all()
    
    from app.background_processor import background_processor
    from app.sse_manager import sse_manager
    
    background_processor.set_sse_manager(sse_manager)
    background_processor.set_app(app)
    background_processor.start()
    
    return app