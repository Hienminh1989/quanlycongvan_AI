#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════╗
║     HỆ THỐNG QUẢN LÝ CÔNG VĂN - DOCUMENT MANAGEMENT SYSTEM    ║
║                       Version 1.0.0                            ║
║                                                                ║
║  Chạy từ: python main.py                                     ║
║  Frontend: http://localhost:5500                             ║
║  Backend:  http://localhost:5000                             ║
╚════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import signal
import subprocess
import time
import webbrowser
import urllib.request  # FIX: Di chuyển import lên đầu
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class DocumentManagementSystem:
    """Main application controller"""

    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / 'backend'
        self.frontend_dir = self.root_dir / 'frontend'
        # FIX: Sửa lại tên thư mục venv tiêu chuẩn là .venv
        self.venv_dir = self.root_dir / '.venv'
        self.processes = []
        self.config = self._load_config()

        # FIX: Xác định đường dẫn chính xác tới python.exe trong venv
        if sys.platform == "win32":
            self.python_executable = self.venv_dir / 'Scripts' / 'python.exe'
        else:
            self.python_executable = self.venv_dir / 'bin' / 'python'

    def _load_config(self):
        """Load configuration"""
        return {
            'backend': {'host': '0.0.0.0', 'port': 5000, 'debug': True, 'url': 'http://localhost:5000'},
            'frontend': {'port': 5500, 'url': 'http://localhost:5500'},
            'database': {'path': str(self.backend_dir / 'database' / 'documents.db')}
        }

    def print_banner(self):
        """Print welcome banner"""
        print(f"\n{Fore.CYAN}╔{'═' * 62}╗{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL}{Fore.YELLOW}{'HỆ THỐNG QUẢN LÝ CÔNG VĂN':^62}{Fore.CYAN}║{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL}{Fore.GREEN}{'Document Management System':^62}{Fore.CYAN}║{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL}{Fore.MAGENTA}{'Version 1.0.0 - Professional Edition':^62}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 62}╝{Style.RESET_ALL}\n")

    def check_requirements(self):
        """Check system requirements"""
        print(f"{Fore.YELLOW}[*] Kiểm tra yêu cầu hệ thống...{Style.RESET_ALL}")
        checks = {
            'Python 3.8+': self._check_python(),
            'pip': self._check_pip(),
            'Backend Folder': self.backend_dir.exists(),
            'Frontend Folder': self.frontend_dir.exists(),
            'Virtual Environment (.venv)': self._check_venv()
        }
        for check, status in checks.items():
            icon = f"{Fore.GREEN}✓" if status else f"{Fore.RED}✗"
            print(f"  {icon} {check}{Style.RESET_ALL}")
        if not all(checks.values()):
            print(
                f"\n{Fore.RED}[!] Một số kiểm tra không thành công! Hãy tạo môi trường ảo tên là '.venv'.{Style.RESET_ALL}")
            return False
        print(f"{Fore.GREEN}[+] Tất cả kiểm tra thành công!{Style.RESET_ALL}\n")
        return True

    def _check_python(self):
        return sys.version_info >= (3, 8)

    def _check_pip(self):
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_venv(self):
        # FIX: Kiểm tra cả sự tồn tại của file thực thi python trong venv
        return self.venv_dir.exists() and self.python_executable.exists()

    def setup_environment(self):
        """Setup project environment"""
        print(f"{Fore.YELLOW}[*] Thiết lập môi trường...{Style.RESET_ALL}")
        dirs = [self.backend_dir / 'database', self.root_dir / 'uploads']
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} Đã tạo thư mục: {dir_path.relative_to(self.root_dir)}")

        env_file = self.backend_dir / '.env'
        if not env_file.exists():
            env_content = (f"FLASK_ENV=development\nFLASK_APP=app.py\n"
                           f"SECRET_KEY=dev-secret-key-change-in-production\n"
                           f"DATABASE_URL=sqlite:///{self.config['database']['path']}\n"
                           f"CORS_ORIGINS={self.config['frontend']['url']}")
            env_file.write_text(env_content)
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} Đã tạo file .env")
        print(f"{Fore.GREEN}[+] Môi trường đã sẵn sàng!{Style.RESET_ALL}\n")

    def check_dependencies(self):
        """Check and install dependencies using venv's pip"""
        print(f"{Fore.YELLOW}[*] Cài đặt dependencies vào .venv...{Style.RESET_ALL}")
        requirements_file = self.backend_dir / 'requirements.txt'
        if not requirements_file.exists():
            print(f"{Fore.RED}[!] Không tìm thấy {requirements_file}{Style.RESET_ALL}")
            return False
        try:
            # FIX: Sử dụng python từ venv để chạy pip, đảm bảo cài đúng nơi
            process = subprocess.run(
                [str(self.python_executable), '-m', 'pip', 'install', '-r', str(requirements_file)],
                capture_output=True, text=True, timeout=300, check=True
            )
            print(f"{Fore.GREEN}[+] Dependencies đã được cài đặt!{Style.RESET_ALL}\n")
            return True
        except subprocess.CalledProcessError as e:
            # FIX: In ra lỗi chi tiết để người dùng dễ dàng debug
            print(f"{Fore.RED}[!] Lỗi khi cài đặt dependencies:{Style.RESET_ALL}")
            print(e.stderr)
            return False
        except Exception as e:
            print(f"{Fore.RED}[!] Lỗi không xác định: {e}{Style.RESET_ALL}")
            return False

    def start_backend(self):
        """Start Flask backend server using venv's python"""
        print(f"{Fore.YELLOW}[*] Khởi động Backend Server...{Style.RESET_ALL}")
        try:
            # FIX: Chạy app.py bằng python từ venv
            process = subprocess.Popen(
                [str(self.python_executable), 'app.py'],
                cwd=str(self.backend_dir),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            self.processes.append(process)
            time.sleep(2)
            if process.poll() is not None:
                print(f"{Fore.RED}[!] Backend không thể khởi động. Lỗi:{Style.RESET_ALL}")
                print(process.stderr.read())
                return False
            print(f"{Fore.GREEN}[+] Backend Server: {self.config['backend']['url']}{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Lỗi khởi động Backend: {e}{Style.RESET_ALL}\n")
            return False

    def start_frontend(self):
        """Start Frontend with Python's http.server"""
        print(f"{Fore.YELLOW}[*] Khởi động Frontend Server...{Style.RESET_ALL}")
        try:
            # FIX: Chạy http.server bằng python hệ thống là đủ
            process = subprocess.Popen(
                [sys.executable, '-m', 'http.server', str(self.config['frontend']['port']), '--bind', '127.0.0.1'],
                cwd=str(self.frontend_dir),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            self.processes.append(process)
            time.sleep(1)
            print(f"{Fore.GREEN}[+] Frontend Server: {self.config['frontend']['url']}{Style.RESET_ALL}\n")
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Lỗi khởi động Frontend: {e}{Style.RESET_ALL}\n")
            return False

    def wait_for_services(self):
        """Wait for services to be ready"""
        print(f"{Fore.YELLOW}[*] Chờ dịch vụ backend sẵn sàng...{Style.RESET_ALL}")
        for attempt in range(10):
            try:
                urllib.request.urlopen(f"{self.config['backend']['url']}/api/health", timeout=2)
                print(f"{Fore.GREEN}[+] Backend đã sẵn sàng!{Style.RESET_ALL}\n")
                return
            except Exception:
                time.sleep(1)
                print(f"  Thử lại... ({attempt + 1}/10)")
        print(f"{Fore.RED}[!] Không thể kết nối tới backend!{Style.RESET_ALL}\n")

    def open_browser(self):
        """Open application in default browser"""
        try:
            print(f"{Fore.YELLOW}[*] Mở ứng dụng trong trình duyệt...{Style.RESET_ALL}")
            webbrowser.open(self.config['frontend']['url'])
        except Exception:
            print(
                f"{Fore.YELLOW}[!] Không thể mở trình duyệt. Hãy truy cập thủ công:{Style.RESET_ALL} {self.config['frontend']['url']}")

    def print_status(self):
        """Print system status"""
        # FIX: Sửa lỗi f-string và căn lề
        print(f"{Fore.CYAN}╔{'═' * 62}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}{Fore.GREEN}{'SYSTEM STATUS':^62}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠{'═' * 62}╣{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{'✓ Backend Server:':<22}{Style.RESET_ALL} {self.config['backend']['url']:<38} {Fore.CYAN}║{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{'✓ Frontend Server:':<22}{Style.RESET_ALL} {self.config['frontend']['url']:<38} {Fore.CYAN}║{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}{'✓ Database:':<22}{Style.RESET_ALL} {'SQLite (documents.db)':<38} {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠{'═' * 62}╣{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{'Bấm CTRL+C để dừng ứng dụng':^62} {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 62}╝{Style.RESET_ALL}\n")

    def handle_signal(self, sig, frame):
        print(f"\n{Fore.YELLOW}[*] Đang dừng các dịch vụ...{Style.RESET_ALL}")
        self.cleanup()
        print(f"{Fore.GREEN}[+] Ứng dụng đã dừng!{Style.RESET_ALL}")
        sys.exit(0)

    def cleanup(self):
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except Exception:
                process.kill()

    def run(self):
        """Main entry point"""
        signal.signal(signal.SIGINT, self.handle_signal)
        try:
            self.print_banner()
            if not self.check_requirements(): sys.exit(1)
            self.setup_environment()
            if not self.check_dependencies(): sys.exit(1)
            if not self.start_backend() or not self.start_frontend(): sys.exit(1)
            self.wait_for_services()
            self.print_status()
            self.open_browser()
            print(f"{Fore.CYAN}{'─' * 64}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Hệ thống đang chạy. Logs sẽ hiển thị nếu có lỗi.{Style.RESET_ALL}")
            while True:
                time.sleep(5)  # Giảm tải CPU
        except KeyboardInterrupt:
            self.handle_signal(None, None)
        except Exception as e:
            print(f"{Fore.RED}[!] Lỗi nghiêm trọng: {e}{Style.RESET_ALL}")
            self.cleanup()
            sys.exit(1)


if __name__ == '__main__':
    app = DocumentManagementSystem()
    app.run()