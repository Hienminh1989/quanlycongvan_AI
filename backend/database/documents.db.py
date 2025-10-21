#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════╗
║         DATABASE INITIALIZATION SCRIPT - KHỞI TẠO DỮ LIỆU        ║
║    Khởi tạo CSDL (PostgreSQL, SQLite, etc.) và thêm dữ liệu mẫu   ║
╚════════════════════════════════════════════════════════════════╝
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# ✅ FIX: Thêm thư mục gốc của dự án (thư mục cha của 'backend') vào sys.path.
# Đây là cách làm chuẩn để Python và IDE hiểu được cấu trúc package của bạn.
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# ✅ FIX: Bây giờ, import trực tiếp từ package 'backend'.
# LƯU Ý: Để cách làm này hoạt động tốt nhất, hãy đảm bảo bạn có một file trống
# tên là __init__.py trong thư mục 'backend' của mình.
from backend.app import app, db
from backend.models import Document, Attachment, ChatMessage

# Xác định thư mục UPLOADS một cách an toàn
UPLOADS_DIR = project_root / 'uploads'


def ensure_dummy_file_exists(filename, content):
    """
    Hàm này đảm bảo file mẫu tồn tại trong thư mục uploads.
    Nếu file chưa có, nó sẽ được tạo ra với nội dung được cung cấp.
    """
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOADS_DIR / filename

    if not file_path.exists():
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except IOError as e:
            print(f"    [!] Lỗi khi tạo file mẫu {filename}: {e}")

    # Trả về đường dẫn tương đối để lưu vào DB
    return str(file_path.relative_to(project_root))


def create_sample_data():
    """Tạo dữ liệu mẫu để test"""
    print("[*] Đang tạo dữ liệu mẫu...")

    with app.app_context():
        # Dữ liệu mẫu 1: Công văn về lương
        content1 = """Kính gửi: Toàn bộ cán bộ nhân viên

Năm 2024, công ty quyết định điều chỉnh lương cơ bản cho tất cả nhân viên.
Mức điều chỉnh dựa trên kết quả đánh giá năm 2023 và hiệu suất công việc.

Trân trọng,
Ban Quản Lý Nhân Sự"""
        doc1 = Document(
            id=str(uuid.uuid4()),
            title="Công Văn Về Điều Chỉnh Lương Năm 2024",
            content=content1,
            document_type="Công văn",
            document_number="CV-2024-001",
            sender="Ban Nhân Sự",
            receiver="Toàn bộ nhân viên",
            date_issued=datetime.utcnow() - timedelta(days=15),
            file_name="CongVan_Luong_2024.txt",
            file_type="txt",
            metadata={"tags": ["lương", "nhân sự", "2024"], "priority": "Khẩn"}
        )
        doc1.file_path = ensure_dummy_file_exists(doc1.file_name, doc1.content)
        doc1.file_size = (project_root / doc1.file_path).stat().st_size
        db.session.add(doc1)

        # Dữ liệu mẫu 2: Quyết định về kỳ nghỉ
        content2 = """QUYẾT ĐỊNH
Về việc phê duyệt kế hoạch kỳ nghỉ hè năm 2024 cho toàn công ty.
Thời gian nghỉ bắt đầu từ 01/06/2024.
Tổng Giám Đốc"""
        doc2 = Document(
            id=str(uuid.uuid4()),
            title="Quyết Định Phê Duyệt Kế Hoạch Kỳ Nghỉ Hè 2024",
            content=content2,
            document_type="Quyết định",
            document_number="QĐ-2024-015",
            sender="Ban Tổng Giám Đốc",
            receiver="Toàn bộ phòng ban",
            date_issued=datetime.utcnow() - timedelta(days=7),
            file_name="QuyetDinh_NghiHe_2024.txt",
            file_type="txt",
            metadata={"tags": ["nghỉ phép", "hè", "quyết định"], "priority": "Rất khẩn"}
        )
        doc2.file_path = ensure_dummy_file_exists(doc2.file_name, doc2.content)
        doc2.file_size = (project_root / doc2.file_path).stat().st_size
        db.session.add(doc2)

        # Dữ liệu mẫu 3: Hợp đồng mẫu
        content3 = """HỢP ĐỒNG LAO ĐỘNG
Xác định thời hạn năm 2024
Bên A: Công Ty ABC
Bên B: [Tên nhân viên]
Nội dung chính: Vị trí công việc, Mức lương, Thời hạn hợp đồng."""
        doc3 = Document(
            id=str(uuid.uuid4()),
            title="Hợp Đồng Lao Động Xác Định Thời Hạn 2024",
            content=content3,
            document_type="Hợp đồng",
            document_number="HĐLD-2024-0001",
            sender="Ban Pháp Chế",
            receiver="Nhân viên mới",
            date_issued=datetime.utcnow() - timedelta(days=25),
            file_name="HopDong_Mau_2024.txt",
            file_type="txt",
            metadata={"tags": ["hợp đồng", "lao động", "mẫu"], "priority": "Normal"}
        )
        doc3.file_path = ensure_dummy_file_exists(doc3.file_name, doc3.content)
        doc3.file_size = (project_root / doc3.file_path).stat().st_size
        db.session.add(doc3)

        db.session.commit()
        print("    [+] Đã tạo 3 tài liệu mẫu và các file vật lý tương ứng.")

        create_sample_chats()


