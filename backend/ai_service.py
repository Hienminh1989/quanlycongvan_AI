#!/usr/bin/env python3
"""
AI Service Module - Xử lý tìm kiếm thông minh và Chat AI
Tích hợp hỗ trợ model mới nhất từ OpenAI, Local AI, etc.
"""

import re
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any


# Import models - sẽ được import khi cần để tránh circular import
def get_document_model():
    """Import Document model động để tránh circular import"""
    from models import Document
    return Document


class AIService:
    """Dịch vụ AI cho tìm kiếm thông minh và Chat"""

    # ============ SEARCH DOCUMENTS ============

    @staticmethod
    def search_documents(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Tìm kiếm thông minh văn bản - Phiên bản cơ bản

        Args:
            query: Từ khóa tìm kiếm
            limit: Số kết quả tối đa

        Returns:
            Danh sách tài liệu khớp với điểm số
        """
        if not query or not query.strip():
            return []

        try:
            from models import Document

            query_lower = query.lower()
            keywords = query_lower.split()

            documents = Document.query.all()
            results = []

            for doc in documents:
                score = 0
                matches = []

                # Tìm kiếm trong tiêu đề
                if any(kw in doc.title.lower() for kw in keywords):
                    score += 50

                # Tìm kiếm trong nội dung
                if doc.content:
                    content_lower = doc.content.lower()
                    for kw in keywords:
                        count = content_lower.count(kw)
                        if count > 0:
                            score += count * 10
                            idx = content_lower.find(kw)
                            snippet = doc.content[max(0, idx - 50):min(len(doc.content), idx + 100)]
                            matches.append({
                                'snippet': snippet.strip(),
                                'chunk_index': 0
                            })

                # Tìm kiếm trong metadata
                if doc.metadata:
                    if any(kw in str(doc.metadata).lower() for kw in keywords):
                        score += 20

                # Tìm kiếm trong số công văn
                if doc.document_number and any(kw in doc.document_number.lower() for kw in keywords):
                    score += 30

                if score > 0:
                    results.append({
                        'document': doc,
                        'score': score,
                        'matches': matches
                    })

            results = sorted(results, key=lambda x: x['score'], reverse=True)[:limit]
            return results

        except Exception as e:
            print(f"[ERROR] Search error: {str(e)}")
            return []

    @staticmethod
    def search_documents_enhanced(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Tìm kiếm nâng cao - tìm kiếm trong nội dung đầy đủ và file đính kèm

        Args:
            query: Từ khóa tìm kiếm
            limit: Số kết quả tối đa

        Returns:
            Danh sách tài liệu với điểm số và matched content
        """
        if not query or not query.strip():
            return []

        try:
            from models import Document

            query_lower = query.lower()
            keywords = query_lower.split()

            documents = Document.query.all()
            results = []

            for doc in documents:
                score = 0
                matches = []
                highlighted_content = ""

                # 1. Tìm kiếm trong tiêu đề (cao nhất)
                if any(kw in doc.title.lower() for kw in keywords):
                    score += 100

                # 2. Tìm kiếm trong nội dung chính (tối quan trọng)
                if doc.content:
                    content_lower = doc.content.lower()
                    for kw in keywords:
                        count = content_lower.count(kw)
                        if count > 0:
                            score += count * 20  # Tăng điểm số cho nội dung

                            # Lấy tất cả các đoạn khớp
                            start_idx = 0
                            match_count = 0
                            while match_count < 5:  # Giới hạn 5 đoạn mỗi từ khóa
                                idx = content_lower.find(kw, start_idx)
                                if idx == -1:
                                    break

                                snippet_start = max(0, idx - 100)
                                snippet_end = min(len(doc.content), idx + len(kw) + 100)
                                snippet = doc.content[snippet_start:snippet_end]

                                matches.append({
                                    'snippet': snippet.strip(),
                                    'chunk_index': match_count,
                                    'keyword': kw,
                                    'position': idx
                                })

                                start_idx = idx + len(kw)
                                match_count += 1

                # 3. Tìm kiếm trong file đính kèm
                for att in doc.attachments:
                    if att.metadata and att.metadata.get('content'):
                        att_content = att.metadata['content'].lower()
                        for kw in keywords:
                            if kw in att_content:
                                score += 30  # Điểm cho attachment
                                matches.append({
                                    'snippet': f"[Từ file đính kèm: {att.filename}]",
                                    'source': 'attachment',
                                    'filename': att.filename,
                                    'keyword': kw
                                })

                # 4. Tìm kiếm trong metadata
                if doc.metadata:
                    metadata_str = str(doc.metadata).lower()
                    for kw in keywords:
                        if kw in metadata_str:
                            score += 15

                # 5. Tìm kiếm trong số công văn
                if doc.document_number and any(kw in doc.document_number.lower() for kw in keywords):
                    score += 80

                # 6. Tìm kiếm trong người gửi
                if doc.sender and any(kw in doc.sender.lower() for kw in keywords):
                    score += 40

                if score > 0:
                    # Tạo nội dung với highlight
                    highlighted = doc.content if doc.content else ""
                    for kw in keywords:
                        highlighted = highlighted.replace(
                            kw,
                            f"<mark>{kw}</mark>"
                        )

                    results.append({
                        'document': doc,
                        'score': score,
                        'matches': matches[:10],  # Giới hạn 10 đoạn mỗi tài liệu
                        'highlighted_content': highlighted[:500] if highlighted else ""
                    })

            # Sắp xếp theo điểm số
            results = sorted(results, key=lambda x: x['score'], reverse=True)[:limit]
            return results

        except Exception as e:
            print(f"[ERROR] Enhanced search error: {str(e)}")
            return []

    # ============ PROCESS CHAT MESSAGE ============

    @staticmethod
    def process_chat_message(message: str) -> Tuple[str, List[Any]]:
        """
        Xử lý tin nhắn chat từ người dùng

        Args:
            message: Tin nhắn từ người dùng

        Returns:
            Tuple[response, related_documents]
        """
        try:
            message_lower = message.lower()

            # Nhận diện ý định người dùng
            intent = AIService._detect_intent(message_lower)

            if intent == 'search':
                # Trích xuất từ khóa tìm kiếm
                keywords = AIService._extract_keywords(message)
                results = AIService.search_documents(keywords, limit=5)

                response = f"Tôi tìm thấy {len(results)} kết quả liên quan đến '{keywords}':\n\n"

                for i, result in enumerate(results, 1):
                    doc = result['document']
                    response += f"{i}. {doc.title} "
                    if doc.document_number:
                        response += f"(Số: {doc.document_number})"
                    response += "\n"

                return response, [r['document'] for r in results]

            elif intent == 'statistics':
                from models import Document

                total_docs = Document.query.count()
                today = datetime.utcnow().date()
                today_docs = Document.query.filter(
                    Document.created_at >= datetime(today.year, today.month, today.day)
                ).count()

                response = f"📊 Thống kê hệ thống:\n"
                response += f"• Tổng số văn bản: {total_docs}\n"
                response += f"• Văn bản hôm nay: {today_docs}\n"
                response += f"• Công văn: {Document.query.filter_by(document_type='Công văn').count()}\n"
                response += f"• Quyết định: {Document.query.filter_by(document_type='Quyết định').count()}"

                return response, []

            elif intent == 'list':
                from models import Document

                docs = Document.query.order_by(Document.created_at.desc()).limit(5).all()

                response = "📋 Các văn bản gần đây:\n\n"
                for i, doc in enumerate(docs, 1):
                    response += f"{i}. {doc.title}\n"
                    if doc.sender:
                        response += f"   Từ: {doc.sender}\n"
                    if doc.date_received:
                        response += f"   Ngày: {doc.date_received.strftime('%d/%m/%Y')}\n"
                    response += "\n"

                return response, docs

            elif intent == 'help':
                response = """💡 Tôi có thể giúp bạn:

• "Tìm công văn về..." - Tìm kiếm văn bản
• "Thống kê" - Xem thống kê hệ thống
• "Danh sách" - Xem các văn bản gần đây
• "Tìm kiếm nâng cao" - Tìm kiếm chi tiết
• "Số lượng" - Đếm số văn bản

Bạn cũng có thể đặt bất kỳ câu hỏi nào về các văn bản!"""
                return response, []

            else:
                # Trả lời chung chung
                response = f"Xin lỗi, tôi không hiểu rõ: '{message}'\n\n"
                response += "Vui lòng thử:\n"
                response += "• 'Tìm công văn về...' - để tìm kiếm\n"
                response += "• 'Thống kê' - để xem thống kê\n"
                response += "• 'Danh sách' - để xem các văn bản gần đây"

                return response, []

        except Exception as e:
            print(f"[ERROR] Chat processing error: {str(e)}")
            return f"Đã xảy ra lỗi: {str(e)}", []

    # ============ INTENT DETECTION ============

    @staticmethod
    def _detect_intent(message: str) -> str:
        """
        Nhận diện ý định từ tin nhắn

        Args:
            message: Tin nhắn (đã chuyển thành lowercase)

        Returns:
            Intent type (search, statistics, list, help, general)
        """
        search_keywords = ['tìm', 'tìm kiếm', 'search', 'liên quan']
        stats_keywords = ['thống kê', 'statistics', 'số lượng', 'tổng', 'bao nhiêu']
        list_keywords = ['danh sách', 'list', 'xem', 'gần đây', 'mới nhất']
        help_keywords = ['giúp', 'help', 'làm gì', 'có thể gì', 'hỏi']

        if any(kw in message for kw in search_keywords):
            return 'search'
        elif any(kw in message for kw in stats_keywords):
            return 'statistics'
        elif any(kw in message for kw in list_keywords):
            return 'list'
        elif any(kw in message for kw in help_keywords):
            return 'help'

        return 'general'

    # ============ KEYWORD EXTRACTION ============

    @staticmethod
    def _extract_keywords(message: str) -> str:
        """
        Trích xuất từ khóa từ tin nhắn

        Args:
            message: Tin nhắn từ người dùng

        Returns:
            Chuỗi từ khóa
        """
        stopwords = ['tìm', 'tìm kiếm', 'search', 'công', 'văn', 'về', 'liên quan', 'có', 'là']

        words = message.lower().split()
        keywords = [w for w in words if w not in stopwords and len(w) > 2]

        return ' '.join(keywords) if keywords else message

    # ============ DOCUMENT ANALYSIS ============

    @staticmethod
    def analyze_document_sentiment(content: str) -> Dict[str, Any]:
        """
        Phân tích cảm xúc/tính chất của tài liệu

        Args:
            content: Nội dung tài liệu

        Returns:
            Dict với sentiment, score và indicators
        """
        if not content:
            return {'sentiment': 'neutral', 'score': 0}

        positive_words = ['quan trọng', 'khẩn', 'cần thiết', 'ưu tiên', 'thành công', 'hoàn thành']
        negative_words = ['hủy', 'từ chối', 'tạm dừng', 'lỗi', 'vấn đề']

        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)

        if positive_count > negative_count:
            sentiment = 'positive'
            score = min(positive_count / 10, 1.0)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = -min(negative_count / 10, 1.0)
        else:
            sentiment = 'neutral'
            score = 0

        return {
            'sentiment': sentiment,
            'score': score,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count
        }

    # ============ ENTITY EXTRACTION ============

    @staticmethod
    def extract_entities(text: str) -> Dict[str, Any]:
        """
        Trích xuất các thực thể từ văn bản (người, tổ chức, ngày tháng)

        Args:
            text: Văn bản input

        Returns:
            Dict chứa dates, organizations, numbers
        """
        entities = {
            'dates': [],
            'organizations': [],
            'numbers': []
        }

        try:
            # Tìm ngày tháng
            date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
            entities['dates'] = re.findall(date_pattern, text)

            # Tìm số
            number_pattern = r'\d+(?:\.\d+)?'
            entities['numbers'] = re.findall(number_pattern, text)

            # Tìm tổ chức
            org_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
            entities['organizations'] = list(set(re.findall(org_pattern, text)))[:10]

        except Exception as e:
            print(f"[ERROR] Entity extraction error: {str(e)}")

        return entities

    # ============ DOCUMENT SUMMARIZATION ============

    @staticmethod
    def generate_summary(text: str, max_length: int = 200) -> str:
        """
        Tạo tóm tắt từ văn bản

        Args:
            text: Văn bản input
            max_length: Độ dài tối đa của tóm tắt

        Returns:
            Tóm tắt văn bản
        """
        if not text or len(text) < max_length:
            return text

        sentences = text.split('.')
        summary_sentences = []
        total_length = 0

        for sentence in sentences:
            if total_length < max_length:
                summary_sentences.append(sentence.strip())
                total_length += len(sentence)
            else:
                break

        return '. '.join(summary_sentences) + '...'


# Export AIService
__all__ = ['AIService']