#!/usr/bin/env python3
"""
Configuration Module - Cấu hình cho Flask Application
Fix: Trả về class thay vì instance để tương thích với Flask
"""

import os
from datetime import timedelta
from pathlib import Path

# Get base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
DATABASE_FOLDER = os.path.join(BASE_DIR, 'database')

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATABASE_FOLDER, exist_ok=True)


class Config:
    """Base Configuration - Cấu hình cơ bản"""

    # ============ DATABASE ============
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_FOLDER}/documents.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # ============ FILE UPLOAD ============
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

    # ============ SECURITY ============
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production-12345')

    # ============ SESSION ============
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ============ CORS ============
    CORS_ORIGINS = [
        'http://localhost:5500',
        'http://localhost:3000',
        'http://127.0.0.1:5500',
        'http://127.0.0.1:3000',
    ]

    # ============ APPLICATION ============
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True


class DevelopmentConfig(Config):
    """Development Configuration - Phát triển"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # Log SQL queries


class ProductionConfig(Config):
    """Production Configuration - Sản xuất"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing Configuration - Test"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration class based on environment

    Args:
        env: Environment name (development, production, testing)

    Returns:
        Configuration class (NOT instance)
    """
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')

    # ✅ FIX: Return the class itself, not an instance
    config_class = config_dict.get(env, config_dict['default'])
    return config_class


# For direct access to config instances if needed
def get_config_instance(env=None):
    """
    Get configuration instance

    Args:
        env: Environment name

    Returns:
        Configuration instance
    """
    ConfigClass = get_config(env)
    return ConfigClass()


# Export
__all__ = ['Config', 'DevelopmentConfig', 'ProductionConfig', 'TestingConfig', 'get_config', 'get_config_instance']