def create_sample_chats():
    """Tạo lịch sử chat mẫu"""
    print("[*] Đang tạo lịch sử chat mẫu...")

    with app.app_context():
        chats = [
            ChatMessage(
                id=str(uuid.uuid4()),
                session_id="default",
                user_message="Tìm công văn về lương",
                ai_response="Tôi tìm thấy 1 kết quả liên quan: 'Công Văn Về Điều Chỉnh Lương Năm 2024'.",
                created_at=datetime.utcnow() - timedelta(hours=5)
            ),
            ChatMessage(
                id=str(uuid.uuid4()),
                session_id="default",
                user_message="Kỳ nghỉ hè khi nào bắt đầu?",
                ai_response="Theo quyết định QĐ-2024-015, kỳ nghỉ hè bắt đầu từ ngày 01/06/2024.",
                created_at=datetime.utcnow() - timedelta(hours=3)
            )
        ]

        db.session.add_all(chats)
        db.session.commit()
        print("    [+] Đã tạo 2 tin nhắn chat mẫu.")


def print_summary():
    """In tóm tắt database"""
    print("\n[+] Tóm tắt dữ liệu Database:")
    print("    ╔════════════════════════════════════════╗")

    with app.app_context():
        doc_count = Document.query.count()
        chat_count = ChatMessage.query.count()
        total_size = sum(d.file_size for d in Document.query.all() if d.file_size)
        size_kb = total_size / 1024

        print(f"    ║ Documents: {doc_count:<28} ║")
        print(f"    ║ Chat Messages: {chat_count:<21} ║")
        print(f"    ║ Total Size: {size_kb:<24.2f} KB ║")
        print("    ╚════════════════════════════════════════╝")


def main():
    """Hàm chính điều khiển script."""
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║         DATABASE INITIALIZATION - KHỞI TẠO CƠ SỞ DỮ LIỆU       ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    try:
        with app.app_context():
            print("[*] Bắt đầu quá trình khởi tạo cơ sở dữ liệu...")
            print("    [!] Sẽ xoá toàn bộ dữ liệu cũ (drop all tables)...")
            db.drop_all()
            print("    [+] Đã xoá các bảng cũ.")

            db.create_all()
            print("    [+] Đã tạo cấu trúc bảng mới.")

        create_sample_data()
        print_summary()

        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"\n[+] Đã kết nối và khởi tạo dữ liệu cho database:")
        safe_uri = db_uri.split('@')[-1] if '@' in db_uri else db_uri
        print(f"    HOST/DB: {safe_uri}")

        print(f"[+] Thư mục uploads tại: {UPLOADS_DIR.resolve()}")
        print("\n[✓] Khởi tạo thành công!\n")

    except Exception as e:
        import traceback
        print(f"\n[✗] Lỗi nghiêm trọng xảy ra: {str(e)}\n")
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()