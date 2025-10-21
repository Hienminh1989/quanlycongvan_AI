from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


class Document(db.Model):
    """Model cho các tài liệu/công văn"""
    __tablename__ = 'documents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)

    # Thông tin công văn
    document_type = db.Column(db.String(100), nullable=True)
    document_number = db.Column(db.String(100), nullable=True)
    sender = db.Column(db.String(255), nullable=True)
    receiver = db.Column(db.String(255), nullable=True)
    date_received = db.Column(db.DateTime, nullable=True)
    date_issued = db.Column(db.DateTime, nullable=True)

    # File
    file_path = db.Column(db.String(500), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    file_type = db.Column(db.String(50), nullable=True)

    # Metadata
    json_data = db.Column(db.JSON, nullable=True)
    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Quan hệ
    attachments = db.relationship('Attachment', backref='document', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content[:200] + '...' if self.content and len(self.content) > 200 else self.content,
            'document_type': self.document_type,
            'document_number': self.document_number,
            'sender': self.sender,
            'receiver': self.receiver,
            'date_received': self.date_received.isoformat() if self.date_received else None,
            'date_issued': self.date_issued.isoformat() if self.date_issued else None,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'attachments': [a.to_dict() for a in self.attachments]
        }


class Attachment(db.Model):
    """Model cho các file đính kèm"""
    __tablename__ = 'attachments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=False)

    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    file_type = db.Column(db.String(50), nullable=True)
    json_data = db.Column(db.JSON, nullable=True)  # Lưu nội dung extracted + thông tin khác

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=False)

    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    file_type = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'created_at': self.created_at.isoformat()
        }


class ChatMessage(db.Model):
    """Model cho lịch sử chat"""
    __tablename__ = 'chat_messages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    related_documents = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_message': self.user_message,
            'ai_response': self.ai_response,
            'related_documents': self.related_documents,
            'created_at': self.created_at.isoformat()
        }