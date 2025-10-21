#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════╗
║         FLASK APPLICATION - HỆ THỐNG QUẢN LÝ CÔNG VĂN         ║
║                       Version 1.0.0                            ║
╚════════════════════════════════════════════════════════════════╝
"""

import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

# ============ INITIALIZE FLASK ============

app = Flask(__name__)

# ============ LOAD CONFIGURATION ============

from config import get_config

# ✅ FIX: get_config() returns the CLASS, not an instance
ConfigClass = get_config()
app.config.from_object(ConfigClass)

print(f"[+] Configuration loaded: {ConfigClass.__name__}")

# ============ INITIALIZE DATABASE ============

from models import db

# ✅ FIX: Chỉ init_app một lần, kiểm tra trước
if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
    db.init_app(app)
    print("[+] Database initialized")
else:
    print("[+] Database already initialized")

# ============ SETUP CORS ============

CORS(app, resources={
    r"/api/*": {
        "origins": app.config['CORS_ORIGINS'],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
    }
})

print(f"[+] CORS enabled for: {app.config['CORS_ORIGINS']}")

# ============ REGISTER BLUEPRINTS ============

try:
    # Try to import from routes_enhanced first
    try:
        from routes_enhanced import api_bp

        print("[+] Loaded routes_enhanced.py")
    except ImportError:
        # Fallback to routes.py
        from routes import api_bp

        print("[+] Loaded routes.py")

    app.register_blueprint(api_bp)
    print("[+] API Blueprint registered")
except ImportError as e:
    print(f"[!] Error importing routes: {e}")
    sys.exit(1)

# ============ CREATE TABLES ============

with app.app_context():
    try:
        db.create_all()
        print("[+] Database tables created/verified")
    except Exception as e:
        print(f"[!] Error creating tables: {e}")
        sys.exit(1)


# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'status': 404
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'status': 500
    }), 500


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return jsonify({
        'success': False,
        'error': 'Bad request',
        'status': 400
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'status': 405
    }), 405


# ============ ROUTES ============

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'success': True,
        'message': 'Hệ Thống Quản Lý Công Văn',
        'version': '1.0.0',
        'api_base': 'http://localhost:5000/api',
        'endpoints': {
            'health': '/api/health',
            'documents': '/api/documents',
            'upload': '/api/upload',
            'search': '/api/search',
            'chat': '/api/chat',
            'statistics': '/api/statistics'
        }
    })


@app.route('/api')
def api_root():
    """API root endpoint"""
    return jsonify({
        'success': True,
        'message': 'API Server',
        'version': '1.0.0',
        'status': 'running'
    })


# ============ BEFORE REQUEST ============

@app.before_request
def before_request():
    """Run before each request"""
    pass


# ============ AFTER REQUEST ============

@app.after_request
def after_request(response):
    """Run after each request"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


# ============ MAIN ============

if __name__ == '__main__':
    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║         FLASK BACKEND SERVER - QUẢN LÝ CÔNG VĂN             ║")
    print("║                    Starting...                               ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False,
            use_debugger=True
        )
    except Exception as e:
        print(f"\n[!] Error starting app: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)