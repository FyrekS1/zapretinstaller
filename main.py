import customtkinter as ctk
import threading
import os
import subprocess
import time
import psutil
import requests
import rarfile
import ctypes
import sys
from tkinter import messagebox

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

ARCHIVE_URL = "https://github.com/Flowseal/zapret-discord-youtube/releases/download/1.8.3/zapret-discord-youtube-1.8.3.rar"
TEMP_DIR = os.path.join(os.environ["TEMP"], "FyrekS")
ARCHIVE_PATH = os.path.join(TEMP_DIR, os.path.basename(ARCHIVE_URL))
LOCAL_VERSION = "1.8.3"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/Flowseal/zapret-discord-youtube/main/.service/version.txt"
GITHUB_RELEASE_URL = "https://github.com/Flowseal/zapret-discord-youtube/releases/tag/"
GITHUB_DOWNLOAD_URL = "https://github.com/Flowseal/zapret-discord-youtube/releases/latest/download/zapret-discord-youtube-"
IPSET_URL = "https://raw.githubusercontent.com/Flowseal/zapret-discord-youtube/refs/heads/main/.service/ipset-service.txt"


class ZapretApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Zapret Discord YouTube Bypass")
        self.geometry("900x700")

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=20)

        self.main_tab = self.tab_view.add("Главная")
        self.service_tab = self.tab_view.add("Сервис")
        self.diagnostics_tab = self.tab_view.add("Диагностика")
        self.settings_tab = self.tab_view.add("Настройки")

        self.init_main_tab()
        self.init_service_tab()
        self.init_diagnostics_tab()
        self.init_settings_tab()

        self.game_filter_status = "disabled"
        self.ipset_status = "loaded"
        self.update_status_vars()

    def update_status_vars(self):
        

        game_flag_file = os.path.join(TEMP_DIR, "bin", "game_filter.enabled")
        if os.path.exists(game_flag_file):
            self.game_filter_status = "enabled"
        else:
            self.game_filter_status = "disabled"

        ipset_file = os.path.join(TEMP_DIR, "lists", "ipset-all.txt")
        if os.path.exists(ipset_file):
            with open(ipset_file, "r") as f:
                content = f.read().strip()
                if content == "0.0.0.0/32":
                    self.ipset_status = "empty"
                else:
                    self.ipset_status = "loaded"

    def log(self, msg, color=None):
        
        self.logbox.configure(state="normal")
        self.logbox.insert("end", msg + "\n")
        if color:
            start_index = self.logbox.index("end-2c linestart")
            end_index = self.logbox.index("end-1c")
            self.logbox.tag_add(color, start_index, end_index)
        self.logbox.configure(state="disabled")
        self.logbox.see("end")

    def run_as_admin(self):
        
        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                return True
            else:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                return False
        except:
            return False

    def init_main_tab(self):
        frame = ctk.CTkFrame(self.main_tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.logbox = ctk.CTkTextbox(frame, width=850, height=400)
        self.logbox.pack(pady=10)
        self.logbox.tag_config("green", foreground="#2ECC71")
        self.logbox.tag_config("red", foreground="#E74C3C")
        self.logbox.tag_config("yellow", foreground="#F39C12")
        self.logbox.configure(state="disabled")

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=10)

        self.download_btn = ctk.CTkButton(
            btn_frame,
            text="Скачать архив",
            command=lambda: threading.Thread(target=self.download_archive).start()
        )
        self.download_btn.grid(row=0, column=0, padx=10)

        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="Запустить проверку",
            command=lambda: threading.Thread(target=self.run_bats).start()
        )
        self.start_btn.grid(row=0, column=1, padx=10)

        self.status_btn = ctk.CTkButton(
            btn_frame,
            text="Проверить статус",
            command=lambda: self.check_service_status()
        )
        self.status_btn.grid(row=0, column=2, padx=10)

    def check_bypass(self):
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        try:
            r = requests.get(url, stream=True, timeout=5, verify=False)
            total = 0
            for chunk in r.iter_content(1024 * 64):
                total += len(chunk)
                if total > 1024 * 1024:
                    break
            self.log(f"Скачано {total / 1024:.1f} KB — поток идёт", "green")
            return True
        except Exception as e:
            self.log(f"Ошибка: {e}", "red")
            return False

    def kill_winws(self):
        
        process_name = "winws.exe"
        for proc in psutil.process_iter():
            try:
                if proc.name() == process_name:
                    proc.kill()
                    self.log(f"Процесс '{process_name}' завершен.", "green")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def count_bats(self):
        
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        bat_files = [f for f in os.listdir(TEMP_DIR) if f.lower().endswith(".bat")]
        self.log("Найденные .bat файлы:")
        for f in bat_files:
            self.log(os.path.join(TEMP_DIR, f))
        return bat_files

    def run_bats(self):
        
        self.log("\n=== Начало проверки батников ===")
        bat_files = self.count_bats()
        working_bat = None

        for bat in bat_files:
            bat_path = os.path.join(TEMP_DIR, bat)
            self.log(f"\n▶ Запускаю {bat_path} ...")
            try:
                subprocess.Popen(bat_path, shell=True)
                time.sleep(5)

                if self.check_bypass():
                    self.log(f"✅ Рабочий батник: {bat}", "green")
                    working_bat = bat
                    break
                else:
                    self.log(f"⚠ Не сработал: {bat}, завершаю процесс...", "yellow")
                    self.kill_winws()
            except Exception as e:
                self.log(f"Ошибка при запуске батника: {e}", "red")

        if working_bat:
            self.log("\n=== Найден рабочий батник ===", "green")
        else:
            self.log("\n=== Рабочий батник не найден ===", "red")

    def download_archive(self):
        
        self.log("\n=== Скачивание архива ===")

        if os.path.exists(ARCHIVE_PATH):
            self.log(f"⚠ Архив уже скачан: {ARCHIVE_PATH}", "yellow")
            return

        os.makedirs(TEMP_DIR, exist_ok=True)
        self.log(f"Скачиваю архив в {ARCHIVE_PATH} ...")

        try:
            r = requests.get(ARCHIVE_URL, stream=True)
            r.raise_for_status()

            with open(ARCHIVE_PATH, "wb") as f:
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                chunk_size = 8192

                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress = int(50 * downloaded / total_size)
                    self.log(
                        f"Прогресс: [{'=' * progress}{' ' * (50 - progress)}] {downloaded / 1024 / 1024:.1f}/{total_size / 1024 / 1024:.1f} MB",
                        "green")

            self.log("✅ Архив скачан.", "green")
            self.log(f"Распаковываю архив в {TEMP_DIR} ...")

            with rarfile.RarFile(ARCHIVE_PATH) as rf:
                rf.extractall(TEMP_DIR)

            self.log(f"✅ Распаковка завершена. Файлы в {TEMP_DIR}", "green")
        except Exception as e:
            self.log(f"Ошибка при скачивании/распаковке: {e}", "red")

    def init_service_tab(self):
        frame = ctk.CTkFrame(self.service_tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=10, fill="x")

        self.install_btn = ctk.CTkButton(
            btn_frame,
            text="Установить сервис",
            command=lambda: threading.Thread(target=self.install_service).start()
        )
        self.install_btn.grid(row=0, column=0, padx=5, pady=5)

        self.remove_btn = ctk.CTkButton(
            btn_frame,
            text="Удалить сервис",
            command=lambda: threading.Thread(target=self.remove_service).start()
        )
        self.remove_btn.grid(row=0, column=1, padx=5, pady=5)

        self.status_btn = ctk.CTkButton(
            btn_frame,
            text="Проверить статус",
            command=lambda: self.check_service_status()
        )
        self.status_btn.grid(row=0, column=2, padx=5, pady=5)

        self.diag_btn = ctk.CTkButton(
            btn_frame,
            text="Диагностика",
            command=lambda: threading.Thread(target=self.run_diagnostics).start()
        )
        self.diag_btn.grid(row=0, column=3, padx=5, pady=5)

        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="Проверить обновления",
            command=lambda: threading.Thread(target=self.check_updates).start()
        )
        self.update_btn.grid(row=0, column=4, padx=5, pady=5)

        self.service_log = ctk.CTkTextbox(frame, width=850, height=300)
        self.service_log.pack(pady=10)
        self.service_log.tag_config("green", foreground="#2ECC71")
        self.service_log.tag_config("red", foreground="#E74C3C")
        self.service_log.tag_config("yellow", foreground="#F39C12")
        self.service_log.configure(state="disabled")

    def service_log_message(self, msg, color=None):
        self.service_log.configure(state="normal")
        self.service_log.insert("end", msg + "\n")
        if color:
            start_index = self.service_log.index("end-2c linestart")
            end_index = self.service_log.index("end-1c")
            self.service_log.tag_add(color, start_index, end_index)
        self.service_log.configure(state="disabled")
        self.service_log.see("end")

    def install_service(self, *args):
        try:
            if not self.run_as_admin():
                self.service_log_message("Требуются права администратора", "red")
                return

            bat_files = [f for f in os.listdir(TEMP_DIR)
                         if f.lower().endswith('.bat')
                         and not f.lower().startswith('service')]

            if not bat_files:
                self.service_log_message("Не найдено .bat файлов для проверки", "red")
                return

            self.service_log_message("\n=== Поиск рабочего .bat файла ===")
            working_bat = None
            winws_args = ""

            for bat in bat_files:
                bat_path = os.path.join(TEMP_DIR, bat)
                self.service_log_message(f"\nТестируем файл: {bat}")

                try:
                    process = subprocess.Popen(bat_path, shell=True)
                    time.sleep(5)  # Ожидаем запуска

                    if self.check_bypass():
                        working_bat = bat_path
                        self.service_log_message("Успешно! Определяем параметры...", "green")

                        winws_pid = None
                        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                            if proc.info['name'] == 'winws.exe':
                                winws_pid = proc.info['pid']
                                cmdline = proc.info['cmdline']
                                if cmdline:
                                    winws_args = ' '.join(cmdline[1:])  # Берем аргументы без пути к exe
                                break

                        self.kill_winws()

                        if winws_args:
                            self.service_log_message(f"Найдены параметры: {winws_args}", "green")
                            break
                        else:
                            self.service_log_message("Не удалось определить параметры", "yellow")
                    else:
                        self.service_log_message("Не работает", "yellow")
                        self.kill_winws()

                except Exception as e:
                    self.service_log_message(f"Ошибка тестирования: {str(e)}", "red")
                    self.kill_winws()

            if not working_bat or not winws_args:
                self.service_log_message("\nРабочий .bat файл не найден!", "red")
                return

            bin_path = os.path.join(TEMP_DIR, "bin", "winws.exe")

            full_command = f'"{bin_path}" {winws_args}'
            self.service_log_message(f"\nСоздаем службу с командой:\n{full_command}")

            subprocess.run(['sc', 'delete', 'zapret'], stderr=subprocess.DEVNULL)
            time.sleep(1)

            cmd = [
                'sc', 'create', 'zapret',
                'binPath=', full_command,
                'DisplayName=', 'zapret',
                'start=', 'auto',
                'obj=', 'LocalSystem'
            ]
            subprocess.run(cmd, check=True)

            subprocess.run([
                'sc', 'failure', 'zapret',
                'reset=', '60',
                'actions=', 'restart/5000/restart/5000/restart/5000'
            ], check=True)

            time.sleep(2)
            subprocess.run(['sc', 'start', 'zapret'], check=True)

            time.sleep(3)
            result = subprocess.run(['sc', 'query', 'zapret'], capture_output=True, text=True)

            if "RUNNING" in result.stdout:
                self.service_log_message("\nСлужба успешно запущена!", "green")
            else:
                self.service_log_message("\nСлужба создана, но не запустилась", "yellow")
                self.service_log_message(result.stdout)

        except subprocess.CalledProcessError as e:
            error_msg = f"Ошибка (код {e.returncode}): {e.stderr.decode('cp1251') if e.stderr else str(e)}"
            self.service_log_message(f"\nОшибка установки: {error_msg}", "red")

            self.service_log_message("\nДиагностика:")
            if not os.path.exists(os.path.join(TEMP_DIR, "bin", "winws.exe")):
                self.service_log_message("Файл winws.exe не найден!", "red")

        except Exception as e:
            self.service_log_message(f"\nКритическая ошибка: {str(e)}", "red")
    def remove_service(self, *args):
        
        try:
            if not self.run_as_admin():
                self.service_log_message("Требуются права администратора", "red")
                return

            services = ["zapret", "WinDivert", "WinDivert14"]
            for service in services:
                try:
                    subprocess.run(['net', 'stop', service], check=True)
                    self.service_log_message(f"Сервис {service} остановлен", "green")
                except subprocess.CalledProcessError:
                    self.service_log_message(f"Сервис {service} не запущен или не существует", "yellow")

                try:
                    subprocess.run(['sc', 'delete', service], check=True)
                    self.service_log_message(f"Сервис {service} удален", "green")
                except subprocess.CalledProcessError:
                    self.service_log_message(f"Ошибка удаления сервиса {service}", "red")

            self.service_log_message("Операция удаления сервисов завершена", "green")

        except Exception as e:
            self.service_log_message(f"Ошибка удаления сервисов: {e}", "red")

    def check_service_status(self, *args):
        
        self.service_log_message("\n=== Проверка статуса сервисов ===")

        try:

            result = subprocess.run(['sc', 'query', 'zapret'], capture_output=True, text=True)
            if "RUNNING" in result.stdout:
                self.service_log_message("Сервис zapret: ЗАПУЩЕН", "green")
            else:
                self.service_log_message("Сервис zapret: НЕ ЗАПУЩЕН", "red")

            result = subprocess.run(['sc', 'query', 'WinDivert'], capture_output=True, text=True)
            if "RUNNING" in result.stdout:
                self.service_log_message("Сервис WinDivert: ЗАПУЩЕН", "green")
            else:
                self.service_log_message("Сервис WinDivert: НЕ ЗАПУЩЕН", "red")

            running = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == 'winws.exe':
                    running = True
                    break

            if running:
                self.service_log_message("Процесс winws.exe: ЗАПУЩЕН", "green")
            else:
                self.service_log_message("Процесс winws.exe: НЕ ЗАПУЩЕН", "red")

        except Exception as e:
            self.service_log_message(f"Ошибка проверки статуса: {e}", "red")

    def run_diagnostics(self, *args):
        
        self.service_log_message("\n=== Запуск диагностики ===")

        conflicts = {
            "Adguard": ("AdguardSvc.exe", "https://github.com/Flowseal/zapret-discord-youtube/issues/417"),
            "Killer": ("Killer",
                       "https://github.com/Flowseal/zapret-discord-youtube/issues/2512#issuecomment-2821119513"),
            "Intel": ("Intel Connectivity Network Service",
                      "https://github.com/ValdikSS/GoodbyeDPI/issues/541#issuecomment-2661670982"),
            "CheckPoint": ("TracSrvWrapper", "https://github.com/Flowseal/zapret-discord-youtube/issues/"),
            "SmartByte": ("SmartByte", "https://github.com/Flowseal/zapret-discord-youtube/issues/"),
            "VPN": ("VPN", "https://github.com/Flowseal/zapret-discord-youtube/issues/")
        }

        all_ok = True
        result = subprocess.run(['sc', 'query'], capture_output=True, text=True)
        services_output = result.stdout

        for name, (pattern, url) in conflicts.items():
            if pattern in services_output:
                self.service_log_message(f"[X] Обнаружен конфликт: {name}", "red")
                self.service_log_message(f"    Решение: {url}", "yellow")
                all_ok = False
            else:
                self.service_log_message(f"[✓] {name}: конфликтов не обнаружено", "green")

        if all_ok:
            self.service_log_message("Все проверки на конфликты пройдены успешно", "green")

        self.service_log_message("\nОчистка кеша Discord...")
        discord_cache = os.path.join(os.getenv('APPDATA'), 'discord')
        cache_dirs = ["Cache", "Code Cache", "GPUCache"]

        for cache_dir in cache_dirs:
            dir_path = os.path.join(discord_cache, cache_dir)
            if os.path.exists(dir_path):
                try:
                    subprocess.run(['rmdir', '/s', '/q', dir_path], shell=True)
                    self.service_log_message(f"Удалено: {dir_path}", "green")
                except Exception as e:
                    self.service_log_message(f"Ошибка удаления {dir_path}: {e}", "red")
            else:
                self.service_log_message(f"Директория не найдена: {dir_path}", "yellow")

    def check_updates(self, *args):
        
        self.service_log_message("\n=== Проверка обновлений ===")

        try:
            response = requests.get(GITHUB_VERSION_URL, timeout=5)
            github_version = response.text.strip()

            if github_version == LOCAL_VERSION:
                self.service_log_message(f"Установлена последняя версия: {LOCAL_VERSION}", "green")
            else:
                self.service_log_message(f"Доступна новая версия: {github_version}", "yellow")
                self.service_log_message(f"Текущая версия: {LOCAL_VERSION}", "yellow")
                self.service_log_message(f"Ссылка: {GITHUB_RELEASE_URL}{github_version}", "yellow")

                if messagebox.askyesno("Обновление", "Скачать новую версию?"):
                    download_url = f"{GITHUB_DOWNLOAD_URL}{github_version}.rar"
                    self.service_log_message(f"Скачивание: {download_url}")
                    threading.Thread(target=self.download_archive).start()

        except Exception as e:
            self.service_log_message(f"Ошибка проверки обновлений: {e}", "red")

    def init_diagnostics_tab(self):
        frame = ctk.CTkFrame(self.diagnostics_tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=10, fill="x")

        self.diag_btn = ctk.CTkButton(
            btn_frame,
            text="Запустить полную диагностику",
            command=lambda: threading.Thread(target=self.run_full_diagnostics).start()
        )
        self.diag_btn.grid(row=0, column=0, padx=5, pady=5)

        self.discord_btn = ctk.CTkButton(
            btn_frame,
            text="Очистить кеш Discord",
            command=lambda: threading.Thread(target=self.clear_discord_cache).start()
        )
        self.discord_btn.grid(row=0, column=1, padx=5, pady=5)

        self.diag_log = ctk.CTkTextbox(frame, width=850, height=400)
        self.diag_log.pack(pady=10)
        self.diag_log.tag_config("green", foreground="#2ECC71")
        self.diag_log.tag_config("red", foreground="#E74C3C")
        self.diag_log.tag_config("yellow", foreground="#F39C12")
        self.diag_log.configure(state="disabled")

    def diag_log_message(self, msg, color=None):
        
        self.diag_log.configure(state="normal")
        self.diag_log.insert("end", msg + "\n")
        if color:
            start_index = self.diag_log.index("end-2c linestart")
            end_index = self.diag_log.index("end-1c")
            self.diag_log.tag_add(color, start_index, end_index)
        self.diag_log.configure(state="disabled")
        self.diag_log.see("end")

    def run_full_diagnostics(self, *args):
        
        self.diag_log_message("\n=== Запуск полной диагностики ===")

        self.diag_log_message("\n[1] Проверка сервисов:")
        self.check_service_status_diag()

        self.diag_log_message("\n[2] Проверка сетевых параметров:")
        self.check_network_settings()

        self.diag_log_message("\n[3] Проверка конфликтующих процессов:")
        self.check_conflicting_processes()

        self.diag_log_message("\n[4] Проверка DNS:")
        self.check_dns_settings()

        self.diag_log_message("\n=== Диагностика завершена ===", "green")

    def check_service_status_diag(self, *args):
        
        try:

            result = subprocess.run(['sc', 'query', 'zapret'], capture_output=True, text=True)
            if "RUNNING" in result.stdout:
                self.diag_log_message("Сервис zapret: ЗАПУЩЕН", "green")
            else:
                self.diag_log_message("Сервис zapret: НЕ ЗАПУЩЕН", "red")

            result = subprocess.run(['sc', 'query', 'WinDivert'], capture_output=True, text=True)
            if "RUNNING" in result.stdout:
                self.diag_log_message("Сервис WinDivert: ЗАПУЩЕН", "green")
            else:
                self.diag_log_message("Сервис WinDivert: НЕ ЗАПУЩЕН", "red")

        except Exception as e:
            self.diag_log_message(f"Ошибка проверки статуса: {e}", "red")

    def check_network_settings(self, *args):
        
        try:

            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            self.diag_log_message("Сетевые интерфейсы:\n" + result.stdout)

            result = subprocess.run(['route', 'print'], capture_output=True, text=True)
            self.diag_log_message("Таблица маршрутизации:\n" + result.stdout)

            self.diag_log_message("Сетевые параметры проверены", "green")
        except Exception as e:
            self.diag_log_message(f"Ошибка проверки сетевых параметров: {e}", "red")

    def check_conflicting_processes(self, *args):
        
        conflicts = {
            "Adguard": "AdguardSvc.exe",
            "Killer": "KillerService.exe",
            "VPN": "vpnui.exe",
            "Antivirus": "avp.exe"
        }

        all_ok = True
        for name, process in conflicts.items():
            found = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == process:
                    found = True
                    break

            if found:
                self.diag_log_message(f"[X] Обнаружен конфликт: {name} ({process})", "red")
                all_ok = False
            else:
                self.diag_log_message(f"[✓] {name}: не обнаружен", "green")

        if all_ok:
            self.diag_log_message("Конфликтующие процессы не обнаружены", "green")

    def check_dns_settings(self, *args):
        
        try:
            result = subprocess.run(['nslookup', 'youtube.com'], capture_output=True, text=True)
            self.diag_log_message("Результат nslookup youtube.com:\n" + result.stdout)

            if "answer" not in result.stdout.lower():
                self.diag_log_message("Возможные проблемы с DNS", "yellow")
            else:
                self.diag_log_message("DNS работает нормально", "green")
        except Exception as e:
            self.diag_log_message(f"Ошибка проверки DNS: {e}", "red")

    def clear_discord_cache(self, *args):
        
        self.diag_log_message("\nОчистка кеша Discord...")
        discord_cache = os.path.join(os.getenv('APPDATA'), 'discord')
        cache_dirs = ["Cache", "Code Cache", "GPUCache"]

        for cache_dir in cache_dirs:
            dir_path = os.path.join(discord_cache, cache_dir)
            if os.path.exists(dir_path):
                try:
                    subprocess.run(['rmdir', '/s', '/q', dir_path], shell=True)
                    self.diag_log_message(f"Удалено: {dir_path}", "green")
                except Exception as e:
                    self.diag_log_message(f"Ошибка удаления {dir_path}: {e}", "red")
            else:
                self.diag_log_message(f"Директория не найдена: {dir_path}", "yellow")

        self.diag_log_message("Очистка кеша Discord завершена", "green")

    def init_settings_tab(self):
        frame = ctk.CTkFrame(self.settings_tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.game_filter_status = "disabled"
        self.ipset_status = "loaded"
        self.update_status_vars()

        game_frame = ctk.CTkFrame(frame)
        game_frame.pack(pady=10, fill="x", padx=20)

        ctk.CTkLabel(game_frame, text="Фильтр игр:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.game_status = ctk.CTkLabel(game_frame, text=self.game_filter_status)
        self.game_status.grid(row=0, column=1, padx=10, pady=10)

        self.game_switch_btn = ctk.CTkButton(
            game_frame,
            text="Переключить",
            command=lambda: self.toggle_game_filter()
        )
        self.game_switch_btn.grid(row=0, column=2, padx=10, pady=10)

        ipset_frame = ctk.CTkFrame(frame)
        ipset_frame.pack(pady=10, fill="x", padx=20)

        ctk.CTkLabel(ipset_frame, text="IPSet:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.ipset_status_label = ctk.CTkLabel(ipset_frame, text=self.ipset_status)
        self.ipset_status_label.grid(row=0, column=1, padx=10, pady=10)

        self.ipset_switch_btn = ctk.CTkButton(
            ipset_frame,
            text="Переключить",
            command=lambda: self.toggle_ipset()
        )
        self.ipset_switch_btn.grid(row=0, column=2, padx=10, pady=10)

        self.ipset_update_btn = ctk.CTkButton(
            ipset_frame,
            text="Обновить",
            command=lambda: threading.Thread(target=self.update_ipset).start()
        )
        self.ipset_update_btn.grid(row=0, column=3, padx=10, pady=10)

        self.settings_log = ctk.CTkTextbox(frame, width=850, height=300)
        self.settings_log.pack(pady=10)
        self.settings_log.tag_config("green", foreground="#2ECC71")
        self.settings_log.tag_config("red", foreground="#E74C3C")
        self.settings_log.tag_config("yellow", foreground="#F39C12")
        self.settings_log.configure(state="disabled")

    def settings_log_message(self, msg, color=None):
        
        self.settings_log.configure(state="normal")
        self.settings_log.insert("end", msg + "\n")
        if color:
            start_index = self.settings_log.index("end-2c linestart")
            end_index = self.settings_log.index("end-1c")
            self.settings_log.tag_add(color, start_index, end_index)
        self.settings_log.configure(state="disabled")
        self.settings_log.see("end")

    def toggle_game_filter(self):
        
        game_flag_file = os.path.join(TEMP_DIR, "bin", "game_filter.enabled")

        if os.path.exists(game_flag_file):
            try:
                os.remove(game_flag_file)
                self.game_filter_status = "disabled"
                self.settings_log_message("Фильтр игр: ОТКЛЮЧЕН", "green")
            except Exception as e:
                self.settings_log_message(f"Ошибка отключения фильтра: {e}", "red")
        else:
            try:
                with open(game_flag_file, "w") as f:
                    f.write("ENABLED")
                self.game_filter_status = "enabled"
                self.settings_log_message("Фильтр игр: ВКЛЮЧЕН", "green")
            except Exception as e:
                self.settings_log_message(f"Ошибка включения фильтра: {e}", "red")

        self.game_status.configure(text=self.game_filter_status)

    def toggle_ipset(self):
        
        ipset_file = os.path.join(TEMP_DIR, "lists", "ipset-all.txt")
        backup_file = os.path.join(TEMP_DIR, "lists", "ipset-all.txt.backup")

        try:

            if self.ipset_status == "empty":
                if os.path.exists(backup_file):
                    if os.path.exists(ipset_file):
                        os.remove(ipset_file)
                    os.rename(backup_file, ipset_file)
                    self.ipset_status = "loaded"
                    self.settings_log_message("IPSet: ВКЛЮЧЕН (список восстановлен)", "green")
                else:
                    self.settings_log_message("Резервная копия не найдена", "red")

            else:
                if os.path.exists(ipset_file):

                    if os.path.exists(backup_file):
                        os.remove(backup_file)
                    os.rename(ipset_file, backup_file)

                    with open(ipset_file, "w") as f:
                        f.write("0.0.0.0/32")

                    self.ipset_status = "empty"
                    self.settings_log_message("IPSet: ОТКЛЮЧЕН (список очищен)", "green")
                else:
                    self.settings_log_message("Файл ipset не найден", "red")

        except Exception as e:
            self.settings_log_message(f"Ошибка переключения ipset: {e}", "red")

        self.ipset_status_label.configure(text=self.ipset_status)

    def update_ipset(self):
        
        ipset_file = os.path.join(TEMP_DIR, "lists", "ipset-all.txt")

        try:
            self.settings_log_message("Обновление списка ipset...")

            response = requests.get(IPSET_URL, timeout=10)
            response.raise_for_status()

            with open(ipset_file, "w", encoding="utf-8") as f:
                f.write(response.text)

            self.ipset_status = "loaded"
            self.ipset_status_label.configure(text=self.ipset_status)
            self.settings_log_message("Список ipset успешно обновлен", "green")

        except Exception as e:
            self.settings_log_message(f"Ошибка обновления ipset: {e}", "red")


if __name__ == "__main__":
    app = ZapretApp()
    app.mainloop()