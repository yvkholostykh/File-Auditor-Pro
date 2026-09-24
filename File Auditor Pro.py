#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Auditor Pro v40.7 - FULL FORENSIC EDITION + CAD + COPY + SOUND + SMART LIBS
                          + FIXED ENCODING + OCR/SOUND BUTTONS ON SCAN TAB
                          + RESIZABLE WINDOWS + COMPACT SCAN TAB
                          + CSV REMOVED + CODE OPTIMIZED
                          + BILINGUAL UI (RU/EN) + MIT LICENSE
                          + ROBUST IMPORTS + FIXED HELP TRANSLATION
                          + FIXED SCAN TIMER + FIXED STOP + TIMER ABOVE COUNTERS
                          + CHECKPOINT RESET / СБРОС ЧЕКПОИНТА
                          + OCR TOGGLE REMOVED / УБРАНА КНОПКА OCR
                          + NAMES-ONLY SCAN MODE / РЕЖИМ СКАНИРОВАНИЯ ТОЛЬКО ПО ИМЕНАМ
                          + FIXED HYPERLINKS: mapped drive → UNC / ИСПРАВЛЕНЫ ССЫЛКИ
Author: Information Security Specialist, Y. V. Kholostykh
"""

import os
import sys
import subprocess
import time
import string
import warnings
import zipfile
import tarfile
import shutil
import tempfile
import re
import signal
import threading
import queue
import traceback
import ctypes
import email
import json
import html as html_module
import zlib
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from email import policy as email_policy
from email.parser import BytesParser

# ----------------------------------------------------------------------
# Portable paths and constants / Портабельные пути и константы
# ----------------------------------------------------------------------
AUTHOR = "Information Security Specialist, Y. V. Kholostykh"
GITHUB = "https://github.com/yvkholostykh?tab=repositories"
LICENSE = "MIT"
PROGRAM_NAME = "FILE AUDITOR PRO"
VERSION = "40.7 GUI"

BASE_DIR = Path(__file__).parent.resolve()
LIBS_DIR = BASE_DIR / "libs"
LIBS_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_REPORTS_DIR = Path.home() / "FileAuditorReports"
DEFAULT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_FILE = BASE_DIR / "audit_checkpoint.json"
SETTINGS_FILE = BASE_DIR / "auditor_settings.json"

_EML_META_CACHE: Dict[str, Dict[str, str]] = {}
_EML_META_LOCK = threading.Lock()

# ----------------------------------------------------------------------
# I18N — Bilingual strings / Двуязычные строки
# ----------------------------------------------------------------------
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'ru': {
        'tab_info': "Информация",
        'tab_scan': "Сканирование",
        'tab_libs': "Библиотеки",

        'menu_file': "Файл",
        'menu_tools': "Инструменты",
        'menu_help': "Справка",
        'menu_select_folder': "Выбрать папку...",
        'menu_select_drives': "Выбрать диски...",
        'menu_export_txt': "Экспорт TXT",
        'menu_export_word': "Экспорт WORD (полный отчёт ИБ)",
        'menu_exit': "Выход",
        'menu_show_keywords': "Показать ключевые слова",
        'menu_edit_keywords': "Редактировать keywords.txt",
        'menu_reload_keywords': "Перезагрузить ключевые слова",
        'menu_reinstall_libs': "Повторно проверить библиотеки",
        'menu_errors': "Окно ошибок",
        'menu_about': "О программе",
        'menu_reset_checkpoint': "Сбросить чекпоинт",
        'menu_checkpoint_info': "Информация о чекпоинте",

        'btn_sound_on': "🔊 Звук: ВКЛ",
        'btn_sound_off': "🔇 Звук: ВЫКЛ",
        'btn_names_on': "📝 Только имена: ВКЛ",
        'btn_names_off': "📝 Только имена: ВЫКЛ",
        'btn_lang': "🌐 Язык: RU",
        'btn_folder': "📁 Папка...",
        'btn_drives': "💾 Выбрать диски…",
        'btn_stop': "⏹ Остановить",
        'btn_pause': "⏸ Пауза",
        'btn_resume': "▶ Продолжить",
        'btn_export_txt': "📄 Экспорт TXT",
        'btn_export_word': "📝 Экспорт WORD",
        'btn_errors': "⚠ Ошибки",

        'scan_header': "Найденные файлы",
        'log_header': "Журнал сканирования",
        'progress_preparing': "подготовка…",

        'timer_found': "Найдено файлов",
        'timer_scanned': "Проверено",
        'timer_elapsed': "Прошло",

        'info_header': "СВОДНАЯ ИНФОРМАЦИЯ",
        'info_subheader': "Всё, что раньше печаталось в консоль при запуске.",
        'info_boot_log': "Лог запуска и установки библиотек",
        'info_disks': "Информация о дисках",
        'info_formats': "Поддерживаемые форматы",
        'info_ocr_status': "Статус OCR",
        'info_keywords': "Ключевые слова",
        'info_loading_disks': "  Загрузка информации о дисках...\n",
        'info_ocr_init': "Инициализация...",

        'libs_header': "БИБЛИОТЕКИ (многопоточная проверка/установка)",
        'libs_current': "СЕЙЧАС:",
        'libs_log': "Журнал установки",
        'libs_col_name': "Название",
        'libs_col_type': "Тип",
        'libs_col_pip': "pip-имя",
        'libs_col_fallbacks': "Аналоги",
        'libs_col_status': "Статус",
        'libs_col_version': "Версия",

        'col_filename': "Имя файла",
        'col_keywords': "Ключевые слова",
        'col_size': "Размер",
        'col_owner': "Владелец",
        'col_author': "Автор",
        'col_modified': "Изменён",
        'col_disk': "Диск",

        'status_ready': "Готов",
        'status_scanning_prep': "Сканирование: подготовка…",

        'dlg_officer_title': "Данные офицера ИБ",
        'dlg_officer_header': "Введите данные офицера по информационной безопасности",
        'dlg_officer_fio': "ФИО:",
        'dlg_officer_position': "Должность:",
        'dlg_officer_position_default': "Офицер по информационной безопасности",
        'dlg_officer_department': "Подразделение:",
        'dlg_officer_contact': "Контакт (телефон/почта):",
        'dlg_officer_ok': "Сформировать отчёт",
        'dlg_officer_cancel': "Отмена",

        'dlg_drives_title': "Все диски — выберите, что сканировать",
        'dlg_drives_hint': "Отметьте диски, которые нужно просканировать:",
        'dlg_drives_select_all': "Выбрать все",
        'dlg_drives_deselect_all': "Снять все",
        'dlg_drives_internal': "Только внутренние",
        'dlg_drives_usb': "Только USB",
        'dlg_drives_col_disk': "Диск",
        'dlg_drives_col_type': "Тип",
        'dlg_drives_col_label': "Метка",
        'dlg_drives_col_fs': "ФС",
        'dlg_drives_col_total': "Всего",
        'dlg_drives_col_free': "Свободно",
        'dlg_drives_col_usb': "USB",
        'dlg_drives_col_serial': "Сер. номер",
        'dlg_drives_col_model': "Модель",
        'dlg_drives_scan': "Сканировать выбранные",
        'dlg_drives_cancel': "Отмена",
        'dlg_drives_warn': "Не выбран ни один диск",

        'dlg_splash_author': "Автор:",
        'dlg_splash_github': "GitHub:",
        'dlg_splash_license': "Лицензия:",
        'dlg_splash_program': "Программа:",
        'dlg_splash_version': "Версия:",

        'msg_scan_running': "Сканирование уже выполняется",
        'msg_no_results': "Нет результатов для экспорта",
        'msg_no_results_word': "Нет результатов для экспорта.\nСначала выполните сканирование.",
        'msg_save_title': "Сохранить отчёт",
        'msg_save_word_title': "Сохранить Word-отчёт",
        'msg_saved': "Отчёт сохранён:\n{path}",
        'msg_saved_word': "Word-отчёт сохранён:\n{path}",
        'msg_save_error': "Ошибка сохранения отчёта",
        'msg_save_word_error': "Не удалось сформировать Word-отчёт.\nПроверьте окно ошибок для деталей.",
        'msg_done_title': "Готово",
        'msg_done_scan': "Сканирование завершено.\nНайдено совпадений: {n}\n\nПрошло времени: {elapsed}\n\nМожно сформировать Word-отчёт: кнопка «Экспорт WORD».",
        'msg_done_no_matches': "Сканирование завершено. Совпадений не найдено.\nПрошло времени: {elapsed}",
        'msg_stopped_title': "Остановлено",
        'msg_stopped': "Сканирование остановлено пользователем.\nПрошло времени: {elapsed}\nНайдено совпадений: {n}",
        'msg_no_disks': "Не найдено ни одного диска с файловой системой",
        'msg_keywords_title': "Ключевые слова",
        'msg_keywords_reloaded': "Перезагружено {n} ключевых слов",
        'msg_keywords_open_error': "Не удалось открыть файл:\n{e}",
        'msg_errors_title': "Ошибки / Предупреждения",
        'msg_errors_header': "ОКНО ОШИБОК",
        'msg_errors_total': "Всего записей: {n}",
        'msg_errors_none': "\n  Ошибок не зафиксировано.\n",
        'msg_errors_save_title': "Сохранить журнал ошибок",
        'msg_errors_saved': "Сохранено:\n{path}",
        'msg_errors_save_error': "Не удалось сохранить:\n{ex}",
        'msg_errors_clear_confirm': "Очистить журнал ошибок?",
        'msg_reinstall_libs_confirm': "Запустить повторную параллельную проверку и установку библиотек?",
        'msg_reinstall_libs_title': "Библиотеки",

        'msg_checkpoint_title': "Чекпоинт",
        'msg_checkpoint_not_found': "Чекпоинт не найден.\nНет сохранённого состояния сканирования.",
        'msg_checkpoint_reset_ok': "Чекпоинт успешно сброшен.\nСледующее сканирование начнётся с нуля.",
        'msg_checkpoint_reset_error': "Не удалось сбросить чекпоинт.\nПроверьте окно ошибок.",
        'btn_reset_checkpoint': "🗑 Сбросить чекпоинт",

        'btn_save_to_file': "Сохранить в файл",
        'btn_clear': "Очистить",
        'btn_close': "Закрыть",
        'btn_copy_all': "Копировать всё",

        'word_title': "ОТЧЁТ\nО РЕЗУЛЬТАТАХ ПОИСКА КОНФИДЕНЦИАЛЬНОЙ ИНФОРМАЦИИ\nИ АУДИТА ФАЙЛОВОЙ СИСТЕМЫ",
        'word_subtitle': "Программа: {name} v{ver}",
        'word_author_prog': "Автор программы: {a}",
        'word_license': "Лицензия: {l}",
        'word_github': "GitHub: {g}",
        'word_generated': "Отчёт сгенерирован: {dt}",
        'word_computer': "Компьютер сканирующий: {c}",
        'word_audit_start': "Аудит начат: {dt}",
        'word_audit_end': "Аудит завершён: {dt}",
        'word_elapsed': "Время сканирования",
        'word_officer_header': "СОСТАВИЛ ОФИЦЕР ПО ИНФОРМАЦИОННОЙ БЕЗОПАСНОСТИ:",
        'word_officer_fio': "ФИО: {v}",
        'word_officer_position': "Должность: {v}",
        'word_officer_department': "Подразделение: {v}",
        'word_officer_contact': "Контакт: {v}",

        'word_h1_summary': "1. Сводка по аудиту",
        'word_h1_1_conclusions': "1.1. Обобщённые выводы",
        'word_h2_media': "2. Информация о носителях",
        'word_h2_1_scan_media': "2.1. Характеристики просканированных носителей",
        'word_h3_files_table': "3. Сводная таблица найденных файлов",
        'word_h4_details': "4. Детальные карточки найденных файлов",
        'word_h2_disk': "2.{i}. Физический диск",

        'word_total_found': "Всего найдено файлов",
        'word_audit_started': "Начало аудита",
        'word_audit_finished': "Завершение аудита",
        'word_ocr_status': "Статус OCR",
        'word_categories': "Категории файлов:",
        'word_extensions_top': "Топ-15 расширений:",
        'word_keywords_top': "Топ ключевых слов:",
        'word_owners_top': "Топ владельцев:",
        'word_authors_top': "Топ авторов документов:",
        'word_forensic_metrics': "Форензик-метрики:",
        'word_category': "Категория",
        'word_count': "Количество",
        'word_extension': "Расширение",
        'word_keyword': "Ключевое слово",
        'word_files_found': "Найдено файлов",
        'word_owner': "Владелец",
        'word_author': "Автор",
        'word_model': "Модель",
        'word_manufacturer': "Производитель",
        'word_serial': "Серийный номер",
        'word_interface': "Интерфейс",
        'word_size': "Размер",
        'word_partitions': "Разделов",
        'word_drive_letters': "Буквы дисков",
        'word_num': "№",
        'word_filename': "Имя файла",
        'word_path': "Путь",
        'word_keywords': "Ключевые слова",
        'word_modified': "Изменён",
        'word_full_path': "Полный путь",
        'word_extension2': "Расширение",
        'word_size2': "Размер",
        'word_created': "Создан",
        'word_modified2': "Изменён",
        'word_accessed': "Открыт",
        'word_file_creator': "Создатель файла",
        'word_file_owner': "Владелец файла",
        'word_doc_author': "Автор документа",
        'word_last_saved_by': "Кем изменён",
        'word_computer_scan': "Компьютер сканирующий",
        'word_readonly': "Только чтение",
        'word_hidden': "Скрытый",
        'word_system': "Системный",
        'word_archive': "Архивный",
        'word_disk_letter': "Буква диска",
        'word_disk_model': "Модель диска",
        'word_disk_serial': "Серийный номер диска",
        'word_keywords2': "Ключевые слова",
        'word_mail_sender': "Кто отправил письмо",
        'word_mail_recipient': "Кому отправлено письмо",
        'word_drive_chars': "Характеристики носителя:",
        'word_screenshot': "Скриншот / превью содержимого:",
        'word_sign_off': "Офицер по информационной безопасности: _____________________ / {fio}",
        'word_date': "Дата: {dt}",
        'word_exif': "Изображений с EXIF",
        'word_gps': "Изображений с GPS-метками",
        'word_stegano': "Кандидатов на стеганографию",
        'word_pdf_susp': "PDF с потенциально опасными объектами",
        'word_registry': "Файлов реестра/журналов",
        'word_mail': "Файлов почты (EML/MSG)",
        'word_usb': "Файлов на USB-носителях",
        'word_forensic': "Форензик-образов (E01/RAW/VMDK/…)",
        'word_exec': "Исполняемых файлов (EXE/DLL/скрипты)",
        'word_cad': "CAD/Сметных файлов (DWG/DXF/CDW/GSFX/…)",
        'word_yes': "Да",
        'word_no': "Нет",
        'word_not_specified': "Не указан",
        'word_not_defined': "Не определен",
    },
    'en': {
        'tab_info': "Information",
        'tab_scan': "Scanning",
        'tab_libs': "Libraries",

        'menu_file': "File",
        'menu_tools': "Tools",
        'menu_help': "Help",
        'menu_select_folder': "Select folder...",
        'menu_select_drives': "Select drives...",
        'menu_export_txt': "Export TXT",
        'menu_export_word': "Export WORD (full IS report)",
        'menu_exit': "Exit",
        'menu_show_keywords': "Show keywords",
        'menu_edit_keywords': "Edit keywords.txt",
        'menu_reload_keywords': "Reload keywords",
        'menu_reinstall_libs': "Re-check libraries",
        'menu_errors': "Error log",
        'menu_about': "About",
        'menu_reset_checkpoint': "Reset checkpoint",
        'menu_checkpoint_info': "Checkpoint info",

        'btn_sound_on': "🔊 Sound: ON",
        'btn_sound_off': "🔇 Sound: OFF",
        'btn_names_on': "📝 Names only: ON",
        'btn_names_off': "📝 Names only: OFF",
        'btn_lang': "🌐 Lang: EN",
        'btn_folder': "📁 Folder...",
        'btn_drives': "💾 Select drives…",
        'btn_stop': "⏹ Stop",
        'btn_pause': "⏸ Pause",
        'btn_resume': "▶ Resume",
        'btn_export_txt': "📄 Export TXT",
        'btn_export_word': "📝 Export WORD",
        'btn_errors': "⚠ Errors",

        'scan_header': "Found files",
        'log_header': "Scan log",
        'progress_preparing': "preparing…",

        'timer_found': "Files found",
        'timer_scanned': "Scanned",
        'timer_elapsed': "Elapsed",

        'info_header': "SUMMARY INFORMATION",
        'info_subheader': "Everything that used to be printed to console at startup.",
        'info_boot_log': "Startup & library installation log",
        'info_disks': "Disk information",
        'info_formats': "Supported formats",
        'info_ocr_status': "OCR status",
        'info_keywords': "Keywords",
        'info_loading_disks': "  Loading disk information...\n",
        'info_ocr_init': "Initializing...",

        'libs_header': "LIBRARIES (multithreaded check/install)",
        'libs_current': "NOW:",
        'libs_log': "Installation log",
        'libs_col_name': "Name",
        'libs_col_type': "Type",
        'libs_col_pip': "pip-name",
        'libs_col_fallbacks': "Fallbacks",
        'libs_col_status': "Status",
        'libs_col_version': "Version",

        'col_filename': "File name",
        'col_keywords': "Keywords",
        'col_size': "Size",
        'col_owner': "Owner",
        'col_author': "Author",
        'col_modified': "Modified",
        'col_disk': "Disk",

        'status_ready': "Ready",
        'status_scanning_prep': "Scanning: preparing…",

        'dlg_officer_title': "IS Officer Data",
        'dlg_officer_header': "Enter Information Security Officer data",
        'dlg_officer_fio': "Full name:",
        'dlg_officer_position': "Position:",
        'dlg_officer_position_default': "Information Security Officer",
        'dlg_officer_department': "Department:",
        'dlg_officer_contact': "Contact (phone/email):",
        'dlg_officer_ok': "Generate report",
        'dlg_officer_cancel': "Cancel",

        'dlg_drives_title': "All drives — select what to scan",
        'dlg_drives_hint': "Check the drives you want to scan:",
        'dlg_drives_select_all': "Select all",
        'dlg_drives_deselect_all': "Deselect all",
        'dlg_drives_internal': "Internal only",
        'dlg_drives_usb': "USB only",
        'dlg_drives_col_disk': "Drive",
        'dlg_drives_col_type': "Type",
        'dlg_drives_col_label': "Label",
        'dlg_drives_col_fs': "FS",
        'dlg_drives_col_total': "Total",
        'dlg_drives_col_free': "Free",
        'dlg_drives_col_usb': "USB",
        'dlg_drives_col_serial': "Serial",
        'dlg_drives_col_model': "Model",
        'dlg_drives_scan': "Scan selected",
        'dlg_drives_cancel': "Cancel",
        'dlg_drives_warn': "No drive selected",

        'dlg_splash_author': "Author:",
        'dlg_splash_github': "GitHub:",
        'dlg_splash_license': "License:",
        'dlg_splash_program': "Program:",
        'dlg_splash_version': "Version:",

        'msg_scan_running': "Scanning is already in progress",
        'msg_no_results': "No results to export",
        'msg_no_results_word': "No results to export.\nPlease run a scan first.",
        'msg_save_title': "Save report",
        'msg_save_word_title': "Save Word report",
        'msg_saved': "Report saved:\n{path}",
        'msg_saved_word': "Word report saved:\n{path}",
        'msg_save_error': "Failed to save report",
        'msg_save_word_error': "Failed to generate Word report.\nCheck the error log for details.",
        'msg_done_title': "Done",
        'msg_done_scan': "Scan complete.\nMatches found: {n}\n\nElapsed time: {elapsed}\n\nYou can now generate a Word report using the “Export WORD” button.",
        'msg_done_no_matches': "Scan complete. No matches found.\nElapsed time: {elapsed}",
        'msg_stopped_title': "Stopped",
        'msg_stopped': "Scan stopped by user.\nElapsed time: {elapsed}\nMatches found: {n}",
        'msg_no_disks': "No drives with a file system were found",
        'msg_keywords_title': "Keywords",
        'msg_keywords_reloaded': "Reloaded {n} keywords",
        'msg_keywords_open_error': "Failed to open file:\n{e}",
        'msg_errors_title': "Errors / Warnings",
        'msg_errors_header': "ERROR LOG",
        'msg_errors_total': "Total entries: {n}",
        'msg_errors_none': "\n  No errors recorded.\n",
        'msg_errors_save_title': "Save error log",
        'msg_errors_saved': "Saved:\n{path}",
        'msg_errors_save_error': "Failed to save:\n{ex}",
        'msg_errors_clear_confirm': "Clear error log?",
        'msg_reinstall_libs_confirm': "Run parallel re-check and reinstall of libraries?",
        'msg_reinstall_libs_title': "Libraries",

        'msg_checkpoint_title': "Checkpoint",
        'msg_checkpoint_not_found': "Checkpoint not found.\nNo saved scan state.",
        'msg_checkpoint_reset_ok': "Checkpoint reset successfully.\nNext scan will start from scratch.",
        'msg_checkpoint_reset_error': "Failed to reset checkpoint.\nCheck the error log.",
        'btn_reset_checkpoint': "🗑 Reset checkpoint",

        'btn_save_to_file': "Save to file",
        'btn_clear': "Clear",
        'btn_close': "Close",
        'btn_copy_all': "Copy all",

        'word_title': "REPORT\nON THE RESULTS OF SEARCHING FOR CONFIDENTIAL INFORMATION\nAND FILE SYSTEM AUDIT",
        'word_subtitle': "Program: {name} v{ver}",
        'word_author_prog': "Program author: {a}",
        'word_license': "License: {l}",
        'word_github': "GitHub: {g}",
        'word_generated': "Report generated: {dt}",
        'word_computer': "Scanning computer: {c}",
        'word_audit_start': "Audit started: {dt}",
        'word_audit_end': "Audit finished: {dt}",
        'word_elapsed': "Scan duration",
        'word_officer_header': "PREPARED BY INFORMATION SECURITY OFFICER:",
        'word_officer_fio': "Full name: {v}",
        'word_officer_position': "Position: {v}",
        'word_officer_department': "Department: {v}",
        'word_officer_contact': "Contact: {v}",

        'word_h1_summary': "1. Audit summary",
        'word_h1_1_conclusions': "1.1. Aggregated conclusions",
        'word_h2_media': "2. Media information",
        'word_h2_1_scan_media': "2.1. Characteristics of scanned media",
        'word_h3_files_table': "3. Summary table of found files",
        'word_h4_details': "4. Detailed cards of found files",
        'word_h2_disk': "2.{i}. Physical disk",

        'word_total_found': "Total files found",
        'word_audit_started': "Audit start",
        'word_audit_finished': "Audit finish",
        'word_ocr_status': "OCR status",
        'word_categories': "File categories:",
        'word_extensions_top': "Top-15 extensions:",
        'word_keywords_top': "Top keywords:",
        'word_owners_top': "Top owners:",
        'word_authors_top': "Top document authors:",
        'word_forensic_metrics': "Forensic metrics:",
        'word_category': "Category",
        'word_count': "Count",
        'word_extension': "Extension",
        'word_keyword': "Keyword",
        'word_files_found': "Files found",
        'word_owner': "Owner",
        'word_author': "Author",
        'word_model': "Model",
        'word_manufacturer': "Manufacturer",
        'word_serial': "Serial number",
        'word_interface': "Interface",
        'word_size': "Size",
        'word_partitions': "Partitions",
        'word_drive_letters': "Drive letters",
        'word_num': "#",
        'word_filename': "File name",
        'word_path': "Path",
        'word_keywords': "Keywords",
        'word_modified': "Modified",
        'word_full_path': "Full path",
        'word_extension2': "Extension",
        'word_size2': "Size",
        'word_created': "Created",
        'word_modified2': "Modified",
        'word_accessed': "Accessed",
        'word_file_creator': "File creator",
        'word_file_owner': "File owner",
        'word_doc_author': "Document author",
        'word_last_saved_by': "Last saved by",
        'word_computer_scan': "Scanning computer",
        'word_readonly': "Read-only",
        'word_hidden': "Hidden",
        'word_system': "System",
        'word_archive': "Archive",
        'word_disk_letter': "Disk letter",
        'word_disk_model': "Disk model",
        'word_disk_serial': "Disk serial number",
        'word_keywords2': "Keywords",
        'word_mail_sender': "Sent by",
        'word_mail_recipient': "Recipient",
        'word_drive_chars': "Media characteristics:",
        'word_screenshot': "Screenshot / content preview:",
        'word_sign_off': "Information Security Officer: _____________________ / {fio}",
        'word_date': "Date: {dt}",
        'word_exif': "Images with EXIF",
        'word_gps': "Images with GPS marks",
        'word_stegano': "Steganography candidates",
        'word_pdf_susp': "PDF with potentially dangerous objects",
        'word_registry': "Registry/log files",
        'word_mail': "Mail files (EML/MSG)",
        'word_usb': "Files on USB media",
        'word_forensic': "Forensic images (E01/RAW/VMDK/…)",
        'word_exec': "Executables (EXE/DLL/scripts)",
        'word_cad': "CAD/Estimating files (DWG/DXF/CDW/GSFX/…)",
        'word_yes': "Yes",
        'word_no': "No",
        'word_not_specified': "Not specified",
        'word_not_defined': "Not defined",
    },
}


def tr(key: str, **kwargs) -> str:
    """Return translated string for current UI language."""
    lang = SETTINGS.get('ui_language', 'ru')
    if lang not in TRANSLATIONS:
        lang = 'ru'
    text = TRANSLATIONS[lang].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def format_elapsed(seconds: float) -> str:
    """Format elapsed time as HH:MM:SS."""
    try:
        seconds = max(0, int(seconds))
    except Exception:
        return "00:00:00"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


# ----------------------------------------------------------------------
# Settings / Настройки
# ----------------------------------------------------------------------
DEFAULT_SETTINGS = {
    'sound_on_find': True,
    'ocr_enabled': True,
    'ui_language': 'ru',
    'names_only_mode': False,
}

def load_settings() -> Dict[str, Any]:
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            merged = dict(DEFAULT_SETTINGS)
            merged.update(data)
            return merged
    except Exception:
        pass
    return dict(DEFAULT_SETTINGS)

def save_settings(settings: Dict[str, Any]):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

SETTINGS = load_settings()

# ----------------------------------------------------------------------
# Protect against sys.stdout = None (pythonw)
# ----------------------------------------------------------------------
class _NullWriter:
    def write(self, *a, **k):
        return 0
    def flush(self, *a, **k):
        pass
    def isatty(self, *a, **k):
        return False

def _ensure_streams():
    try:
        if sys.stdout is None:
            sys.stdout = _NullWriter()
    except Exception:
        pass
    try:
        if sys.stderr is None:
            sys.stderr = _NullWriter()
    except Exception:
        pass
    if sys.platform == 'win32':
        try:
            import io
            if sys.stdout and hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, _NullWriter):
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except Exception:
            pass
        try:
            import io
            if sys.stderr and hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, _NullWriter):
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception:
            pass

_ensure_streams()

def _safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except Exception:
        pass

# ----------------------------------------------------------------------
# Recursive local module search / Рекурсивный поиск локальных модулей
# ----------------------------------------------------------------------
def scan_local_modules(base_dir: Path):
    added = []
    try:
        if str(LIBS_DIR) not in sys.path:
            sys.path.insert(0, str(LIBS_DIR))
            added.append(str(LIBS_DIR))

        SKIP_DIRS = {'__pycache__', '.git', '.idea', '.vscode', '.mypy_cache',
                     '.pytest_cache', 'node_modules', '$Recycle.Bin',
                     'System Volume Information', '.tox', '.venv', 'venv',
                     'env', '.eggs', 'build', 'dist'}

        for root, dirs, files in os.walk(str(base_dir)):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            has_python = False
            for f in files:
                lf = f.lower()
                if lf.endswith(('.py', '.pyw', '.pyd', '.so', '.dll')):
                    has_python = True
                    break
                if lf == '__init__.py':
                    has_python = True
                    break

            if not has_python:
                for d in dirs:
                    if d.endswith('.dist-info') or d.endswith('.egg-info'):
                        has_python = True
                        break

            if has_python:
                p = str(Path(root).resolve())
                if p not in sys.path:
                    sys.path.append(p)
                    added.append(p)

        try:
            import importlib
            importlib.invalidate_caches()
        except Exception:
            pass
        try:
            for finder in list(sys.meta_path):
                if hasattr(finder, 'invalidate_caches'):
                    try:
                        finder.invalidate_caches()
                    except Exception:
                        pass
        except Exception:
            pass

    except Exception as e:
        _safe_print(f"  [!] scan_local_modules: {e}")
    return added


def _ensure_libs_importable():
    try:
        import importlib
        import site as _site

        try:
            _site.addsitedir(str(LIBS_DIR))
        except Exception:
            pass

        if LIBS_DIR.exists():
            for sub in LIBS_DIR.iterdir():
                try:
                    if sub.is_dir():
                        n = sub.name
                        if n.startswith('.'):
                            continue
                        if n.endswith(('.dist-info', '.egg-info')):
                            continue
                        sp = str(sub.resolve())
                        if sp not in sys.path:
                            sys.path.insert(0, sp)
                except Exception:
                    continue

        scan_local_modules(BASE_DIR)

        try:
            import importlib
            importlib.invalidate_caches()
        except Exception:
            pass
        try:
            for finder in list(sys.meta_path):
                if hasattr(finder, 'invalidate_caches'):
                    try:
                        finder.invalidate_caches()
                    except Exception:
                        pass
        except Exception:
            pass

        return True
    except Exception as e:
        register_error('libs-importable', 'Ошибка регистрации libs/ / libs/ registration error', str(e))
        return False


def _robust_import(module_name: str):
    import importlib
    try:
        return importlib.import_module(module_name)
    except Exception:
        pass
    try:
        import importlib.util
        pkg_path = LIBS_DIR / module_name
        if pkg_path.is_dir() and (pkg_path / '__init__.py').exists():
            spec = importlib.util.spec_from_file_location(
                module_name, str(pkg_path / '__init__.py'),
                submodule_search_locations=[str(pkg_path)]
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod
                spec.loader.exec_module(mod)
                return mod
    except Exception:
        pass
    try:
        import importlib.util
        py_file = LIBS_DIR / f"{module_name}.py"
        if py_file.is_file():
            spec = importlib.util.spec_from_file_location(module_name, str(py_file))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod
                spec.loader.exec_module(mod)
                return mod
    except Exception:
        pass
    if '.' in module_name:
        parent = module_name.split('.')[0]
        try:
            _robust_import(parent)
            importlib.invalidate_caches()
            return importlib.import_module(module_name)
        except Exception:
            pass
    raise ImportError(f"Cannot import {module_name} / Не удалось импортировать {module_name}")


_LOCAL_MODULES_ADDED = scan_local_modules(BASE_DIR)

try:
    import site as _site
    try:
        _site.addsitedir(str(LIBS_DIR))
    except Exception:
        pass
except Exception:
    pass

try:
    if LIBS_DIR.exists():
        for _sub in LIBS_DIR.iterdir():
            try:
                if _sub.is_dir() and not _sub.name.startswith('.'):
                    if not _sub.name.endswith(('.dist-info', '.egg-info')):
                        _sp = str(_sub.resolve())
                        if _sp not in sys.path:
                            sys.path.append(_sp)
            except Exception:
                continue
except Exception:
    pass

if str(LIBS_DIR) not in sys.path:
    sys.path.insert(0, str(LIBS_DIR))

warnings.filterwarnings("ignore")

# ----------------------------------------------------------------------
# Hide / show console
# ----------------------------------------------------------------------
_console_hidden = False
_console_hwnd = None

def hide_console():
    global _console_hidden, _console_hwnd
    if sys.platform != 'win32':
        return False
    try:
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        hwnd = kernel32.GetConsoleWindow()
        if hwnd:
            _console_hwnd = hwnd
            user32.ShowWindow(hwnd, 0)
            _console_hidden = True
            return True
    except Exception:
        pass
    return False

def show_console():
    global _console_hidden
    if sys.platform != 'win32':
        return False
    try:
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        hwnd = _console_hwnd or kernel32.GetConsoleWindow()
        if hwnd:
            user32.ShowWindow(hwnd, 5)
            _console_hidden = False
            return True
    except Exception:
        pass
    return False

def is_pythonw():
    try:
        exe = os.path.basename(sys.executable).lower()
        return exe.startswith('pythonw')
    except Exception:
        return False

def relaunch_as_pythonw():
    if sys.platform != 'win32':
        return False
    if is_pythonw():
        return False
    try:
        py_dir = os.path.dirname(sys.executable)
        pythonw = os.path.join(py_dir, 'pythonw.exe')
        if not os.path.isfile(pythonw):
            try:
                out = subprocess.run(['where', 'pythonw'], capture_output=True, timeout=5)
                lines = out.stdout.decode('utf-8', errors='replace').strip().splitlines()
                if lines:
                    pythonw = lines[0].strip()
            except Exception:
                pythonw = None
        if pythonw and os.path.isfile(pythonw):
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            subprocess.Popen(
                [pythonw] + sys.argv,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
                cwd=str(BASE_DIR),
            )
            return True
    except Exception:
        pass
    return False

# ----------------------------------------------------------------------
# Error buffer / Буфер ошибок
# ----------------------------------------------------------------------
ERROR_BUFFER: List[Dict[str, str]] = []
ERROR_BUFFER_LOCK = threading.Lock()

def register_error(stage: str, message: str, details: str = ""):
    entry = {
        'time': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        'stage': stage,
        'message': str(message),
        'details': str(details),
    }
    with ERROR_BUFFER_LOCK:
        ERROR_BUFFER.append(entry)
    _safe_print(f"  [ERROR] [{stage}] {message}")
    if details:
        _safe_print(f"          {details}")

# ----------------------------------------------------------------------
# Stop flag / Стоп-флаг
# ----------------------------------------------------------------------
stop_scan = False

def signal_handler(sig, frame):
    global stop_scan
    stop_scan = True
    _safe_print("\n[!] Stop signal received. Finishing scan... / Получен сигнал остановки.")

try:
    signal.signal(signal.SIGINT, signal_handler)
except Exception:
    pass

# ----------------------------------------------------------------------
# Colored output / Цветной вывод
# ----------------------------------------------------------------------
HAS_COLORAMA = False
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--target', str(LIBS_DIR),
             '--quiet', '--no-warn-script-location', 'colorama'],
            capture_output=True, check=False, timeout=120
        )
        _ensure_libs_importable()
        from colorama import init as colorama_init, Fore, Style
        colorama_init(autoreset=True)
        HAS_COLORAMA = True
    except Exception:
        class _Dummy:
            def __getattr__(self, name):
                return ''
        Fore = _Dummy()
        Style = _Dummy()
        HAS_COLORAMA = False

# ----------------------------------------------------------------------
# Console helpers
# ----------------------------------------------------------------------
def get_console_width():
    try:
        return min(shutil.get_terminal_size().columns, 120)
    except Exception:
        return 100

def print_line(char='=', width=None):
    if width is None:
        width = get_console_width()
    _safe_print(char * min(width, 100))

def print_color(text, color=Fore.WHITE, style=Style.NORMAL, end='\n'):
    try:
        _safe_print(f"{style}{color}{text}{Style.RESET_ALL}", end=end)
    except Exception:
        _safe_print(text, end=end)

def print_success(text):
    print_color(f"  [OK] {text}", Fore.GREEN)

def print_error(text):
    print_color(f"  [X] {text}", Fore.RED)

def print_info(text):
    print_color(f"  [i] {text}", Fore.CYAN)

def print_warning(text):
    print_color(f"  [!] {text}", Fore.YELLOW)

def print_centered(text, color=Fore.WHITE, style=Style.NORMAL):
    width = get_console_width()
    max_width = min(width, 100)
    if len(text) > max_width - 4:
        text = text[:max_width - 7] + "..."
    try:
        _safe_print(f"{style}{color}{text.center(max_width)}{Style.RESET_ALL}")
    except Exception:
        _safe_print(text.center(max_width))

def print_header(text):
    width = get_console_width()
    print_color("=" * min(width, 100), Fore.CYAN, Style.BRIGHT)
    print_centered(text, Fore.YELLOW, Style.BRIGHT)
    print_color("=" * min(width, 100), Fore.CYAN, Style.BRIGHT)

def print_two_columns(label, value, label_width=20):
    width = get_console_width()
    max_width = min(width, 100)
    content_width = max_width - label_width - 4
    value_str = safe_decode(str(value))
    if len(value_str) > content_width:
        value_str = value_str[:content_width - 3] + "..."
    print_color(f"  {label:<{label_width}}: {value_str}", Fore.WHITE)

# ----------------------------------------------------------------------
# Decoding
# ----------------------------------------------------------------------
def safe_decode(text):
    if text is None:
        return ""

    if isinstance(text, bytes):
        try:
            return text.decode('utf-8')
        except UnicodeDecodeError:
            pass
        try:
            decoded = text.decode('utf-16-le')
            if decoded and '\ufffd' not in decoded:
                if decoded.startswith('\ufeff'):
                    decoded = decoded[1:]
                if any(c.isprintable() for c in decoded):
                    return decoded
        except Exception:
            pass
        for enc in ['cp1251', 'cp866', 'koi8-r', 'cp850']:
            try:
                decoded = text.decode(enc)
                if decoded and '\ufffd' not in decoded:
                    return decoded
            except Exception:
                continue
        return text.decode('utf-8', errors='replace')

    if isinstance(text, str):
        if any('\u0400' <= c <= '\u04FF' for c in text):
            return text
        if all(ord(c) < 128 for c in text):
            return text
        if '\ufffd' in text:
            return text
        for enc_chain in [
            ('latin1', 'cp1251'),
            ('cp1252', 'cp1251'),
            ('latin1', 'cp866'),
        ]:
            try:
                src_enc, dst_enc = enc_chain
                fixed = text.encode(src_enc, errors='strict').decode(dst_enc, errors='replace')
                if fixed != text and '\ufffd' not in fixed:
                    before = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
                    after = sum(1 for c in fixed if '\u0400' <= c <= '\u04FF')
                    if after > before:
                        return fixed
            except Exception:
                continue
        return text
    return str(text)

# ----------------------------------------------------------------------
# Banner
# ----------------------------------------------------------------------
def print_banner():
    width = get_console_width()
    max_width = min(width, 100)
    _safe_print()
    print_color("+" + "=" * (max_width - 2) + "+", Fore.CYAN, Style.BRIGHT)
    print_centered(PROGRAM_NAME, Fore.YELLOW, Style.BRIGHT)
    print_color("|" + " " * (max_width - 2) + "|", Fore.CYAN)
    print_two_columns("Версия / Version", VERSION, 18)
    print_two_columns("Автор / Author", AUTHOR[:60], 18)
    print_two_columns("Лицензия / License", LICENSE, 18)
    print_two_columns("GitHub", GITHUB[:60], 18)
    print_color("+" + "=" * (max_width - 2) + "+", Fore.CYAN, Style.BRIGHT)
    _safe_print()

# ======================================================================
# MULTITHREADED LIBRARY INSTALLATION
# ======================================================================
INSTALL_LOCK = threading.Lock()

HEAVY_PACKAGES = {
    'easyocr', 'torch', 'torchvision', 'torchaudio', 'tensorflow',
    'volatility3', 'dissect', 'hindsight', 'pytsk3', 'pyewf',
}

_NON_PIP_PACKAGES = {'(внешн.)', '(внешн)'}

_FORCE_BINARY_PACKAGES = {
    'pandas', 'numpy', 'scipy', 'lxml', 'Pillow', 'pycryptodome',
    'cchardet', 'chardet', 'regex', 'pyyaml', 'PyYAML',
    'reportlab', 'cryptography', 'bcrypt', 'psutil',
    'MarkupSafe', 'Jinja2', 'packaging',
}

_CORE_PREREQ_PACKAGES = ['packaging', 'setuptools', 'wheel']

_FAILED_MODULES = ('fitz', 'filetype', 'regipy', 'registry', 'pytesseract',
                   'packaging', 'magic', 'pikepdf', 'mammoth')

def install_package_local(package):
    try:
        if not package or package in _NON_PIP_PACKAGES:
            return False, f"Package '{package}' is not a pip package / не pip-пакет"
        if not re.match(r'^[A-Za-z0-9._\-\[\],<>=!~ ]+$', str(package)):
            return False, f"Invalid package name / Некорректное имя пакета: {package!r}"

        py_exe = sys.executable
        try:
            base = os.path.basename(py_exe).lower()
            if base.startswith('pythonw'):
                candidate = os.path.join(os.path.dirname(py_exe), 'python.exe')
                if os.path.isfile(candidate):
                    py_exe = candidate
        except Exception:
            pass

        cmd = [py_exe, '-m', 'pip', 'install', '--target', str(LIBS_DIR),
               '--no-warn-script-location', '--disable-pip-version-check',
               '--prefer-binary']

        pkg_name = str(package).split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('[')[0].strip()
        if pkg_name in _FORCE_BINARY_PACKAGES:
            cmd.append('--only-binary=:all:')

        cmd.append(package)

        r = subprocess.run(cmd, capture_output=True, check=False, timeout=1800,
                           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if r.returncode != 0:
            err = (r.stderr or b'').decode('utf-8', errors='replace')[-1000:]
            if 'pkg_resources' in err or 'use_2to3' in err:
                short = 'Package is outdated or requires legacy build — skipping. / Пакет устарел или требует старой сборки — пропускаем.'
                with INSTALL_LOCK:
                    register_error('pip', f'Failed to install / Не удалось установить {package}', short)
            else:
                with INSTALL_LOCK:
                    register_error('pip', f'Failed to install / Не удалось установить {package}', err)
            return False, err
        try:
            _ensure_libs_importable()
        except Exception:
            pass
        return True, ""
    except subprocess.TimeoutExpired:
        msg = (f'Timeout installing {package} (1800 sec). '
               f'Package too large — skipping, using fallback. / Таймаут установки.')
        with INSTALL_LOCK:
            register_error('pip', msg, '')
        return False, msg
    except Exception as e:
        with INSTALL_LOCK:
            register_error('pip', f'Exception installing / Исключение при установке {package}', str(e))
        return False, str(e)

def install_package_with_retry(package, max_retries=3):
    if package in HEAVY_PACKAGES:
        max_retries = 1
    for attempt in range(max_retries):
        if attempt > 0:
            time.sleep(2)
        ok, _ = install_package_local(package)
        if ok:
            return True
    return False

def install_packages_parallel(packages: List[str], max_workers: int = 6,
                              progress_cb=None, log_cb=None) -> Dict[str, bool]:
    results: Dict[str, bool] = {}
    total = len(packages)
    if total == 0:
        return results

    light = [p for p in packages if p not in HEAVY_PACKAGES]
    heavy = [p for p in packages if p in HEAVY_PACKAGES]

    done = 0

    def _run_batch(batch, workers):
        nonlocal done
        if not batch:
            return
        with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
            futures = {ex.submit(install_package_local, p): p for p in batch}
            for fut in as_completed(futures):
                pkg = futures[fut]
                ok = False
                try:
                    ok, err = fut.result()
                    results[pkg] = ok
                except Exception as e:
                    results[pkg] = False
                    ok = False
                    with INSTALL_LOCK:
                        register_error('pip-parallel', f'Thread error / Ошибка потока для {pkg}', str(e))
                done += 1
                if progress_cb:
                    try:
                        progress_cb(done, total, pkg, ok)
                    except Exception:
                        pass
                if log_cb:
                    try:
                        if ok:
                            log_cb(f"[{done}/{total}] INSTALLED / УСТАНОВЛЕН: {pkg}", 'success')
                        else:
                            log_cb(f"[{done}/{total}] FAILED / НЕ УДАЛОСЬ: {pkg}", 'error')
                    except Exception:
                        pass

    _run_batch(light, min(max_workers, 8))
    _run_batch(heavy, 1)

    return results

def get_package_version(package_name):
    try:
        import importlib.metadata
        return importlib.metadata.version(package_name)
    except Exception:
        try:
            import pkg_resources
            return pkg_resources.get_distribution(package_name).version
        except Exception:
            return ""

# ----------------------------------------------------------------------
# Import checks
# ----------------------------------------------------------------------
def _init_com():
    if sys.platform == 'win32':
        try:
            import pythoncom
            pythoncom.CoInitialize()
            return True
        except Exception:
            return False
    return False

def _import_pptx():
    _robust_import('pptx')
    return True

def _import_PIL():
    _robust_import('PIL')
    return True

def _import_textract():
    _robust_import('textract')
    return True

def _import_wmi():
    _init_com()
    try:
        wmi = _robust_import('wmi')
        c = wmi.WMI()
        _ = c.Win32_ComputerSystem()
        return True
    except Exception:
        wmi = _robust_import('wmi')
        c = wmi.WMI()
        return True

def _import_pdf2image():
    _robust_import('pdf2image')
    return True

def _import_std(lib_id):
    def _f():
        _robust_import(lib_id)
        return True
    return _f

def _import_easyocr():
    _robust_import('easyocr')
    return True

def _import_tesseract_ocr():
    try:
        _robust_import('packaging.version')
    except Exception:
        if install_package_with_retry('packaging', max_retries=2):
            _ensure_libs_importable()
            try:
                _robust_import('packaging.version')
            except Exception:
                pass
    mod = _robust_import('pytesseract')
    exe = find_tesseract_executable()
    if not exe:
        raise ImportError("pytesseract installed but tesseract.exe not found / pytesseract установлен, но tesseract.exe не найден")
    mod.pytesseract.tesseract_cmd = exe
    return True

def _import_rarfile():
    _robust_import('rarfile')
    return True

def _import_py7zr():
    _robust_import('py7zr')
    return True

def _import_pymupdf():
    _robust_import('fitz')
    return True

def _import_pillow_heif():
    mod = _robust_import('pillow_heif')
    try:
        mod.register_heif_opener()
    except Exception:
        pass
    return True

def _import_pillow_avif():
    _robust_import('pillow_avif')
    return True

def _import_odf():
    _robust_import('odf')
    return True

def _import_striprtf():
    _robust_import('striprtf')
    return True

def _import_docx2txt():
    _robust_import('docx2txt')
    return True

def _import_xlrd():
    _robust_import('xlrd')
    return True

def _import_pandas():
    _robust_import('pandas')
    return True

def _import_chardet():
    _robust_import('chardet')
    return True

def _import_pycryptodome():
    _robust_import('Crypto')
    return True

def _import_pytsk3():
    _robust_import('pytsk3')
    return True

def _import_dissect():
    _robust_import('dissect')
    return True

def _import_dftimewolf():
    _robust_import('dftimewolf')
    return True

def _import_registry():
    _robust_import('Registry')
    return True

def _import_regipy():
    _robust_import('regipy')
    return True

def _import_pyusb():
    _robust_import('usb.core')
    return True

def _import_usbinfo():
    _robust_import('usbinfo')
    return True

def _import_exifread():
    _robust_import('exifread')
    return True

def _import_stegano():
    _robust_import('stegano')
    return True

def _import_magic():
    try:
        _robust_import('magic')
        return True
    except Exception:
        _robust_import('filetype')
        return True

def _import_cchardet():
    _robust_import('cchardet')
    return True

def _import_pdfid():
    try:
        _robust_import('pdfid')
        return True
    except Exception:
        _robust_import('peepdf')
        return True

def _import_pdfminer():
    _robust_import('pdfminer')
    return True

def _import_pefile():
    _robust_import('pefile')
    return True

def _import_ezdxf():
    _robust_import('ezdxf')
    return True

def _import_olefile():
    _robust_import('olefile')
    return True

# ----------------------------------------------------------------------
# External tools
# ----------------------------------------------------------------------
def _find_tool(names):
    for n in names:
        try:
            p = shutil.which(n)
            if p and os.path.isfile(p):
                return p
        except Exception:
            continue
    extra_dirs = [
        r"C:\Program Files\volatility3",
        r"C:\Program Files\Volatility Foundation",
        r"C:\Program Files\7-Zip",
        r"C:\Program Files\WinRAR",
        str(BASE_DIR),
    ]
    for d in extra_dirs:
        try:
            if not os.path.isdir(d):
                continue
            for root, dirs, files in os.walk(d):
                depth = root[len(d):].count(os.sep)
                if depth > 2:
                    dirs[:] = []
                    continue
                for f in files:
                    for n in names:
                        if f.lower() == n.lower():
                            return os.path.join(root, f)
        except Exception:
            continue
    return None

def _check_volatility():
    try:
        _robust_import('volatility3')
        return True
    except Exception:
        pass
    if _find_tool(['vol.py', 'volatility3.exe', 'vol.exe', 'volatility.exe']):
        return True
    raise ImportError('volatility3 not found / не найден (ни pip, ни внешний)')

TESSERACT_SEARCH_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Tesseract-OCR\tesseract.exe",
    os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
    os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
    r"C:\ProgramData\Tesseract-OCR\tesseract.exe",
    str(BASE_DIR / "Tesseract-OCR" / "tesseract.exe"),
    str(BASE_DIR / "tesseract" / "tesseract.exe"),
]

def find_tesseract_executable() -> Optional[str]:
    try:
        which = shutil.which("tesseract")
        if which and os.path.isfile(which):
            return which
    except Exception:
        pass
    for p in TESSERACT_SEARCH_PATHS:
        try:
            if os.path.isfile(p):
                return p
        except Exception:
            continue
    if sys.platform == 'win32':
        try:
            import winreg
            for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                for sub in (r"SOFTWARE\Tesseract-OCR", r"SOFTWARE\WOW6432Node\Tesseract-OCR"):
                    try:
                        with winreg.OpenKey(hive, sub) as k:
                            path, _ = winreg.QueryValueEx(k, "Path")
                            if path:
                                exe = os.path.join(path, "tesseract.exe")
                                if os.path.isfile(exe):
                                    return exe
                    except Exception:
                        continue
        except Exception:
            pass
    try:
        for root, dirs, files in os.walk(str(BASE_DIR)):
            depth = root[len(str(BASE_DIR)):].count(os.sep)
            if depth > 3:
                dirs[:] = []
                continue
            if "tesseract.exe" in [f.lower() for f in files]:
                return os.path.join(root, "tesseract.exe")
    except Exception:
        pass
    return None

# ----------------------------------------------------------------------
# LIBRARY REGISTRY
# ----------------------------------------------------------------------
ALL_LIBRARIES = {
    'easyocr': {'name': 'EasyOCR', 'desc': 'OCR for images (RU/EN) / OCR для изображений',
                'type': 'OCR', 'pip': 'easyocr', 'check': _import_easyocr,
                'fallbacks': [('pytesseract', _import_tesseract_ocr, 'Tesseract-OCR (pytesseract)')]},
    'pytesseract': {'name': 'pytesseract', 'desc': 'Tesseract OCR',
                    'type': 'OCR', 'pip': 'pytesseract', 'check': _import_tesseract_ocr,
                    'fallbacks': []},
    'pdfplumber': {'name': 'PDFPlumber', 'desc': 'PDF text extraction / Извлечение текста из PDF',
                   'type': 'PDF', 'pip': 'pdfplumber', 'check': _import_std('pdfplumber'),
                   'fallbacks': [('PyPDF2', _import_std('PyPDF2'), 'PyPDF2'),
                                 ('pypdf', _import_std('pypdf'), 'pypdf'),
                                 ('PyMuPDF', _import_pymupdf, 'PyMuPDF (fitz)')]},
    'PyPDF2': {'name': 'PyPDF2', 'desc': 'Alternative PDF parser / Альтернативный парсер PDF',
               'type': 'PDF', 'pip': 'PyPDF2', 'check': _import_std('PyPDF2'),
               'fallbacks': [('pypdf', _import_std('pypdf'), 'pypdf')]},
    'pypdf': {'name': 'pypdf', 'desc': 'Modern PDF library / Современная библиотека PDF',
              'type': 'PDF', 'pip': 'pypdf', 'check': _import_std('pypdf'),
              'fallbacks': [('PyPDF2', _import_std('PyPDF2'), 'PyPDF2')]},
    'pdf2image': {'name': 'pdf2image', 'desc': 'PDF → images for OCR',
                  'type': 'PDF', 'pip': 'pdf2image', 'check': _import_pdf2image,
                  'fallbacks': [('PyMuPDF', _import_pymupdf, 'PyMuPDF (fitz)')]},
    'PyMuPDF': {'name': 'PyMuPDF', 'desc': 'PDF + page rendering / PDF + рендер страниц',
                'type': 'PDF', 'pip': 'PyMuPDF', 'check': _import_pymupdf,
                'fallbacks': []},
    'pdfminer.six': {'name': 'pdfminer.six', 'desc': 'Alternative PDF parser',
                     'type': 'PDF', 'pip': 'pdfminer.six', 'check': _import_pdfminer,
                     'fallbacks': [('pdfplumber', _import_std('pdfplumber'), 'pdfplumber')]},
    'peepdf': {'name': 'peepdf', 'desc': 'PDF analysis (JS, exploits)',
               'type': 'PDF', 'pip': 'pdfid', 'check': _import_pdfid,
               'fallbacks': [('pikepdf', _import_std('pikepdf'), 'pikepdf')]},
    'pdfid': {'name': 'pdfid', 'desc': 'PDF scanner for suspicious objects / Сканер PDF',
              'type': 'PDF', 'pip': 'pdfid', 'check': _import_pdfid,
              'fallbacks': [('peepdf', _import_pdfid, 'peepdf')]},
    'docx': {'name': 'Python-DOCX', 'desc': 'Read Word documents / Чтение Word',
             'type': 'Office', 'pip': 'python-docx', 'check': _import_std('docx'),
             'fallbacks': [('docx2txt', _import_docx2txt, 'docx2txt'),
                           ('mammoth', _import_std('mammoth'), 'mammoth')]},
    'openpyxl': {'name': 'OpenPyXL', 'desc': 'Read Excel (xlsx/xlsm)',
                 'type': 'Office', 'pip': 'openpyxl', 'check': _import_std('openpyxl'),
                 'fallbacks': [('xlrd', _import_xlrd, 'xlrd (xls)')]},
    'pptx': {'name': 'Python-PPTX', 'desc': 'Read PowerPoint',
             'type': 'Office', 'pip': 'python-pptx', 'check': _import_pptx,
             'fallbacks': []},
    'odfpy': {'name': 'ODFPy', 'desc': 'Read OpenDocument',
              'type': 'Office', 'pip': 'odfpy', 'check': _import_odf,
              'fallbacks': []},
    'striprtf': {'name': 'striprtf', 'desc': 'Read RTF',
                 'type': 'Office', 'pip': 'striprtf', 'check': _import_striprtf,
                 'fallbacks': []},
    'PIL': {'name': 'Pillow', 'desc': 'Image processing / Обработка изображений',
            'type': 'Image', 'pip': 'Pillow', 'check': _import_PIL,
            'fallbacks': [('Pillow-SIMD', _import_PIL, 'Pillow-SIMD')]},
    'pillow-heif': {'name': 'pillow-heif', 'desc': 'HEIC/HEIF support',
                    'type': 'Image', 'pip': 'pillow-heif', 'check': _import_pillow_heif,
                    'fallbacks': []},
    'pillow-avif-plugin': {'name': 'pillow-avif-plugin', 'desc': 'AVIF support',
                           'type': 'Image', 'pip': 'pillow-avif-plugin',
                           'check': _import_pillow_avif, 'fallbacks': []},
    'exifread': {'name': 'exifread', 'desc': 'EXIF metadata of images',
                 'type': 'Image', 'pip': 'ExifRead', 'check': _import_exifread,
                 'fallbacks': []},
    'stegano': {'name': 'Stegano', 'desc': 'Steganography detection / Обнаружение стеганографии',
                'type': 'Image', 'pip': 'stegano', 'check': _import_stegano,
                'fallbacks': []},
    'textract': {'name': 'Textract', 'desc': 'Extract from legacy DOC, VSDX',
                 'type': 'Legacy', 'pip': 'textract', 'check': _import_textract,
                 'fallbacks': [('docx2txt', _import_docx2txt, 'docx2txt'),
                               ('striprtf', _import_striprtf, 'striprtf')]},
    'rarfile': {'name': 'rarfile', 'desc': 'Read RAR archives (needs 7z/unrar)',
                'type': 'Archive', 'pip': 'rarfile', 'check': _import_rarfile,
                'fallbacks': []},
    'py7zr': {'name': 'py7zr', 'desc': 'Read 7z archives',
              'type': 'Archive', 'pip': 'py7zr', 'check': _import_py7zr,
              'fallbacks': []},
    'pytsk3': {'name': 'pytsk3 (SleuthKit)', 'desc': 'Read disk images',
               'type': 'Forensic', 'pip': 'pytsk3', 'check': _import_pytsk3,
               'fallbacks': [('dissect', _import_dissect, 'dissect')]},
    'pyewf': {'name': 'pyewf (via pytsk3)', 'desc': 'Read E01 images',
              'type': 'Forensic', 'pip': 'pytsk3', 'check': _import_pytsk3,
              'fallbacks': [('dissect', _import_dissect, 'dissect')]},
    'pyvmdk': {'name': 'pyvmdk (via dissect)', 'desc': 'Read VMDK images',
               'type': 'Forensic', 'pip': 'dissect', 'check': _import_dissect,
               'fallbacks': []},
    'dissect': {'name': 'dissect', 'desc': 'Forensics (disks, FS, registry)',
                'type': 'Forensic', 'pip': 'dissect', 'check': _import_dissect,
                'fallbacks': []},
    'hindsight': {'name': 'Hindsight (via dissect)', 'desc': 'Chrome/Chromium history analysis',
                  'type': 'Forensic', 'pip': 'dissect', 'check': _import_dissect,
                  'fallbacks': []},
    'triage': {'name': 'triage (via dissect)', 'desc': 'System artifacts collection',
               'type': 'Forensic', 'pip': 'dissect', 'check': _import_dissect,
               'fallbacks': []},
    'dftimewolf': {'name': 'dftimewolf', 'desc': 'Forensic collection orchestration',
                   'type': 'Forensic', 'pip': 'dftimewolf', 'check': _import_dftimewolf,
                   'fallbacks': []},
    'volatility3': {'name': 'Volatility3', 'desc': 'Memory image analysis',
                    'type': 'Forensic', 'pip': 'volatility3', 'check': _check_volatility,
                    'fallbacks': []},
    'python-magic': {'name': 'python-magic', 'desc': 'Detect file type',
                     'type': 'Forensic', 'pip': 'python-magic', 'check': _import_magic,
                     'fallbacks': [('filetype', _import_std('filetype'), 'filetype')]},
    'python-registry': {'name': 'python-registry', 'desc': 'Read Windows registry',
                        'type': 'Registry', 'pip': 'python-registry', 'check': _import_registry,
                        'fallbacks': [('regipy', _import_regipy, 'regipy'),
                                      ('dissect', _import_dissect, 'dissect')]},
    'regipy': {'name': 'regipy', 'desc': 'Registry analysis (modern fallback)',
               'type': 'Registry', 'pip': 'regipy', 'check': _import_regipy,
               'fallbacks': [('python-registry', _import_registry, 'python-registry')]},
    'pyusb': {'name': 'pyusb', 'desc': 'Work with USB devices',
              'type': 'USB', 'pip': 'pyusb', 'check': _import_pyusb,
              'fallbacks': []},
    'usbinfo': {'name': 'usbinfo', 'desc': 'USB devices info',
                'type': 'USB', 'pip': 'usbinfo', 'check': _import_usbinfo,
                'fallbacks': []},
    'usb_parser': {'name': 'usb_parser (via pyusb)', 'desc': 'Parse USB activity',
                   'type': 'USB', 'pip': 'pyusb', 'check': _import_pyusb,
                   'fallbacks': []},
    'usbescape': {'name': 'python-usbescape (via pyusb)', 'desc': 'USB analysis',
                  'type': 'USB', 'pip': 'pyusb', 'check': _import_pyusb,
                  'fallbacks': []},
    'chardet': {'name': 'chardet', 'desc': 'Detect text encoding',
                'type': 'Data', 'pip': 'chardet', 'check': _import_chardet,
                'fallbacks': [('charset-normalizer', _import_std('charset_normalizer'), 'charset-normalizer')]},
    'cchardet': {'name': 'cchardet', 'desc': 'Fast encoding detection',
                 'type': 'Data', 'pip': 'cchardet', 'check': _import_cchardet,
                 'fallbacks': [('chardet', _import_std('chardet'), 'chardet')]},
    'pycryptodome': {'name': 'pycryptodome', 'desc': 'Encryption/archives',
                     'type': 'Data', 'pip': 'pycryptodome', 'check': _import_pycryptodome,
                     'fallbacks': []},
    'pefile': {'name': 'pefile', 'desc': 'Parse PE files (EXE/DLL)',
               'type': 'Executable', 'pip': 'pefile', 'check': _import_pefile,
               'fallbacks': []},
    'ezdxf': {'name': 'ezdxf', 'desc': 'Read DXF/DWG (AutoCAD)',
              'type': 'CAD', 'pip': 'ezdxf', 'check': _import_ezdxf,
              'fallbacks': []},
    'olefile': {'name': 'olefile', 'desc': 'Read OLE containers (DOC, KOMPAS)',
                'type': 'CAD', 'pip': 'olefile', 'check': _import_olefile,
                'fallbacks': []},
    'colorama': {'name': 'Colorama', 'desc': 'Colored output / Цветной вывод',
                 'type': 'UI', 'pip': 'colorama', 'check': _import_std('colorama'),
                 'fallbacks': [('termcolor', _import_std('termcolor'), 'termcolor')]},
    'wmi': {'name': 'WMI', 'desc': 'Disk information / Информация о дисках',
            'type': 'System', 'pip': 'wmi', 'check': _import_wmi,
            'fallbacks': [('pywin32', _import_std('win32com'), 'pywin32')]},
}

LIBRARY_STATUS: Dict[str, bool] = {}
LIBRARY_VERSIONS: Dict[str, str] = {}
LIBRARY_INSTALLED_AS: Dict[str, str] = {}

def try_check(lib_info) -> bool:
    try:
        return bool(lib_info['check']())
    except Exception:
        return False

def install_with_fallback(lib_id: str, lib_info: Dict[str, Any],
                          status_cb=None) -> Tuple[bool, str, str]:
    if try_check(lib_info):
        ver = get_package_version(lib_info['pip'])
        LIBRARY_STATUS[lib_id] = True
        LIBRARY_VERSIONS[lib_id] = ver
        LIBRARY_INSTALLED_AS[lib_id] = lib_info['pip']
        return True, lib_info['pip'], ver

    if status_cb:
        status_cb(f"Installing: {lib_info['name']} ({lib_info['pip']}) / Установка")
    if install_package_with_retry(lib_info['pip']):
        _ensure_libs_importable()
        if try_check(lib_info):
            ver = get_package_version(lib_info['pip'])
            LIBRARY_STATUS[lib_id] = True
            LIBRARY_VERSIONS[lib_id] = ver
            LIBRARY_INSTALLED_AS[lib_id] = lib_info['pip']
            return True, lib_info['pip'], ver

    for fb_pip, fb_check, fb_name in lib_info.get('fallbacks', []):
        if status_cb:
            status_cb(f"Trying fallback: {fb_name} ({fb_pip}) / Пробуем аналог")
        try:
            for mod_name in list(sys.modules.keys()):
                top = mod_name.split('.')[0]
                if top.lower() in _FAILED_MODULES:
                    try:
                        del sys.modules[mod_name]
                    except Exception:
                        pass
        except Exception:
            pass
        try:
            ok = bool(fb_check())
        except Exception:
            ok = False

        if not ok:
            if not install_package_with_retry(fb_pip, max_retries=2):
                continue
            _ensure_libs_importable()
            try:
                for mod_name in list(sys.modules.keys()):
                    top = mod_name.split('.')[0]
                    if top.lower() in _FAILED_MODULES:
                        try:
                            del sys.modules[mod_name]
                        except Exception:
                            pass
            except Exception:
                pass
            try:
                ok = bool(fb_check())
            except Exception as e:
                with INSTALL_LOCK:
                    register_error('fallback', f'Fallback {fb_name} failed / Аналог не работает', str(e))
                continue

        if ok:
            ver = get_package_version(fb_pip)
            LIBRARY_STATUS[lib_id] = True
            LIBRARY_VERSIONS[lib_id] = ver
            LIBRARY_INSTALLED_AS[lib_id] = fb_pip
            return True, fb_pip, ver

    LIBRARY_STATUS[lib_id] = False
    LIBRARY_VERSIONS[lib_id] = ""
    LIBRARY_INSTALLED_AS[lib_id] = ""
    return False, "", ""

def check_and_install_libraries_parallel(progress_cb=None, status_cb=None,
                                         log_cb=None, done_cb=None):
    total = len(ALL_LIBRARIES)

    def _emit(msg, level='info'):
        if log_cb:
            try:
                log_cb(msg, level)
            except Exception:
                pass
        if status_cb:
            try:
                status_cb(msg, level)
            except Exception:
                pass

    for prereq in _CORE_PREREQ_PACKAGES:
        try:
            _robust_import(prereq.replace('-', '_'))
        except Exception:
            install_package_local(prereq)

    _emit(f"Checking {total} libraries (parallel)... / Проверка {total} библиотек (параллельно)...", 'info')

    present = {}
    missing = []

    def _check_one(lib_id, lib_info):
        if lib_id in ('wmi', 'volatility3'):
            _init_com()
        return lib_id, lib_info, try_check(lib_info)

    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(_check_one, lid, linfo) for lid, linfo in ALL_LIBRARIES.items()]
        for fut in as_completed(futures):
            try:
                lid, linfo, ok = fut.result()
            except Exception as e:
                register_error('check', 'Library check error / Ошибка проверки библиотеки', str(e))
                continue
            done += 1
            if ok:
                present[lid] = True
                LIBRARY_STATUS[lid] = True
                LIBRARY_VERSIONS[lid] = get_package_version(linfo['pip'])
                LIBRARY_INSTALLED_AS[lid] = linfo['pip']
                _emit(f"[{done}/{total}] OK: {linfo['name']}", 'success')
            else:
                missing.append((lid, linfo))
                LIBRARY_STATUS[lid] = False
                _emit(f"[{done}/{total}] MISSING / ОТСУТСТВУЕТ: {linfo['name']} ({linfo['pip']})", 'warning')
            if progress_cb:
                try:
                    progress_cb(done, total, linfo['name'])
                except Exception:
                    pass

    _emit(f"Installed / Установлено: {len(present)} / {total}", 'info')

    if missing:
        _emit(f"Parallel installation of {len(missing)} package(s)... / Параллельная установка...", 'info')

        pip_names = []
        skipped_names = []
        for lid, linfo in missing:
            pip_name = linfo.get('pip', '')
            if not pip_name or pip_name in _NON_PIP_PACKAGES:
                skipped_names.append(linfo['name'])
                continue
            if not re.match(r'^[A-Za-z0-9._\-\[\],<>=!~ ]+$', pip_name):
                skipped_names.append(linfo['name'])
                continue
            pip_names.append(pip_name)
        pip_names = list(dict.fromkeys(pip_names))

        if skipped_names:
            _emit(f"Skipping (external tools, not pip) / Пропускаем: {', '.join(skipped_names)}", 'warning')

        def _inst_progress(d, t, pkg, ok):
            if progress_cb:
                try:
                    progress_cb(d, t, f"pkg: {pkg}")
                except Exception:
                    pass

        if pip_names:
            install_packages_parallel(
                pip_names,
                max_workers=min(6, max(1, len(pip_names))),
                progress_cb=_inst_progress,
                log_cb=log_cb,
            )
            _ensure_libs_importable()
            try:
                import importlib
                importlib.invalidate_caches()
                _pip_set = set(pip_names)
                for mod_name in list(sys.modules.keys()):
                    top = mod_name.split('.')[0]
                    if top in _pip_set:
                        try:
                            del sys.modules[mod_name]
                        except Exception:
                            pass
            except Exception:
                pass

        scan_local_modules(BASE_DIR)

        _emit("Re-check and fallback application... / Перепроверка и применение аналогов...", 'info')
        still_failed = []
        for lid, linfo in missing:
            if lid in ('wmi', 'volatility3'):
                _init_com()
            try:
                if LIBS_DIR.exists():
                    for _sub in LIBS_DIR.iterdir():
                        if _sub.is_dir() and not _sub.name.startswith('.'):
                            if not _sub.name.endswith(('.dist-info', '.egg-info')):
                                _sp = str(_sub.resolve())
                                if _sp not in sys.path:
                                    sys.path.append(_sp)
            except Exception:
                pass
            if try_check(linfo):
                LIBRARY_STATUS[lid] = True
                LIBRARY_VERSIONS[lid] = get_package_version(linfo['pip'])
                LIBRARY_INSTALLED_AS[lid] = linfo['pip']
                _emit(f"OK after installation / OK после установки: {linfo['name']}", 'success')
                continue

            ok, used, ver = install_with_fallback(
                lid, linfo,
                status_cb=lambda m: _emit(m, 'warning')
            )
            if ok:
                msg = f"INSTALLED / УСТАНОВЛЕНА: {linfo['name']}"
                if used and used != linfo['pip']:
                    msg += f" (fallback / аналог: {used})"
                if ver:
                    msg += f" v{ver}"
                _emit(msg, 'success')
            else:
                still_failed.append(linfo)
                _emit(f"FAILED (no fallbacks) / НЕ УДАЛОСЬ: {linfo['name']}", 'error')

        _emit("=" * 50, 'info')
        installed = sum(1 for s in LIBRARY_STATUS.values() if s)
        _emit(f"TOTAL / ИТОГО: installed {installed}/{total}",
              'success' if installed == total else 'warning')
    else:
        _emit("All libraries already installed / Все библиотеки уже установлены", 'success')

    refresh_library_flags()

    if done_cb:
        try:
            done_cb()
        except Exception:
            pass

# ----------------------------------------------------------------------
# Tesseract
# ----------------------------------------------------------------------
TESSERACT_EXE: Optional[str] = None
HAS_TESSERACT = False

def init_tesseract():
    global TESSERACT_EXE, HAS_TESSERACT
    exe = find_tesseract_executable()
    if not exe:
        HAS_TESSERACT = False
        return False
    TESSERACT_EXE = exe
    try:
        mod = _robust_import('pytesseract')
        mod.pytesseract.tesseract_cmd = exe
        HAS_TESSERACT = True
        return True
    except Exception as e:
        register_error('tesseract', 'pytesseract not installed / не установлен', str(e))
        if install_package_with_retry('packaging', max_retries=2) and \
           install_package_with_retry('pytesseract', max_retries=2):
            _ensure_libs_importable()
            try:
                for mod_name in list(sys.modules.keys()):
                    top = mod_name.split('.')[0]
                    if top.lower() in ('pytesseract', 'packaging'):
                        try:
                            del sys.modules[mod_name]
                        except Exception:
                            pass
            except Exception:
                pass
            try:
                mod = _robust_import('pytesseract')
                mod.pytesseract.tesseract_cmd = exe
                HAS_TESSERACT = True
                return True
            except Exception as e2:
                register_error('tesseract', 'pytesseract broken after install / не работает после установки', str(e2))
        HAS_TESSERACT = False
        return False

def ocr_with_tesseract(img):
    if not HAS_TESSERACT:
        return ""
    try:
        mod = _robust_import('pytesseract')
        mod.pytesseract.tesseract_cmd = TESSERACT_EXE
        try:
            return mod.image_to_string(img, lang='rus+eng')
        except Exception:
            return mod.image_to_string(img, lang='eng')
    except Exception as e:
        register_error('tesseract', 'Tesseract OCR error / Ошибка OCR через Tesseract', str(e))
        return ""

reader = None
HAS_OCR = False

def init_ocr():
    global reader, HAS_OCR
    if not SETTINGS.get('ocr_enabled', True):
        HAS_OCR = False
        reader = None
        print_info("OCR disabled in settings / OCR отключён в настройках")
        return False
    if LIBRARY_STATUS.get('easyocr', False):
        try:
            mod = _robust_import('easyocr')
            print_info("Loading EasyOCR... / Загрузка EasyOCR...")
            reader = mod.Reader(['ru', 'en'], gpu=False, verbose=False)
            HAS_OCR = True
            print_success("EasyOCR ready (RU/EN) / EasyOCR готов")
            if init_tesseract():
                print_success(f"Tesseract-OCR also available / тоже доступен ({TESSERACT_EXE})")
            return True
        except Exception as e:
            register_error('easyocr', 'EasyOCR init error / Ошибка инициализации EasyOCR', str(e))
            print_error(f"EasyOCR error / ошибка: {e}")

    if init_tesseract():
        HAS_OCR = True
        print_success(f"Tesseract-OCR ready / готов ({TESSERACT_EXE})")
        return True

    HAS_OCR = False
    print_warning("OCR unavailable / OCR недоступен (ни EasyOCR, ни Tesseract)")
    return False

# ----------------------------------------------------------------------
# Global library flags
# ----------------------------------------------------------------------
HAS_PDFPLUMBER = False
HAS_PYPDF2 = False
HAS_PYPDF = False
HAS_PYMUPDF = False
HAS_PDF2IMAGE = False
HAS_PDFMINER = False
HAS_PEEPDF = False
HAS_PDFID = False
HAS_DOCX = False
HAS_DOCX2TXT = False
HAS_OPENPYXL = False
HAS_XLRD = False
HAS_PANDAS = False
HAS_PPTX = False
HAS_ODF = False
HAS_STRIPRTF = False
HAS_PIL = False
HAS_PILLOW_HEIF = False
HAS_PILLOW_AVIF = False
HAS_EXIFREAD = False
HAS_STEGANO = False
HAS_TEXTRACT = False
HAS_RARFILE = False
HAS_PY7ZR = False
HAS_WMI = False
HAS_CHARDET = False
HAS_CCHARDET = False
HAS_PYTSK3 = False
HAS_PYEWF = False
HAS_PYVMDK = False
HAS_DISSECT = False
HAS_HINDSIGHT = False
HAS_TRIAGE = False
HAS_DFTIMEWOLF = False
HAS_VOLATILITY3 = False
HAS_MAGIC = False
HAS_REGISTRY = False
HAS_REGIPY = False
HAS_PYUSB = False
HAS_USBINFO = False
HAS_USB_PARSER = False
HAS_USBESCAPE = False
HAS_PEFILE = False
HAS_EZDXF = False
HAS_OLEFILE = False

def refresh_library_flags():
    global HAS_PDFPLUMBER, HAS_PYPDF2, HAS_PYPDF, HAS_PYMUPDF, HAS_PDF2IMAGE
    global HAS_PDFMINER, HAS_PEEPDF, HAS_PDFID
    global HAS_DOCX, HAS_DOCX2TXT, HAS_OPENPYXL, HAS_XLRD, HAS_PANDAS
    global HAS_PPTX, HAS_ODF, HAS_STRIPRTF
    global HAS_PIL, HAS_PILLOW_HEIF, HAS_PILLOW_AVIF, HAS_EXIFREAD, HAS_STEGANO
    global HAS_TEXTRACT, HAS_RARFILE, HAS_PY7ZR, HAS_WMI, HAS_CHARDET, HAS_CCHARDET
    global HAS_PYTSK3, HAS_PYEWF, HAS_PYVMDK, HAS_DISSECT, HAS_HINDSIGHT
    global HAS_TRIAGE, HAS_DFTIMEWOLF, HAS_VOLATILITY3
    global HAS_MAGIC
    global HAS_REGISTRY, HAS_REGIPY
    global HAS_PYUSB, HAS_USBINFO, HAS_USB_PARSER, HAS_USBESCAPE
    global HAS_PEFILE, HAS_EZDXF, HAS_OLEFILE

    def _c(*names):
        for n in names:
            if LIBRARY_STATUS.get(n, False):
                return True
        return False

    HAS_PDFPLUMBER   = _c('pdfplumber')
    HAS_PYPDF2       = _c('PyPDF2')
    HAS_PYPDF        = _c('pypdf')
    HAS_PYMUPDF      = _c('PyMuPDF')
    HAS_PDF2IMAGE    = _c('pdf2image')
    HAS_PDFMINER     = _c('pdfminer.six')
    HAS_PEEPDF       = _c('peepdf')
    HAS_PDFID        = _c('pdfid')

    HAS_DOCX         = _c('docx')
    HAS_DOCX2TXT     = _c('docx2txt')
    HAS_OPENPYXL     = _c('openpyxl')
    HAS_XLRD         = _c('xlrd')
    HAS_PANDAS       = _c('pandas')
    HAS_PPTX         = _c('pptx')
    HAS_ODF          = _c('odfpy')
    HAS_STRIPRTF     = _c('striprtf')

    HAS_PIL          = _c('PIL')
    HAS_PILLOW_HEIF  = _c('pillow-heif')
    HAS_PILLOW_AVIF  = _c('pillow-avif-plugin')
    HAS_EXIFREAD     = _c('exifread')
    HAS_STEGANO      = _c('stegano')

    HAS_TEXTRACT     = _c('textract')
    HAS_RARFILE      = _c('rarfile')
    HAS_PY7ZR        = _c('py7zr')
    HAS_WMI          = _c('wmi')
    HAS_CHARDET      = _c('chardet')
    HAS_CCHARDET     = _c('cchardet')

    HAS_PYTSK3       = _c('pytsk3')
    HAS_PYEWF        = _c('pyewf')
    HAS_PYVMDK       = _c('pyvmdk')
    HAS_DISSECT      = _c('dissect')
    HAS_HINDSIGHT    = _c('hindsight')
    HAS_TRIAGE       = _c('triage')
    HAS_DFTIMEWOLF   = _c('dftimewolf')
    HAS_VOLATILITY3  = _c('volatility3')
    HAS_MAGIC        = _c('python-magic')

    HAS_REGISTRY     = _c('python-registry')
    HAS_REGIPY       = _c('regipy')

    HAS_PYUSB        = _c('pyusb')
    HAS_USBINFO      = _c('usbinfo')
    HAS_USB_PARSER   = _c('usb_parser')
    HAS_USBESCAPE    = _c('usbescape')

    HAS_PEFILE       = _c('pefile')
    HAS_EZDXF        = _c('ezdxf')
    HAS_OLEFILE      = _c('olefile')

    if HAS_PILLOW_HEIF:
        try:
            mod = _robust_import('pillow_heif')
            mod.register_heif_opener()
        except Exception:
            pass
    if HAS_PILLOW_AVIF:
        try:
            _robust_import('pillow_avif')
        except Exception:
            pass

# ----------------------------------------------------------------------
# Size
# ----------------------------------------------------------------------
def get_file_size_human(size: int) -> str:
    try:
        size = float(size)
    except Exception:
        return "0 Б"
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} ПБ"

# ----------------------------------------------------------------------
# Extensions
# ----------------------------------------------------------------------
IMAGE_EXTS = {
    '.jpg', '.jpeg', '.jpe', '.jfif', '.png', '.bmp', '.tif', '.tiff',
    '.gif', '.webp', '.ico', '.heic', '.heif', '.avif', '.svg',
    '.tga', '.pcx', '.ppm', '.pgm', '.pbm', '.pnm', '.xbm', '.xpm',
    '.wmf', '.emf', '.dds', '.exr', '.hdr', '.psd', '.raw', '.cr2',
    '.nef', '.dng', '.arw', '.orf', '.rw2',
}
PDF_EXTS = {'.pdf'}
DOCX_EXTS = {'.docx', '.docm'}
DOC_EXTS = {'.doc', '.dot'}
XLSX_EXTS = {'.xlsx', '.xlsm', '.xltx', '.xltm'}
XLS_EXTS = {'.xls'}
PPTX_EXTS = {'.pptx', '.pptm'}
ODF_EXTS = {'.odt', '.ods', '.odp', '.odg', '.odf'}
RTF_EXTS = {'.rtf'}
VSDX_EXTS = {'.vsdx', '.vsd', '.vssx', '.vstx'}
MAIL_EXTS = {'.eml', '.msg', '.mbox'}
TEXT_EXTS = {
    '.txt', '.text', '.md', '.markdown', '.rst', '.log',
    '.csv', '.tsv', '.psv',
    '.json', '.jsonl', '.ndjson', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.html', '.htm', '.xhtml', '.css', '.scss', '.sass', '.less',
    '.py', '.pyw', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx',
    '.java', '.cs', '.cpp', '.c', '.h', '.hpp', '.go', '.rs', '.rb', '.php',
    '.pl', '.pm', '.lua', '.r', '.swift', '.kt', '.scala', '.sql',
    '.bat', '.cmd', '.ps1', '.psm1', '.sh', '.bash', '.zsh', '.fish',
    '.vbs', '.vba', '.reg', '.tex', '.bib', '.vue', '.svelte',
    '.env', '.gitignore', '.dockerignore', '.editorconfig',
}
ARCHIVE_EXTS = {
    '.zip', '.rar', '.7z', '.tar', '.gz', '.tgz', '.bz2', '.tbz2',
    '.xz', '.txz', '.lzma', '.lz', '.z', '.cab', '.iso',
    '.jar', '.war', '.ear', '.apk', '.ipa', '.whl', '.egg',
    '.tar.gz', '.tar.bz2', '.tar.xz',
}
EXEC_EXTS = {'.exe', '.dll', '.sys', '.scr', '.com', '.msi', '.ocx', '.cpl'}
FORENSIC_EXTS = {'.e01', '.raw', '.dd', '.img', '.vmdk', '.vhd', '.vhdx',
                 '.mem', '.dmp', '.aff', '.vmem', '.001'}
REGISTRY_EXTS = {'.reg', '.dat', '.hiv', '.evt', '.evtx'}

AUTOCAD_EXTS = {'.dwg', '.dxf', '.dwt', '.dws', '.dwf', '.dwfx'}
KOMPAS_EXTS = {'.cdw', '.frw', '.spw', '.m3d', '.a3d', '.c3d', '.kdw', '.cdt'}
GRANDSMETA_EXTS = {'.gsfx', '.gsf', '.grs', '.gs1', '.gs2', '.sfx'}
MACROMINE_EXTS = {'.mmd', '.mmx', '.mmz', '.mma'}
CIVIL_EXTS = {'.landxml', '.tin', '.dem', '.pts'}

# ----------------------------------------------------------------------
# Clean WMI strings
# ----------------------------------------------------------------------
def _clean_wmi_str(v, default=""):
    if v is None:
        return default
    s = safe_decode(v)
    if not s:
        return default
    s = s.strip().strip('\x00')
    s = ''.join(c for c in s if c == ' ' or c == '\t' or c.isprintable())
    if '\ufffd' in s:
        s = s.replace('\ufffd', '').strip()
    return s or default

# ----------------------------------------------------------------------
# Metadata
# ----------------------------------------------------------------------
def get_file_owner_detailed(path):
    if sys.platform == 'win32':
        escaped = str(path).replace("\\", "\\\\").replace('"', '`"')
        ps = (
            '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; '
            '$p="' + escaped + '"; '
            'try{$o=(Get-Acl $p).Owner; '
            'if($o -match "\\\\(.+)$"){$o=$matches[1]}; $o}'
            'catch{"Не определен"}'
        )
        try:
            res = subprocess.run(
                ['powershell', '-NoProfile', '-Command', ps],
                capture_output=True, timeout=15,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            raw = res.stdout or b''
            out = ""
            for enc in ['utf-8-sig', 'utf-8', 'utf-16-le', 'cp866', 'cp1251']:
                try:
                    candidate = raw.decode(enc).strip()
                    if '\ufffd' not in candidate and candidate:
                        out = candidate
                        break
                except Exception:
                    continue
            if not out:
                out = raw.decode('utf-8', errors='replace').replace('\ufffd', '').strip()
            if out and out != "Не определен":
                out = safe_decode(out)
                if '\\' in out:
                    out = out.split('\\')[-1]
                out = out.strip()
                if out and '\ufffd' not in out:
                    return out
        except Exception:
            pass

    if sys.platform == 'win32':
        try:
            mod = _robust_import('win32security')
            sd = mod.GetFileSecurity(
                str(path), mod.OWNER_SECURITY_INFORMATION
            )
            owner_sid = sd.GetSecurityDescriptorOwner()
            name, domain, _ = mod.LookupAccountSid(None, owner_sid)
            if name:
                return safe_decode(name)
        except Exception:
            pass

    try:
        m = re.search(r'Users[\\/]([^\\/]+)', str(path))
        if m:
            owner = safe_decode(m.group(1))
            if owner and '\ufffd' not in owner:
                return owner
    except Exception:
        pass
    return "Не определен"

def get_file_times(p):
    try:
        s = os.stat(p)
        return (
            datetime.fromtimestamp(s.st_ctime).strftime('%d.%m.%Y %H:%M:%S'),
            datetime.fromtimestamp(s.st_mtime).strftime('%d.%m.%Y %H:%M:%S'),
            datetime.fromtimestamp(s.st_atime).strftime('%d.%m.%Y %H:%M:%S'),
        )
    except Exception:
        return "Не определено", "Не определено", "Не определено"

def _clean_meta(v):
    if v is None:
        return ""
    v = safe_decode(v)
    v = v.strip().strip('\x00').strip()
    if '\ufffd' in v:
        v = v.replace('\ufffd', '').strip()
    return v

def get_document_author_detailed(p):
    ext = os.path.splitext(p)[1].lower()
    author = last = ""

    try:
        if ext in DOCX_EXTS:
            if HAS_DOCX:
                try:
                    mod = _robust_import('docx')
                    doc = mod.Document(p)
                    cp = doc.core_properties
                    if cp.author:
                        author = _clean_meta(cp.author)
                    if cp.last_modified_by:
                        last = _clean_meta(cp.last_modified_by)
                except Exception:
                    pass
            if not author or not last:
                try:
                    with zipfile.ZipFile(str(p), 'r') as zf:
                        if 'docProps/core.xml' in zf.namelist():
                            xml = zf.read('docProps/core.xml').decode('utf-8', errors='replace')
                            if not author:
                                m = re.search(r'<dc:creator[^>]*>(.*?)</dc:creator>', xml, re.DOTALL)
                                if m:
                                    author = _clean_meta(m.group(1))
                            if not last:
                                m2 = re.search(r'<cp:lastModifiedBy[^>]*>(.*?)</cp:lastModifiedBy>', xml, re.DOTALL)
                                if m2:
                                    last = _clean_meta(m2.group(1))
                except Exception:
                    pass
        elif ext in XLSX_EXTS:
            if HAS_OPENPYXL:
                try:
                    mod = _robust_import('openpyxl')
                    wb = mod.load_workbook(p, read_only=True)
                    props = wb.properties
                    if props.creator:
                        author = _clean_meta(props.creator)
                    if props.lastModifiedBy:
                        last = _clean_meta(props.lastModifiedBy)
                    wb.close()
                except Exception:
                    pass
            if not author or not last:
                try:
                    with zipfile.ZipFile(str(p), 'r') as zf:
                        if 'docProps/core.xml' in zf.namelist():
                            xml = zf.read('docProps/core.xml').decode('utf-8', errors='replace')
                            if not author:
                                m = re.search(r'<dc:creator[^>]*>(.*?)</dc:creator>', xml, re.DOTALL)
                                if m:
                                    author = _clean_meta(m.group(1))
                            if not last:
                                m2 = re.search(r'<cp:lastModifiedBy[^>]*>(.*?)</cp:lastModifiedBy>', xml, re.DOTALL)
                                if m2:
                                    last = _clean_meta(m2.group(1))
                except Exception:
                    pass
        elif ext in PPTX_EXTS:
            if HAS_PPTX:
                try:
                    mod = _robust_import('pptx')
                    prs = mod.Presentation(p)
                    cp = prs.core_properties
                    if cp.author:
                        author = _clean_meta(cp.author)
                    if cp.last_modified_by:
                        last = _clean_meta(cp.last_modified_by)
                except Exception:
                    pass
            if not author or not last:
                try:
                    with zipfile.ZipFile(str(p), 'r') as zf:
                        if 'docProps/core.xml' in zf.namelist():
                            xml = zf.read('docProps/core.xml').decode('utf-8', errors='replace')
                            if not author:
                                m = re.search(r'<dc:creator[^>]*>(.*?)</dc:creator>', xml, re.DOTALL)
                                if m:
                                    author = _clean_meta(m.group(1))
                            if not last:
                                m2 = re.search(r'<cp:lastModifiedBy[^>]*>(.*?)</cp:lastModifiedBy>', xml, re.DOTALL)
                                if m2:
                                    last = _clean_meta(m2.group(1))
                except Exception:
                    pass
        elif ext in ODF_EXTS:
            try:
                with zipfile.ZipFile(str(p), 'r') as zf:
                    if 'meta.xml' in zf.namelist():
                        xml = zf.read('meta.xml').decode('utf-8', errors='replace')
                        m = re.search(r'<dc:creator[^>]*>(.*?)</dc:creator>', xml, re.DOTALL)
                        if m:
                            author = _clean_meta(m.group(1))
                        m2 = re.search(r'<meta:initial-creator[^>]*>(.*?)</meta:initial-creator>', xml, re.DOTALL)
                        if m2 and not author:
                            author = _clean_meta(m2.group(1))
                        m3 = re.search(r'<meta:printed-by[^>]*>(.*?)</meta:printed-by>', xml, re.DOTALL)
                        if m3 and not last:
                            last = _clean_meta(m3.group(1))
            except Exception:
                pass
        elif ext in PDF_EXTS:
            if HAS_PDFPLUMBER:
                try:
                    mod = _robust_import('pdfplumber')
                    with mod.open(p) as pdf:
                        meta = pdf.metadata or {}
                        if meta.get('Author') and not author:
                            author = _clean_meta(meta['Author'])
                        if meta.get('Creator') and not last:
                            last = _clean_meta(meta['Creator'])
                except Exception:
                    pass
            if not author and HAS_PYPDF2:
                try:
                    mod = _robust_import('PyPDF2')
                    with open(p, 'rb') as f:
                        r = mod.PdfReader(f)
                        if r.metadata:
                            if r.metadata.get('/Author') and not author:
                                author = _clean_meta(r.metadata['/Author'])
                            if r.metadata.get('/Creator') and not last:
                                last = _clean_meta(r.metadata['/Creator'])
                except Exception:
                    pass
            if not author and HAS_PYPDF:
                try:
                    mod = _robust_import('pypdf')
                    with open(p, 'rb') as f:
                        r = mod.PdfReader(f)
                        if r.metadata:
                            if r.metadata.get('/Author'):
                                author = _clean_meta(r.metadata['/Author'])
                            if r.metadata.get('/Creator') and not last:
                                last = _clean_meta(r.metadata['/Creator'])
                except Exception:
                    pass
            if not author and HAS_PYMUPDF:
                try:
                    mod = _robust_import('fitz')
                    doc = mod.open(str(p))
                    meta = doc.metadata or {}
                    if meta.get('author'):
                        author = _clean_meta(meta['author'])
                    if meta.get('creator') and not last:
                        last = _clean_meta(meta['creator'])
                    doc.close()
                except Exception:
                    pass
        elif ext in DOC_EXTS:
            if HAS_OLEFILE:
                try:
                    mod = _robust_import('olefile')
                    if mod.isOleFile(str(p)):
                        ole = mod.OleFileIO(str(p))
                        try:
                            meta = ole.get_metadata()
                            if meta.author:
                                author = _clean_meta(meta.author)
                            if meta.last_saved_by and not last:
                                last = _clean_meta(meta.last_saved_by)
                        except Exception:
                            pass
                        try:
                            ole.close()
                        except Exception:
                            pass
                except Exception:
                    pass
            if not author:
                try:
                    with open(str(p), 'rb') as f:
                        raw = f.read(2000000)
                    found = []
                    i = 0
                    while i < len(raw) - 4:
                        try:
                            chunk = raw[i:i+200]
                            decoded = chunk.decode('utf-16-le', errors='ignore')
                            matches = re.findall(r'[\u0400-\u04FFa-zA-Z0-9_\-\.@ ]{4,}', decoded)
                            for m in matches:
                                m = m.strip()
                                if m and 3 < len(m) < 100:
                                    found.append(m)
                        except Exception:
                            pass
                        i += 2
                    if found:
                        for candidate in found[:50]:
                            if '@' in candidate or '.' in candidate:
                                continue
                            if re.match(r'^[A-ZА-Я][a-zа-я]+\s+[A-ZА-Я]', candidate):
                                author = candidate
                                break
                except Exception:
                    pass
        elif ext in RTF_EXTS:
            try:
                with open(str(p), 'rb') as f:
                    raw = f.read(200000)
                m = re.search(rb'\\author\s+([^\\}]+)', raw)
                if m:
                    author = _clean_meta(m.group(1))
                m2 = re.search(rb'\\operator\s+([^\\}]+)', raw)
                if m2:
                    last = _clean_meta(m2.group(1))
            except Exception:
                pass
    except Exception as e:
        register_error('metadata', f'Metadata read error / Ошибка чтения метаданных {p}', str(e))

    return (author or "Не указан", last or "Не указан")

def get_file_attributes_windows(p):
    a = {'readonly': False, 'hidden': False, 'system': False, 'archive': False}
    if sys.platform != 'win32':
        return a
    try:
        att = ctypes.windll.kernel32.GetFileAttributesW(p)
        if att != 0xFFFFFFFF:
            a['readonly'] = bool(att & 0x1)
            a['hidden'] = bool(att & 0x2)
            a['system'] = bool(att & 0x4)
            a['archive'] = bool(att & 0x20)
    except Exception:
        pass
    return a

def get_computer_name():
    return safe_decode(os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', 'Не определен')))

# ----------------------------------------------------------------------
# Text extraction
# ----------------------------------------------------------------------
def _detect_encoding(raw: bytes) -> str:
    if HAS_CCHARDET:
        try:
            mod = _robust_import('cchardet')
            r = mod.detect(raw[:200000])
            enc = (r.get('encoding') or 'utf-8').lower()
            if enc in ('windows-1251', 'cp1251'):
                return 'cp1251'
            return enc
        except Exception:
            pass
    if HAS_CHARDET:
        try:
            mod = _robust_import('chardet')
            r = mod.detect(raw[:200000])
            enc = (r.get('encoding') or 'utf-8').lower()
            if enc in ('windows-1251', 'cp1251'):
                return 'cp1251'
            return enc
        except Exception:
            pass
    return 'utf-8'

def extract_text_from_txt(p):
    raw = b""
    try:
        with open(p, 'rb') as f:
            raw = f.read(2 * 1024 * 1024)
    except Exception:
        return ""
    for enc in ['utf-8', 'utf-8-sig', 'cp1251', 'cp866', 'koi8-r', 'latin1']:
        try:
            return raw.decode(enc)
        except Exception:
            continue
    enc = _detect_encoding(raw)
    try:
        return raw.decode(enc, errors='replace')
    except Exception:
        return raw.decode('utf-8', errors='replace')

def extract_text_from_rtf(p):
    if HAS_STRIPRTF:
        try:
            from striprtf.striprtf import rtf_to_text
            with open(p, 'r', encoding='latin1', errors='ignore') as f:
                return rtf_to_text(f.read(), errors='ignore')
        except Exception:
            pass
    try:
        with open(p, 'r', encoding='latin1', errors='ignore') as f:
            data = f.read()
        data = re.sub(r'\\[a-z]+\d* ?', ' ', data)
        data = re.sub(r'[{}]', '', data)
        return data
    except Exception:
        return ""

def extract_text_from_odf(p):
    if not HAS_ODF:
        return ""
    try:
        teletype = _robust_import('odf.teletype')
        load = _robust_import('odf.opendocument').load
        odf_text = _robust_import('odf.text')
        doc = load(str(p))
        parts = []
        for para in doc.getElementsByType(odf_text.P):
            t = teletype.extractText(para)
            if t.strip():
                parts.append(t)
        for para in doc.getElementsByType(odf_text.H):
            t = teletype.extractText(para)
            if t.strip():
                parts.append(t)
        return '\n'.join(parts)
    except Exception as e:
        register_error('odf', f'Read error / Ошибка чтения {p}', str(e))
        return ""

def extract_text_from_pdf(p):
    text = ""
    if HAS_PDFPLUMBER:
        try:
            mod = _robust_import('pdfplumber')
            with mod.open(p) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
            if text.strip():
                return text
        except Exception as e:
            register_error('pdf', f'pdfplumber error / ошибка для {p}', str(e))
    if HAS_PDFMINER and not text.strip():
        try:
            mod = _robust_import('pdfminer.high_level')
            t = mod.extract_text(str(p))
            if t and t.strip():
                return t
        except Exception as e:
            register_error('pdf', f'pdfminer error / ошибка для {p}', str(e))
    if HAS_PYPDF2 and not text.strip():
        try:
            mod = _robust_import('PyPDF2')
            with open(p, 'rb') as f:
                r = mod.PdfReader(f)
                for page in r.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
            if text.strip():
                return text
        except Exception as e:
            register_error('pdf', f'PyPDF2 error / ошибка для {p}', str(e))
    if HAS_PYPDF and not text.strip():
        try:
            mod = _robust_import('pypdf')
            with open(p, 'rb') as f:
                r = mod.PdfReader(f)
                for page in r.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
            if text.strip():
                return text
        except Exception as e:
            register_error('pdf', f'pypdf error / ошибка для {p}', str(e))
    if HAS_PYMUPDF and not text.strip():
        try:
            mod = _robust_import('fitz')
            doc = mod.open(str(p))
            for page in doc:
                t = page.get_text()
                if t:
                    text += t + "\n"
            doc.close()
            if text.strip():
                return text
        except Exception as e:
            register_error('pdf', f'PyMuPDF error / ошибка для {p}', str(e))

    if not text.strip() and HAS_OCR and HAS_PIL and SETTINGS.get('ocr_enabled', True):
        try:
            images = []
            if HAS_PDF2IMAGE:
                mod = _robust_import('pdf2image')
                images = mod.convert_from_path(str(p), dpi=200)
            elif HAS_PYMUPDF:
                fitz = _robust_import('fitz')
                PIL_Image = _robust_import('PIL.Image')
                doc = fitz.open(str(p))
                for page in doc:
                    pix = page.get_pixmap(dpi=200)
                    img = PIL_Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    images.append(img)
                doc.close()
            ocr_text = ""
            for img in images:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                if img.width > 2000:
                    img.thumbnail((2000, 2000))
                best_text = ""
                best_len = 0
                if reader is not None:
                    for angle in [0, 90, 180, 270]:
                        try:
                            rotated = img.rotate(angle, expand=True)
                            results = reader.readtext(rotated, detail=0, paragraph=True)
                            candidate = ' '.join(results)
                            if len(candidate) > best_len:
                                best_len = len(candidate)
                                best_text = candidate
                        except Exception:
                            continue
                if not best_text and HAS_TESSERACT:
                    try:
                        best_text = ocr_with_tesseract(img)
                    except Exception:
                        pass
                if best_text:
                    ocr_text += best_text + "\n"
            if ocr_text.strip():
                return ocr_text
        except Exception as e:
            register_error('pdf-ocr', f'PDF OCR error / Ошибка OCR PDF {p}', str(e))
    return text

def extract_text_from_docx(p):
    if HAS_DOCX:
        try:
            mod = _robust_import('docx')
            doc = mod.Document(str(p))
            parts = []
            for para in doc.paragraphs:
                if para.text and para.text.strip():
                    parts.append(para.text)
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text and cell.text.strip():
                            parts.append(cell.text)
            if parts:
                return '\n'.join(parts)
        except Exception:
            pass

    if HAS_DOCX2TXT:
        try:
            mod = _robust_import('docx2txt')
            result = mod.process(str(p))
            if result and result.strip():
                return result
        except Exception:
            pass

    try:
        with zipfile.ZipFile(str(p), 'r') as zf:
            target = None
            for name in zf.namelist():
                if name == 'word/document.xml':
                    target = name
                    break
            if target:
                try:
                    data = zf.read(target)
                except zipfile.BadZipFile as e:
                    try:
                        with zf.open(target) as fp:
                            data = fp.read()
                    except Exception as e2:
                        register_error('docx', f'Bad CRC reading / чтение {p}', f'{e} / {e2}')
                        return ""
                except Exception as e:
                    register_error('docx', f'Read error / Ошибка чтения {p}', str(e))
                    return ""
                try:
                    xml = data.decode('utf-8', errors='replace')
                except Exception:
                    xml = data.decode('cp1251', errors='replace')
                texts = re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml, re.DOTALL)
                if texts:
                    joined = ' '.join(t for t in texts if t and t.strip())
                    if joined.strip():
                        return joined
                simple = re.findall(r'>([^<>]{2,})<', xml)
                if simple:
                    joined = ' '.join(t for t in simple if t.strip())
                    if joined.strip():
                        return joined
    except zipfile.BadZipFile as e:
        register_error('docx', f'Corrupted DOCX / Повреждённый DOCX {p}', str(e))
    except Exception as e:
        register_error('docx', f'Open error / Ошибка открытия DOCX {p}', str(e))

    return ""

def extract_text_from_xlsx(p):
    if HAS_OPENPYXL:
        try:
            mod = _robust_import('openpyxl')
            wb = mod.load_workbook(p, read_only=True, data_only=True)
            parts = []
            for sheet in wb.sheetnames:
                ws = wb[sheet]
                for row in ws.iter_rows(values_only=True):
                    r = ' '.join(str(c) for c in row if c is not None and str(c).strip())
                    if r:
                        parts.append(r)
            wb.close()
            if parts:
                return '\n'.join(parts)[:2000000]
        except Exception as e:
            register_error('xlsx', f'Read error / Ошибка чтения {p}', str(e))
    if HAS_PANDAS:
        try:
            pd = _robust_import('pandas')
            sheets = pd.read_excel(str(p), sheet_name=None)
            parts = []
            for name, df in sheets.items():
                parts.append(f"=== {name} ===")
                parts.append(df.to_string(index=False, max_rows=1000))
            return '\n'.join(parts)[:2000000]
        except Exception as e:
            register_error('pandas-xlsx', f'Read error / Ошибка чтения {p}', str(e))
    return ""

def extract_text_from_xls(p):
    if HAS_XLRD:
        try:
            mod = _robust_import('xlrd')
            wb = mod.open_workbook(str(p))
            parts = []
            for sheet in wb.sheets():
                for row in range(sheet.nrows):
                    r = ' '.join(str(sheet.cell_value(row, c)) for c in range(sheet.ncols)
                                 if str(sheet.cell_value(row, c)).strip())
                    if r:
                        parts.append(r)
            return '\n'.join(parts)[:2000000]
        except Exception as e:
            register_error('xls', f'Read error / Ошибка чтения {p}', str(e))
    if HAS_PANDAS:
        try:
            pd = _robust_import('pandas')
            df = pd.read_excel(str(p))
            return df.to_string(index=False, max_rows=2000)[:2000000]
        except Exception:
            pass
    return ""

def extract_text_from_pptx(p):
    if HAS_PPTX:
        try:
            mod = _robust_import('pptx')
            prs = mod.Presentation(str(p))
            parts = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text:
                        parts.append(shape.text)
                try:
                    if slide.has_notes_slide and slide.notes_slide.notes_text_frame.text:
                        parts.append(slide.notes_slide.notes_text_frame.text)
                except Exception:
                    pass
            return '\n'.join(parts)
        except Exception as e:
            register_error('pptx', f'Read error / Ошибка чтения {p}', str(e))
    try:
        with zipfile.ZipFile(str(p), 'r') as zf:
            parts = []
            for name in zf.namelist():
                if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
                    data = zf.read(name).decode('utf-8', errors='replace')
                    texts = re.findall(r'<a:t>(.*?)</a:t>', data, re.DOTALL)
                    if texts:
                        parts.append(' '.join(texts))
            if parts:
                return '\n'.join(parts)
    except Exception:
        pass
    return ""

def extract_text_from_doc(p):
    if HAS_TEXTRACT:
        try:
            mod = _robust_import('textract')
            return mod.process(str(p)).decode('utf-8', errors='ignore')
        except Exception as e:
            register_error('doc', f'Read error / Ошибка чтения {p}', str(e))
    return ""

def extract_text_from_vsdx(p):
    if HAS_TEXTRACT:
        try:
            mod = _robust_import('textract')
            return mod.process(str(p)).decode('utf-8', errors='ignore')
        except Exception as e:
            register_error('vsdx', f'Read error / Ошибка чтения {p}', str(e))
    try:
        with zipfile.ZipFile(str(p), 'r') as zf:
            parts = []
            for name in zf.namelist():
                if name.endswith('.xml') and ('page' in name.lower() or 'document' in name.lower()):
                    data = zf.read(name).decode('utf-8', errors='replace')
                    texts = re.findall(r'<Text[^>]*>(.*?)</Text>', data, re.DOTALL)
                    texts2 = re.findall(r'>([^<>]{3,})<', data)
                    combined = texts + texts2
                    if combined:
                        parts.append(' '.join(t.strip() for t in combined if t.strip()))
            return '\n'.join(parts)[:500000]
    except Exception:
        pass
    return ""

# ----------------------------------------------------------------------
# CAD / Estimating / Mining / Geodetic extraction
# ----------------------------------------------------------------------
def _extract_dxf_text(p: Path) -> str:
    parts = []
    try:
        with open(str(p), 'rb') as f:
            raw = f.read()
        text = None
        for e in ('utf-8', 'cp1251', 'cp866', 'latin1'):
            try:
                text = raw.decode(e)
                if 'SECTION' in text or 'HEADER' in text:
                    break
            except Exception:
                continue
        if text is None:
            text = raw.decode('latin1', errors='replace')

        lines = text.splitlines()
        i = 0
        found_texts = []
        layer_names = set()
        while i < len(lines) - 1:
            code = lines[i].strip()
            value = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if code in ('1', '3', '4') and value:
                if not value.startswith('{') and not value.startswith('AC'):
                    if len(value) > 1:
                        found_texts.append(value)
            if code == '2' and value and 1 < len(value) < 60:
                if re.match(r'^[A-Za-zА-Яа-я0-9_\-\.\s]+$', value):
                    layer_names.add(value)
            i += 2
        if found_texts:
            parts.append("[DXF TEXT] " + " | ".join(found_texts[:200]))
        if layer_names:
            parts.append("[DXF LAYERS] " + ", ".join(sorted(layer_names)[:80]))
    except Exception as e:
        register_error('cad-dxf', f'DXF read error / Ошибка чтения DXF {p}', str(e))
    return '\n'.join(parts)

def _extract_dwg_text(p: Path) -> str:
    parts = []
    try:
        with open(str(p), 'rb') as f:
            raw = f.read(5000000)
        ver = raw[:6].decode('latin1', errors='replace')
        if ver.startswith('AC'):
            ver_map = {
                'AC1015': 'AutoCAD 2000', 'AC1018': 'AutoCAD 2004',
                'AC1021': 'AutoCAD 2007', 'AC1024': 'AutoCAD 2010',
                'AC1027': 'AutoCAD 2013', 'AC1032': 'AutoCAD 2018',
                'AC1035': 'AutoCAD 2025',
            }
            parts.append(f"[DWG] Version / Версия: {ver_map.get(ver, ver)}")
        ascii_strings = re.findall(rb'[\x20-\x7e]{5,}', raw)
        decoded = []
        for s in ascii_strings[:800]:
            try:
                t = s.decode('ascii')
                if any(c.isalpha() for c in t):
                    decoded.append(t)
            except Exception:
                continue
        if decoded:
            parts.append("[DWG Strings] " + " | ".join(decoded[:150]))
        try:
            text_utf16 = raw.decode('utf-16-le', errors='ignore')
            words = re.findall(r'[\u0400-\u04FFa-zA-Z0-9_\-]{4,}', text_utf16)
            if words:
                parts.append("[DWG Cyrillic] " + " | ".join(words[:100]))
        except Exception:
            pass
    except Exception as e:
        register_error('cad-dwg', f'DWG read error / Ошибка чтения DWG {p}', str(e))
    return '\n'.join(parts)

def _extract_kompas_text(p: Path) -> str:
    parts = []
    try:
        with open(str(p), 'rb') as f:
            raw = f.read(5000000)
        try:
            for offset in range(0, min(len(raw) - 2, 2000)):
                if raw[offset] == 0x78 and raw[offset + 1] in (0x01, 0x9c, 0xda):
                    try:
                        decompressed = zlib.decompress(raw[offset:offset + 3000000])
                        text = decompressed.decode('utf-8', errors='replace')
                        texts = re.findall(r'[\u0400-\u04FFa-zA-Z0-9_\-]{3,}', text)
                        if texts:
                            parts.append("[KOMPAS Text / КОМПАС Text] " + " | ".join(texts[:200]))
                        break
                    except Exception:
                        continue
        except Exception:
            pass
        try:
            text_utf16 = raw.decode('utf-16-le', errors='ignore')
            words = re.findall(r'[\u0400-\u04FFa-zA-Z0-9_\-]{4,}', text_utf16)
            if words:
                parts.append("[KOMPAS Cyrillic / КОМПАС Cyrillic] " + " | ".join(words[:150]))
        except Exception:
            pass
        ascii_strings = re.findall(rb'[\x20-\x7e]{5,}', raw)
        decoded = []
        for s in ascii_strings[:300]:
            try:
                t = s.decode('ascii')
                if any(c.isalpha() for c in t):
                    decoded.append(t)
            except Exception:
                continue
        if decoded:
            parts.append("[KOMPAS ASCII / КОМПАС ASCII] " + " | ".join(decoded[:80]))
    except Exception as e:
        register_error('cad-kompas', f'KOMPAS read error / Ошибка чтения КОМПАС {p}', str(e))
    return '\n'.join(parts)

def _extract_grandmeta_text(p: Path) -> str:
    parts = []
    try:
        with open(str(p), 'rb') as f:
            raw = f.read(5000000)
        try:
            text = raw.decode('utf-8', errors='replace')
            if '<?xml' in text[:300] or '<' in text[:100]:
                texts = re.findall(r'>([^<>]{2,})<', text)
                if texts:
                    parts.append("[GrandSmeta / ГрандСмета] " + " | ".join(t.strip() for t in texts[:300] if t.strip()))
        except Exception:
            pass
        if not parts:
            try:
                for offset in range(0, min(len(raw) - 2, 2000)):
                    if raw[offset] == 0x78 and raw[offset + 1] in (0x01, 0x9c, 0xda):
                        try:
                            decompressed = zlib.decompress(raw[offset:offset + 3000000])
                            text = decompressed.decode('utf-8', errors='replace')
                            texts = re.findall(r'[\u0400-\u04FFa-zA-Z0-9_\-]{3,}', text)
                            if texts:
                                parts.append("[GrandSmeta Text] " + " | ".join(texts[:200]))
                            break
                        except Exception:
                            continue
            except Exception:
                pass
        if not parts:
            try:
                text_utf16 = raw.decode('utf-16-le', errors='ignore')
                words = re.findall(r'[\u0400-\u04FFa-zA-Z0-9_\-]{4,}', text_utf16)
                if words:
                    parts.append("[GrandSmeta Cyrillic] " + " | ".join(words[:150]))
            except Exception:
                pass
        if not parts:
            try:
                text_cp = raw.decode('cp1251', errors='ignore')
                words = re.findall(r'[\u0400-\u04FFa-zA-Z0-9_\-]{4,}', text_cp)
                if words:
                    parts.append("[GrandSmeta cp1251] " + " | ".join(words[:150]))
            except Exception:
                pass
    except Exception as e:
        register_error('cad-grandmeta', f'GrandSmeta read error / Ошибка чтения ГрандСмета {p}', str(e))
    return '\n'.join(parts)

def _extract_macromine_text(p: Path) -> str:
    parts = []
    try:
        with open(str(p), 'rb') as f:
            raw = f.read(5000000)
        try:
            for offset in range(0, min(len(raw) - 2, 2000)):
                if raw[offset] == 0x78 and raw[offset + 1] in (0x01, 0x9c, 0xda):
                    try:
                        decompressed = zlib.decompress(raw[offset:offset + 3000000])
                        text = decompressed.decode('utf-8', errors='replace')
                        texts = re.findall(r'[\u0400-\u04FFa-zA-Z0-9_\-]{3,}', text)
                        if texts:
                            parts.append("[MacroMine Text] " + " | ".join(texts[:200]))
                        break
                    except Exception:
                        continue
        except Exception:
            pass
        if not parts:
            try:
                text_utf16 = raw.decode('utf-16-le', errors='ignore')
                words = re.findall(r'[\u0400-\u04FFa-zA-Z0-9_\-]{4,}', text_utf16)
                if words:
                    parts.append("[MacroMine Cyrillic] " + " | ".join(words[:150]))
            except Exception:
                pass
        if not parts:
            try:
                text_cp = raw.decode('cp1251', errors='ignore')
                words = re.findall(r'[\u0400-\u04FFa-zA-Z0-9_\-]{4,}', text_cp)
                if words:
                    parts.append("[MacroMine cp1251] " + " | ".join(words[:150]))
            except Exception:
                pass
    except Exception as e:
        register_error('cad-macromine', f'MacroMine read error / Ошибка чтения MacroMine {p}', str(e))
    return '\n'.join(parts)

def _extract_civil_text(p: Path) -> str:
    ext = p.suffix.lower()
    if ext == '.dwg':
        return _extract_dwg_text(p)
    if ext == '.dxf':
        return _extract_dxf_text(p)
    if ext in ('.xml', '.landxml', '.csv', '.pts'):
        return extract_text_from_txt(p)
    parts = []
    try:
        with open(str(p), 'rb') as f:
            raw = f.read(2000000)
        try:
            text_utf16 = raw.decode('utf-16-le', errors='ignore')
            words = re.findall(r'[\u0400-\u04FFa-zA-Z0-9_\-]{4,}', text_utf16)
            if words:
                parts.append("[Civil Cyrillic] " + " | ".join(words[:100]))
        except Exception:
            pass
        if not parts:
            text_cp = raw.decode('cp1251', errors='ignore')
            words = re.findall(r'[\u0400-\u04FFa-zA-Z0-9_\-]{4,}', text_cp)
            if words:
                parts.append("[Civil cp1251] " + " | ".join(words[:100]))
    except Exception as e:
        register_error('cad-civil', f'Civil read error / Ошибка чтения Civil {p}', str(e))
    return '\n'.join(parts)

def _get_exif_summary(p) -> str:
    if not HAS_EXIFREAD:
        return ""
    try:
        mod = _robust_import('exifread')
        with open(str(p), 'rb') as f:
            tags = mod.process_file(f, details=False)
        interesting = ['Image Make', 'Image Model', 'EXIF DateTimeOriginal',
                       'GPS GPSLatitude', 'GPS GPSLongitude', 'Image Software']
        parts = []
        for k in interesting:
            if k in tags:
                v = str(tags[k])
                if len(v) > 80:
                    v = v[:77] + "..."
                parts.append(f"{k.split()[-1]}: {v}")
        return "; ".join(parts)
    except Exception:
        return ""

def _get_stegano_hint(p) -> str:
    if not HAS_STEGANO:
        return ""
    try:
        mod = _robust_import('stegano.lsb')
        try:
            secret = mod.reveal(str(p))
            if secret:
                return f"LSB message detected / LSB-сообщение обнаружено ({len(secret)} chars)"
        except Exception:
            pass
    except Exception:
        pass
    return ""

def _get_magic_type(p) -> str:
    if HAS_MAGIC:
        try:
            mod = _robust_import('magic')
            try:
                return mod.from_file(str(p), mime=True)
            except Exception:
                return mod.from_file(str(p))
        except Exception:
            pass
    try:
        mod = _robust_import('filetype')
        kind = mod.guess(str(p))
        if kind:
            return f"{kind.mime} ({kind.extension})"
    except Exception:
        pass
    return ""

def _get_pefile_info(p) -> str:
    if not HAS_PEFILE:
        return ""
    try:
        mod = _robust_import('pefile')
        pe = mod.PE(str(p), fast_load=True)
        info = []
        if hasattr(pe, 'FILE_HEADER'):
            m = pe.FILE_HEADER.Machine
            info.append(f"Machine: {hex(m)}")
        if hasattr(pe, 'OPTIONAL_HEADER'):
            ss = pe.OPTIONAL_HEADER.SizeOfImage
            info.append(f"SizeOfImage: {ss}")
        try:
            info.append(f"CompileTime: {datetime.utcfromtimestamp(pe.FILE_HEADER.TimeDateStamp).strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception:
            pass
        pe.close()
        return "; ".join(info)
    except Exception:
        return ""

def extract_text_from_image(p):
    texts = []
    if HAS_OCR and SETTINGS.get('ocr_enabled', True):
        try:
            mod = _robust_import('PIL.Image')
            img = mod.open(str(p))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            if img.width > 2000:
                img.thumbnail((2000, 2000))
            if reader is not None:
                try:
                    t = ' '.join(reader.readtext(img, detail=0, paragraph=True))
                    if t.strip():
                        texts.append(t)
                except Exception as e:
                    register_error('ocr', f'EasyOCR error for / ошибка для {p}', str(e))
            if HAS_TESSERACT:
                try:
                    t = ocr_with_tesseract(img)
                    if t.strip():
                        texts.append(t)
                except Exception:
                    pass
        except Exception as e:
            register_error('ocr', f'OCR error / Ошибка OCR {p}', str(e))
    exif = _get_exif_summary(p)
    if exif:
        texts.append(f"[EXIF] {exif}")
    steg = _get_stegano_hint(p)
    if steg:
        texts.append(f"[Stegano] {steg}")
    return '\n'.join(texts)

def extract_text_from_gif(p):
    texts = []
    if HAS_OCR and SETTINGS.get('ocr_enabled', True):
        try:
            PIL_Image = _robust_import('PIL.Image')
            with PIL_Image.open(str(p)) as img:
                for i, frame in enumerate(PIL_Image.ImageSequence.Iterator(img)):
                    if i > 20:
                        break
                    f = frame.convert('RGB')
                    if f.width > 2000:
                        f.thumbnail((2000, 2000))
                    if reader is not None:
                        try:
                            t = ' '.join(reader.readtext(f, detail=0, paragraph=True))
                            if t.strip():
                                texts.append(t)
                        except Exception:
                            pass
                    if HAS_TESSERACT:
                        t = ocr_with_tesseract(f)
                        if t.strip():
                            texts.append(t)
        except Exception as e:
            register_error('ocr-gif', f'GIF OCR error / Ошибка OCR GIF {p}', str(e))
    return '\n'.join(texts)

# ----------------------------------------------------------------------
# EML / MSG
# ----------------------------------------------------------------------
def _decode_mime_header(value) -> str:
    if value is None:
        return ""
    try:
        parts = email.header.decode_header(value)
        decoded = []
        for part, enc in parts:
            if isinstance(part, bytes):
                if enc:
                    try:
                        decoded.append(part.decode(enc, errors='replace'))
                    except Exception:
                        decoded.append(part.decode('utf-8', errors='replace'))
                else:
                    for e in ('utf-8', 'cp1251', 'koi8-r', 'latin1'):
                        try:
                            decoded.append(part.decode(e))
                            break
                        except Exception:
                            continue
                    else:
                        decoded.append(part.decode('utf-8', errors='replace'))
            else:
                decoded.append(str(part))
        return ''.join(decoded)
    except Exception:
        return str(value)

def _html_to_text(html: str) -> str:
    if not html:
        return ""
    try:
        html = re.sub(r'(?is)<script.*?</script>', ' ', html)
        html = re.sub(r'(?is)<style.*?</style>', ' ', html)
        html = re.sub(r'(?i)<br\s*/?>', '\n', html)
        html = re.sub(r'(?i)</p>', '\n', html)
        html = re.sub(r'(?i)</div>', '\n', html)
        text = re.sub(r'(?s)<[^>]+>', ' ', html)
        try:
            text = html_module.unescape(text)
        except Exception:
            pass
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    except Exception:
        return html

def _process_eml_attachment(name: str, data: bytes, temp_dir: Path) -> str:
    if not name or not data:
        return ""
    tmp_path = None
    try:
        ext = os.path.splitext(name)[1].lower()
        safe_name = re.sub(r'[\\/:*?"<>|]+', '_', name) or "attach.bin"
        tmp_path = temp_dir / safe_name
        tmp_path.write_bytes(data)
        if ext in PDF_EXTS:
            return extract_text_from_pdf(str(tmp_path))
        if ext in DOCX_EXTS:
            return extract_text_from_docx(str(tmp_path))
        if ext in DOC_EXTS:
            return extract_text_from_doc(str(tmp_path))
        if ext in XLSX_EXTS:
            return extract_text_from_xlsx(str(tmp_path))
        if ext in XLS_EXTS:
            return extract_text_from_xls(str(tmp_path))
        if ext in PPTX_EXTS:
            return extract_text_from_pptx(str(tmp_path))
        if ext in ODF_EXTS:
            return extract_text_from_odf(str(tmp_path))
        if ext in RTF_EXTS:
            return extract_text_from_rtf(str(tmp_path))
        if ext in IMAGE_EXTS:
            if ext == '.gif':
                return extract_text_from_gif(str(tmp_path))
            return extract_text_from_image(str(tmp_path))
        if ext in TEXT_EXTS:
            return extract_text_from_txt(str(tmp_path))
        if ext in ARCHIVE_EXTS:
            return extract_text_from_archive(tmp_path)
        if ext in MAIL_EXTS:
            return extract_text_from_eml(str(tmp_path))
        if ext in AUTOCAD_EXTS:
            if ext in ('.dxf', '.dwt', '.dws'):
                return _extract_dxf_text(tmp_path)
            return _extract_dwg_text(tmp_path)
        if ext in KOMPAS_EXTS:
            return _extract_kompas_text(tmp_path)
        if ext in GRANDSMETA_EXTS:
            return _extract_grandmeta_text(tmp_path)
        if ext in MACROMINE_EXTS:
            return _extract_macromine_text(tmp_path)
        if ext in CIVIL_EXTS:
            return _extract_civil_text(tmp_path)
    except Exception:
        pass
    finally:
        try:
            if tmp_path and tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass
    return ""

def extract_text_from_eml(p) -> str:
    parts_text = []
    temp_dir = None
    email_from = ""
    email_to = ""
    email_cc = ""
    email_bcc = ""
    email_subject = ""
    try:
        temp_dir = Path(tempfile.mkdtemp())
        with open(str(p), 'rb') as f:
            raw = f.read()
        try:
            msg = BytesParser(policy=email_policy.default).parsebytes(raw)
        except Exception:
            msg = email.message_from_bytes(raw)

        try:
            email_subject = _decode_mime_header(msg.get('Subject', ''))
            email_from = _decode_mime_header(msg.get('From', ''))
            email_to = _decode_mime_header(msg.get('To', ''))
            email_cc = _decode_mime_header(msg.get('Cc', ''))
            email_bcc = _decode_mime_header(msg.get('Bcc', ''))
            if email_subject:
                parts_text.append(f"[Subject / Тема] {email_subject}")
            if email_from:
                parts_text.append(f"[From / От] {email_from}")
            if email_to:
                parts_text.append(f"[To / Кому] {email_to}")
            if email_cc:
                parts_text.append(f"[Cc / Копия] {email_cc}")
            if email_bcc:
                parts_text.append(f"[Bcc / Скрытая копия] {email_bcc}")
            date_h = _decode_mime_header(msg.get('Date', ''))
            if date_h:
                parts_text.append(f"[Date / Дата] {date_h}")
        except Exception:
            pass

        try:
            with _EML_META_LOCK:
                _EML_META_CACHE[str(Path(p).resolve()).lower()] = {
                    'from': email_from,
                    'to': email_to,
                    'cc': email_cc,
                    'bcc': email_bcc,
                    'subject': email_subject,
                }
        except Exception:
            pass

        attachments_count = 0
        try:
            for part in msg.walk():
                ctype = (part.get_content_type() or '').lower()
                disp = (part.get('Content-Disposition') or '').lower()
                filename = part.get_filename()
                if filename:
                    filename = _decode_mime_header(filename)

                if 'attachment' in disp or (filename and ctype not in ('text/plain', 'text/html')):
                    try:
                        payload = part.get_payload(decode=True) or b""
                    except Exception:
                        payload = b""
                    if payload:
                        attachments_count += 1
                        a_text = _process_eml_attachment(filename or "attach.bin",
                                                         payload, temp_dir)
                        if a_text:
                            parts_text.append(f"\n[Attachment / Вложение: {filename}]\n{a_text}")

                if ctype == 'text/plain':
                    try:
                        payload = part.get_payload(decode=True) or b""
                        charset = part.get_content_charset() or 'utf-8'
                        try:
                            body = payload.decode(charset, errors='replace')
                        except Exception:
                            body = payload.decode('utf-8', errors='replace')
                        body = body.strip()
                        if body:
                            parts_text.append(body)
                    except Exception:
                        pass
                elif ctype == 'text/html':
                    try:
                        payload = part.get_payload(decode=True) or b""
                        charset = part.get_content_charset() or 'utf-8'
                        try:
                            body_html = payload.decode(charset, errors='replace')
                        except Exception:
                            body_html = payload.decode('utf-8', errors='replace')
                        body_text = _html_to_text(body_html)
                        if body_text:
                            parts_text.append(body_text)
                    except Exception:
                        pass
        except Exception:
            pass

        if attachments_count:
            parts_text.append(f"\n[Total attachments / Всего вложений: {attachments_count}]")

    except Exception as e:
        register_error('eml', f'Read error / Ошибка чтения {p}', str(e))
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

    return '\n'.join(parts_text)

def get_eml_meta_for_path(p) -> Dict[str, str]:
    try:
        key = str(Path(p).resolve()).lower()
        with _EML_META_LOCK:
            return dict(_EML_META_CACHE.get(key, {}))
    except Exception:
        return {}

# ----------------------------------------------------------------------
# RAR / 7z / UNRAR
# ----------------------------------------------------------------------
_RAR_TOOL_WARNED = False

def _find_7z_or_unrar():
    candidates = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
        r"C:\Program Files\WinRAR\UnRAR.exe",
        r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
        r"C:\Program Files\WinRAR\Rar.exe",
        r"C:\Program Files (x86)\WinRAR\Rar.exe",
        shutil.which("7z"),
        shutil.which("7za"),
        shutil.which("unrar"),
        shutil.which("rar"),
    ]
    for c in candidates:
        try:
            if c and os.path.isfile(c):
                return c
        except Exception:
            continue
    try:
        for root, dirs, files in os.walk(str(BASE_DIR)):
            depth = root[len(str(BASE_DIR)):].count(os.sep)
            if depth > 3:
                dirs[:] = []
                continue
            for f in files:
                lf = f.lower()
                if lf in ('7z.exe', '7za.exe', 'unrar.exe', 'rar.exe'):
                    return os.path.join(root, f)
    except Exception:
        pass
    return None

def _extract_rar_smart(p: Path, temp_dir: Path, reg_err) -> bool:
    global _RAR_TOOL_WARNED
    if not _RAR_TOOL_WARNED and _find_7z_or_unrar() is None:
        reg_err('archive-rar',
                'RAR archives require external unrar.exe or 7z.exe / RAR-архивы требуют unrar.exe или 7z.exe',
                'Install 7-Zip (https://www.7-zip.org/) or WinRAR.')
        _RAR_TOOL_WARNED = True

    try:
        mod = _robust_import('rarfile')
        tool = _find_7z_or_unrar()
        if tool:
            try:
                mod.UNRAR_TOOL = tool
            except Exception:
                pass
            try:
                mod.SEVENZIP_TOOL = tool
            except Exception:
                pass
        try:
            with mod.RarFile(str(p)) as rf:
                rf.extractall(str(temp_dir))
            return True
        except Exception as e1:
            reg_err('archive-rar', f'rarfile could not extract / не смог распаковать {p}', str(e1))
    except Exception as e:
        reg_err('archive-rar', 'rarfile unavailable / недоступен', str(e))

    tool = _find_7z_or_unrar()
    if tool:
        try:
            base = os.path.basename(tool).lower()
            cmd = None
            if base.startswith('7z'):
                cmd = [tool, 'x', '-y', f'-o{temp_dir}', str(p)]
            elif base.startswith('unrar'):
                cmd = [tool, 'x', '-y', str(p), str(temp_dir) + os.sep]
            elif base.startswith('rar'):
                cmd = [tool, 'x', '-y', str(p), str(temp_dir) + os.sep]
            if cmd:
                r = subprocess.run(cmd, capture_output=True, check=False, timeout=300,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                if r.returncode == 0:
                    return True
                err = (r.stderr or b'').decode('utf-8', errors='replace')[-500:]
                reg_err('archive-rar', f'External tool {base} returned error / вернул ошибку для {p}', err)
        except Exception as e:
            reg_err('archive-rar', f'External tool call error / Ошибка вызова внешнего инструмента для {p}', str(e))

    try:
        if HAS_PY7ZR:
            mod = _robust_import('py7zr')
            with mod.SevenZipFile(str(p), mode='r') as z:
                z.extractall(path=temp_dir)
            return True
    except Exception as e:
        reg_err('archive-rar', f'py7zr could not extract / не смог распаковать {p}', str(e))

    return False

def extract_text_from_archive(p):
    text = ""
    temp_dir = None
    try:
        temp_dir = Path(tempfile.mkdtemp())
        ext = p.suffix.lower()
        extracted = False
        if zipfile.is_zipfile(p):
            try:
                with zipfile.ZipFile(p, 'r') as zf:
                    zf.extractall(temp_dir)
                extracted = True
            except Exception as e:
                register_error('archive-zip', f'ZIP error / Ошибка ZIP {p}', str(e))
        if not extracted and ext == '.rar':
            extracted = _extract_rar_smart(p, temp_dir, register_error)
        if not extracted and ext == '.7z' and HAS_PY7ZR:
            try:
                mod = _robust_import('py7zr')
                with mod.SevenZipFile(str(p), mode='r') as z:
                    z.extractall(path=temp_dir)
                extracted = True
            except Exception as e:
                register_error('archive-7z', f'7z error / Ошибка 7z {p}', str(e))
        if not extracted:
            try:
                if tarfile.is_tarfile(p):
                    with tarfile.open(p, 'r:*') as tf:
                        tf.extractall(temp_dir)
                    extracted = True
            except Exception:
                pass
        if not extracted and ext in ('.gz', '.bz2', '.xz', '.lzma', '.lz', '.z'):
            try:
                import gzip, bz2, lzma
                target = temp_dir / (p.stem or "file")
                if ext == '.gz':
                    with gzip.open(p, 'rb') as fin, open(target, 'wb') as fout:
                        shutil.copyfileobj(fin, fout)
                elif ext == '.bz2':
                    with bz2.open(p, 'rb') as fin, open(target, 'wb') as fout:
                        shutil.copyfileobj(fin, fout)
                elif ext in ('.xz', '.lzma'):
                    with lzma.open(p, 'rb') as fin, open(target, 'wb') as fout:
                        shutil.copyfileobj(fin, fout)
                extracted = True
            except Exception as e:
                register_error('archive-single', f'Decompress error / Ошибка распаковки {p}', str(e))
        if not extracted:
            return ""
        for f in temp_dir.rglob('*'):
            if not f.is_file():
                continue
            fext = f.suffix.lower()
            try:
                if fext in TEXT_EXTS:
                    text += extract_text_from_txt(f) + "\n"
                elif fext in PDF_EXTS:
                    text += extract_text_from_pdf(f) + "\n"
                elif fext in DOCX_EXTS:
                    text += extract_text_from_docx(f) + "\n"
                elif fext in DOC_EXTS:
                    text += extract_text_from_doc(f) + "\n"
                elif fext in XLSX_EXTS:
                    text += extract_text_from_xlsx(f) + "\n"
                elif fext in XLS_EXTS:
                    text += extract_text_from_xls(f) + "\n"
                elif fext in PPTX_EXTS:
                    text += extract_text_from_pptx(f) + "\n"
                elif fext in ODF_EXTS:
                    text += extract_text_from_odf(f) + "\n"
                elif fext in RTF_EXTS:
                    text += extract_text_from_rtf(f) + "\n"
                elif fext in VSDX_EXTS:
                    text += extract_text_from_vsdx(f) + "\n"
                elif fext in IMAGE_EXTS:
                    if fext == '.gif':
                        text += extract_text_from_gif(f) + "\n"
                    else:
                        text += extract_text_from_image(f) + "\n"
                elif fext in MAIL_EXTS:
                    text += extract_text_from_eml(str(f)) + "\n"
                elif fext in AUTOCAD_EXTS:
                    if fext in ('.dxf', '.dwt', '.dws'):
                        text += _extract_dxf_text(f) + "\n"
                    else:
                        text += _extract_dwg_text(f) + "\n"
                elif fext in KOMPAS_EXTS:
                    text += _extract_kompas_text(f) + "\n"
                elif fext in GRANDSMETA_EXTS:
                    text += _extract_grandmeta_text(f) + "\n"
                elif fext in MACROMINE_EXTS:
                    text += _extract_macromine_text(f) + "\n"
                elif fext in CIVIL_EXTS:
                    text += _extract_civil_text(f) + "\n"
                elif fext in ARCHIVE_EXTS or ('.tar.' in f.name.lower()):
                    text += extract_text_from_archive(f) + "\n"
            except Exception as e:
                register_error('archive-inner', f'Inner processing error / Ошибка обработки {f}', str(e))
    except Exception as e:
        register_error('archive', f'Archive read error / Ошибка чтения архива {p}', str(e))
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
    return text

# ======================================================================
# DRIVE DETECTION
# ======================================================================
_DRIVE_TYPE_NAMES = {
    0: "Unknown / Неизвестный", 1: "No root / Нет корня", 2: "Removable / Съёмный",
    3: "Fixed / Фиксированный", 4: "Network / Сетевой", 5: "CD/DVD", 6: "RAM-disk",
}

def _get_win_drive_type(letter: str) -> int:
    if sys.platform != 'win32':
        return 0
    try:
        return ctypes.windll.kernel32.GetDriveTypeW(f"{letter}:\\")
    except Exception:
        return 0

def _get_volume_label_and_fs(letter: str) -> Tuple[str, str]:
    if sys.platform != 'win32':
        return "", ""
    try:
        volume_name = ctypes.create_unicode_buffer(261)
        fs_name = ctypes.create_unicode_buffer(261)
        serial = ctypes.c_ulong()
        max_len = ctypes.c_ulong()
        flags = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetVolumeInformationW(
            f"{letter}:\\", volume_name, 261,
            ctypes.byref(serial), ctypes.byref(max_len), ctypes.byref(flags),
            fs_name, 261,
        )
        if ok:
            return volume_name.value, fs_name.value
    except Exception:
        pass
    return "", ""

def _get_drive_space(letter: str) -> Tuple[int, int]:
    try:
        total = ctypes.c_ulonglong(0)
        free = ctypes.c_ulonglong(0)
        total_free = ctypes.c_ulonglong(0)
        ok = ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            f"{letter}:\\",
            ctypes.byref(free), ctypes.byref(total), ctypes.byref(total_free),
        )
        if ok:
            return total.value, free.value
    except Exception:
        pass
    return 0, 0

def _get_volume_serial(letter: str) -> str:
    if sys.platform != 'win32':
        return ""
    try:
        volume_name = ctypes.create_unicode_buffer(261)
        fs_name = ctypes.create_unicode_buffer(261)
        serial = ctypes.c_ulong()
        max_len = ctypes.c_ulong()
        flags = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetVolumeInformationW(
            f"{letter}:\\", volume_name, 261,
            ctypes.byref(serial), ctypes.byref(max_len), ctypes.byref(flags),
            fs_name, 261,
        )
        if ok:
            return f"{serial.value:08X}"
    except Exception:
        pass
    return ""

def _get_usb_letters_from_wmi() -> Dict[str, Dict[str, str]]:
    result: Dict[str, Dict[str, str]] = {}
    if sys.platform != 'win32':
        return result
    try:
        _init_com()
        mod = _robust_import('wmi')
        c = mod.WMI()
        for disk in c.Win32_DiskDrive():
            iface = (disk.InterfaceType or "").upper()
            media = (disk.MediaType or "").upper()
            model = safe_decode(disk.Model) if disk.Model else ""
            is_usb = ('USB' in iface) or ('USB' in media)
            letters = []
            try:
                for part in c.Win32_DiskPartition(DiskIndex=disk.Index):
                    try:
                        for log in c.Win32_LogicalDisk(DeviceID=part.Name):
                            letters.append(log.DeviceID)
                    except Exception:
                        continue
            except Exception:
                pass
            for L in letters:
                result[L] = {
                    'usb': 'yes' if is_usb else 'no',
                    'model': _clean_wmi_str(model),
                    'media': _clean_wmi_str(disk.MediaType),
                    'interface': _clean_wmi_str(disk.InterfaceType),
                    'serial': _clean_wmi_str(disk.SerialNumber),
                    'size': get_file_size_human(int(disk.Size)) if disk.Size else "",
                    'pnp': _clean_wmi_str(disk.PNPDeviceID),
                }
    except Exception as e:
        register_error('wmi-usb', 'Failed to get USB drives via WMI / Не удалось получить USB-диски через WMI', str(e))
    return result

def get_volume_full_info(path_or_letter) -> Dict[str, str]:
    info = {
        'letter': '', 'label': '', 'fs': '', 'type': '',
        'total': '', 'free': '', 'serial': '',
        'model': '', 'interface': '', 'is_usb': False,
        'device_id': '', 'vendor': '', 'product': '',
        'physical_serial': '', 'size': '',
    }
    if sys.platform != 'win32':
        return info
    try:
        p = str(path_or_letter)
        letter = ''
        if len(p) >= 2 and p[1] == ':':
            letter = p[0].upper()
        else:
            m = re.match(r'^([A-Za-z]):', p)
            if m:
                letter = m.group(1).upper()
        if not letter:
            return info
        info['letter'] = f"{letter}:"
        dt = _get_win_drive_type(letter)
        info['type'] = _DRIVE_TYPE_NAMES.get(dt, 'Unknown')
        label, fs = _get_volume_label_and_fs(letter)
        info['label'] = label or ''
        info['fs'] = fs or ''
        total, free = _get_drive_space(letter)
        info['total'] = get_file_size_human(total) if total else ''
        info['free'] = get_file_size_human(free) if free else ''
        info['serial'] = _get_volume_serial(letter)
        try:
            usb_map = _get_usb_letters_from_wmi()
            key = f"{letter}:"
            if key in usb_map:
                w = usb_map[key]
                info['model'] = w.get('model', '')
                info['interface'] = w.get('interface', '')
                info['is_usb'] = (w.get('usb') == 'yes')
                info['physical_serial'] = w.get('serial', '')
                info['size'] = w.get('size', '')
                pnp = w.get('pnp', '')
                info['device_id'] = pnp
                m = re.search(r'VEN_([^&]+)', pnp)
                if m:
                    info['vendor'] = m.group(1)
                m = re.search(r'PROD_([^&]+)', pnp)
                if m:
                    info['product'] = m.group(1)
        except Exception:
            pass
    except Exception as e:
        register_error('volume-info', 'Volume info error / Ошибка получения информации о томе', str(e))
    return info

def format_drive_info_block(info: Dict[str, str]) -> str:
    if not info:
        return ""
    lines = []
    if info.get('letter'):
        lines.append(f"Drive letter / Буква диска: {info['letter']}")
    if info.get('label'):
        lines.append(f"Volume label / Метка тома: {info['label']}")
    if info.get('fs'):
        lines.append(f"File system / Файловая система: {info['fs']}")
    if info.get('type'):
        lines.append(f"Media type / Тип носителя: {info['type']}")
    if info.get('model'):
        lines.append(f"Model / Модель: {info['model']}")
    if info.get('interface'):
        lines.append(f"Interface / Интерфейс: {info['interface']}")
    if info.get('serial'):
        lines.append(f"Volume serial / Серийный номер тома: {info['serial']}")
    if info.get('physical_serial'):
        lines.append(f"Device serial / Серийный номер устройства: {info['physical_serial']}")
    if info.get('size'):
        lines.append(f"Device size / Размер устройства: {info['size']}")
    elif info.get('total'):
        lines.append(f"Total size / Общий размер: {info['total']}")
    if info.get('free'):
        lines.append(f"Free / Свободно: {info['free']}")
    if info.get('is_usb'):
        lines.append("USB media / USB-носитель: YES / ДА")
    return "\n".join(lines)

def get_drives_detailed(include_network: bool = True) -> List[Dict[str, Any]]:
    usb_info = _get_usb_letters_from_wmi()
    drives: List[Dict[str, Any]] = []

    for letter in string.ascii_uppercase:
        root = f"{letter}:\\"
        try:
            if not os.path.exists(root):
                continue
        except Exception:
            continue

        dt = _get_win_drive_type(letter)
        if dt == 5:
            label, fs = _get_volume_label_and_fs(letter)
            if not fs:
                continue
        if dt == 1:
            continue
        if dt == 4 and not include_network:
            continue

        label, fs = _get_volume_label_and_fs(letter)
        total, free = _get_drive_space(letter)
        wmi_key = f"{letter}:"
        info = usb_info.get(wmi_key, {})
        is_usb = info.get('usb', 'no') == 'yes'
        model = info.get('model', '') or label or '—'

        drives.append({
            'letter': letter, 'root': root,
            'drive_type': dt,
            'type_name': _DRIVE_TYPE_NAMES.get(dt, 'Unknown'),
            'label': label or '', 'fs': fs or '',
            'total': total, 'free': free,
            'total_human': get_file_size_human(total) if total else '—',
            'free_human': get_file_size_human(free) if free else '—',
            'model': model, 'is_usb': is_usb,
            'is_removable': dt == 2, 'is_fixed': dt == 3,
            'is_network': dt == 4, 'is_cdrom': dt == 5,
            'serial': info.get('serial', ''),
            'interface': info.get('interface', ''),
            'pnp': info.get('pnp', ''),
        })

    return drives

def get_all_data_drives() -> List[str]:
    return [d['root'] for d in get_drives_detailed() if not d['is_cdrom']]

def get_local_fixed_drives() -> List[str]:
    return [d['root'] for d in get_drives_detailed(include_network=False)
            if (d['is_fixed'] or d['is_removable']) and not d['is_cdrom']]

def get_usb_drives() -> List[str]:
    return [d['root'] for d in get_drives_detailed(include_network=False) if d['is_usb']]

# ----------------------------------------------------------------------
# Disk info
# ----------------------------------------------------------------------
def get_disk_info_fallback():
    disk_info = []
    if sys.platform == 'win32':
        _init_com()
        ps = '''
        $disks = Get-WmiObject Win32_DiskDrive
        foreach ($d in $disks) {
            $letters = @()
            $parts = Get-WmiObject Win32_DiskPartition -Filter "DiskIndex = $($d.Index)"
            foreach ($p in $parts) {
                $log = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID = '$($p.DeviceID)'"
                if($log){$letters += $log.DeviceID}
            }
            $size = [math]::Round($d.Size/1GB,2)
            Write-Output "$($d.Model)|$($d.Manufacturer)|$($d.SerialNumber)|$($d.InterfaceType)|${size}GB|$($letters -join ',')|$($d.Partitions)"
        }
        '''
        output = None
        for enc in ['utf-8', 'utf-16-le', 'cp866', 'cp1251']:
            try:
                res = subprocess.run(
                    ['powershell', '-NoProfile', '-Command',
                     '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; ' + ps],
                    capture_output=True, timeout=30,
                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
                )
                decoded = res.stdout.decode(enc, errors='replace')
                if decoded and '|' in decoded:
                    output = decoded
                    break
            except Exception:
                continue
        if output:
            for line in output.strip().split('\n'):
                p = line.strip().split('|')
                if len(p) >= 7:
                    disk_info.append({
                        'drive_letter': p[5].split(',') if p[5] else [],
                        'model': safe_decode(p[0]) or "Unknown",
                        'manufacturer': safe_decode(p[1]) or "Unknown",
                        'serial_number': safe_decode(p[2].strip()) or "Unknown",
                        'interface_type': safe_decode(p[3]) or "Unknown",
                        'size': p[4] or "Unknown",
                        'partitions': p[6] or 0,
                        'status': "OK", 'firmware': "Unknown",
                    })
    if not disk_info:
        for letter in string.ascii_uppercase:
            d = f"{letter}:\\"
            if os.path.exists(d):
                disk_info.append({
                    'drive_letter': [d], 'model': "Unknown",
                    'manufacturer': "Unknown", 'serial_number': "Unknown",
                    'interface_type': "Unknown", 'size': "Unknown",
                    'partitions': 1, 'status': "OK", 'firmware': "Unknown",
                })
    return disk_info

def get_detailed_disk_info():
    disk_info = []
    if sys.platform == 'win32' and HAS_WMI:
        try:
            _init_com()
            mod = _robust_import('wmi')
            c = mod.WMI()
            for disk in c.Win32_DiskDrive():
                data = {
                    'drive_letter': [],
                    'model': _clean_wmi_str(disk.Model, "Unknown"),
                    'manufacturer': _clean_wmi_str(disk.Manufacturer, "Unknown"),
                    'serial_number': _clean_wmi_str(disk.SerialNumber, "Unknown").strip() or "Unknown",
                    'interface_type': _clean_wmi_str(disk.InterfaceType, "Unknown"),
                    'size': get_file_size_human(int(disk.Size)) if disk.Size else "Unknown",
                    'partitions': disk.Partitions or 0,
                    'status': _clean_wmi_str(disk.Status, "OK"),
                    'firmware': _clean_wmi_str(disk.FirmwareRevision, "Unknown"),
                }
                try:
                    for part in c.Win32_DiskPartition(DiskIndex=disk.Index):
                        for log in c.Win32_LogicalDisk(DeviceID=part.Name):
                            data['drive_letter'].append(log.DeviceID)
                except Exception:
                    pass
                disk_info.append(data)
            if not disk_info:
                disk_info = get_disk_info_fallback()
        except Exception as e:
            register_error('wmi', 'WMI error, using fallback / Ошибка WMI, используется fallback', str(e))
            disk_info = get_disk_info_fallback()
    else:
        disk_info = get_disk_info_fallback()
    return disk_info

# ----------------------------------------------------------------------
# Keywords
# ----------------------------------------------------------------------
DEFAULT_KEYWORDS = ['паспорт', 'снилс', 'инн', 'пдн', 'договор', 'контракт', 'пароль', 'password',
                    'секретно', 'конфиденциально', 'персональные данные', 'фио', 'фамилия', 'имя',
                    'отчество', 'медкнижка', 'диплом', 'удостоверение', 'закупка', 'билеты']

def load_keywords_from_file(filepath: Path) -> List[str]:
    kw = DEFAULT_KEYWORDS.copy()
    try:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                k = [line.strip().lower() for line in f
                     if line.strip() and not line.startswith('#')]
                if k:
                    kw = k
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {PROGRAM_NAME} - Keywords / Ключевые слова\n# Author / Автор: {AUTHOR}\n\n")
                for w in DEFAULT_KEYWORDS:
                    f.write(f"{w}\n")
    except Exception as e:
        register_error('keywords', 'Keywords load error / Ошибка загрузки ключевых слов', str(e))
    return kw

KEYWORDS_FILE = BASE_DIR / "keywords.txt"
KEYWORDS = load_keywords_from_file(KEYWORDS_FILE)

# ----------------------------------------------------------------------
# Normalize network path
# ----------------------------------------------------------------------
def normalize_network_path(s: str) -> str:
    s = s.strip().strip('"').strip("'").replace('/', '\\')
    if s.startswith('\\') and not s.startswith('\\\\'):
        s = '\\\\' + s[1:]
    return s.rstrip('\\')

# ----------------------------------------------------------------------
# Console progress bar
# ----------------------------------------------------------------------
class ColoredProgressBar:
    def __init__(self, total, prefix="Progress / Прогресс", length=40, color=Fore.GREEN):
        self.total = total
        self.prefix = prefix
        self.length = min(length, max(10, get_console_width() - 40))
        self.current = 0
        self.start = time.time()
        self.color = color

    def update(self, n=1):
        self.current += n
        if self.total == 0:
            return
        try:
            pct = 100 * self.current / self.total
            filled = int(self.length * self.current / self.total)
            bar = '#' * filled + '.' * (self.length - filled)
            elapsed = time.time() - self.start
            eta = (elapsed / self.current) * (self.total - self.current) if self.current > 0 else 0
            sys.stdout.write(
                f'\r  {self.prefix}: |{self.color}{bar}{Style.RESET_ALL}| '
                f'{self.color}{pct:.1f}%{Style.RESET_ALL} '
                f'[{self.current}/{self.total}] ETA: {eta:.0f}s'
            )
            sys.stdout.flush()
        except Exception:
            pass

    def finish(self):
        if self.total == 0:
            return
        try:
            elapsed = time.time() - self.start
            sys.stdout.write(
                f'\r  {self.prefix}: |{self.color}{"#" * self.length}{Style.RESET_ALL}| '
                f'{self.color}100.0%{Style.RESET_ALL} '
                f'[{self.current}/{self.current}] Time / Время: {elapsed:.1f}s\n'
            )
            sys.stdout.flush()
        except Exception:
            pass

# ----------------------------------------------------------------------
# Data class
# ----------------------------------------------------------------------
try:
    from dataclasses import dataclass, asdict

    @dataclass
    class FileExtendedInfo:
        path: str
        filename: str
        extension: str
        size: int
        size_human: str
        created_time: str
        modified_time: str
        accessed_time: str
        file_owner: str
        document_author: str
        last_saved_by: str
        computer_name: str
        is_readonly: bool
        is_hidden: bool
        is_system: bool
        is_archive: bool
        keywords_matched: str
        content_preview: str
        disk_info: str = ""
        disk_serial: str = ""
        disk_model: str = ""
        disk_letter: str = ""
        creator: str = ""
        email_from: str = ""
        email_to: str = ""
        drive_full_info: str = ""
except ImportError:
    from collections import namedtuple
    FileExtendedInfo = namedtuple('FileExtendedInfo', [
        'path', 'filename', 'extension', 'size', 'size_human',
        'created_time', 'modified_time', 'accessed_time',
        'file_owner', 'document_author', 'last_saved_by', 'computer_name',
        'is_readonly', 'is_hidden', 'is_system', 'is_archive',
        'keywords_matched', 'content_preview',
        'disk_info', 'disk_serial', 'disk_model', 'disk_letter',
        'creator', 'email_from', 'email_to', 'drive_full_info',
    ])

# ======================================================================
# CHECKPOINT
# ======================================================================
CHECKPOINT_LOCK = threading.Lock()

def _targets_to_key(paths: List[Path]) -> str:
    try:
        norm = sorted(str(Path(p).resolve()).lower() for p in paths)
        return "|".join(norm)
    except Exception:
        return "|".join(sorted(str(p) for p in paths))

def _save_checkpoint(paths: List[Path], processed: set, results: list,
                     total_files: int, started_at: str):
    try:
        data = {
            'version': VERSION,
            'targets': [str(p) for p in paths],
            'targets_key': _targets_to_key(paths),
            'processed': list(processed),
            'results': [(asdict(r) if hasattr(r, '__dataclass_fields__')
                         else dict(r._asdict())) for r in results],
            'total_files': int(total_files),
            'started_at': started_at,
            'saved_at': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
        }
        tmp = CHECKPOINT_FILE.with_suffix('.tmp')
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        os.replace(str(tmp), str(CHECKPOINT_FILE))
    except Exception as e:
        register_error('checkpoint', 'Checkpoint save error / Не удалось сохранить чекпоинт', str(e))

def _load_checkpoint(paths: List[Path]):
    try:
        if not CHECKPOINT_FILE.exists():
            return None
        with open(str(CHECKPOINT_FILE), 'r', encoding='utf-8') as f:
            data = json.load(f)
        key = _targets_to_key(paths)
        if data.get('targets_key') != key:
            return None
        processed = set(data.get('processed', []))
        results_dicts = data.get('results', [])
        results = []
        for rd in results_dicts:
            try:
                if hasattr(FileExtendedInfo, '__dataclass_fields__'):
                    filled = {}
                    for k in FileExtendedInfo.__dataclass_fields__.keys():
                        filled[k] = rd.get(k, '')
                    results.append(FileExtendedInfo(**filled))
                else:
                    filled = {}
                    for k in FileExtendedInfo._fields:
                        filled[k] = rd.get(k, '')
                    results.append(FileExtendedInfo(**filled))
            except Exception:
                continue
        total_files = int(data.get('total_files', 0))
        started_at = data.get('started_at', '')
        return processed, results, total_files, started_at
    except Exception as e:
        register_error('checkpoint', 'Checkpoint read error / Не удалось прочитать чекпоинт', str(e))
        return None

def _clear_checkpoint():
    try:
        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()
    except Exception:
        pass


def reset_checkpoint() -> bool:
    """Reset checkpoint file and return success status.
    Сбросить файл чекпоинта и вернуть статус успеха."""
    try:
        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()
            return True
        return True
    except Exception as e:
        register_error('checkpoint', 'Checkpoint reset error / Ошибка сброса чекпоинта', str(e))
        return False


def get_checkpoint_info() -> Optional[Dict[str, Any]]:
    """Get checkpoint information without loading full data.
    Получить информацию о чекпоинте без загрузки полных данных."""
    try:
        if not CHECKPOINT_FILE.exists():
            return None
        with open(str(CHECKPOINT_FILE), 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {
            'targets': data.get('targets', []),
            'processed_count': len(data.get('processed', [])),
            'results_count': len(data.get('results', [])),
            'total_files': data.get('total_files', 0),
            'started_at': data.get('started_at', ''),
            'saved_at': data.get('saved_at', ''),
            'version': data.get('version', ''),
        }
    except Exception as e:
        register_error('checkpoint', 'Checkpoint info read error / Ошибка чтения информации о чекпоинте', str(e))
        return None

# ======================================================================
# AGGREGATED CONCLUSIONS
# ======================================================================
def collect_forensic_summary(records) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        'total_files': len(records),
        'by_category': {},
        'by_keyword': {},
        'by_extension': {},
        'by_owner': {},
        'by_author': {},
        'by_disk': {},
        'by_year_modified': {},
        'exif_summary': {'with_exif': 0, 'with_gps': 0},
        'stegano_candidates': 0,
        'pdf_suspicious': 0,
        'registry_hits': 0,
        'mail_hits': 0,
        'usb_hits': 0,
        'forensic_hits': 0,
        'exec_hits': 0,
        'cad_hits': 0,
    }

    cat_office = DOCX_EXTS | DOC_EXTS | XLSX_EXTS | XLS_EXTS | PPTX_EXTS | ODF_EXTS | RTF_EXTS

    for r in records:
        try:
            ext = (r.extension or '').lower()
            if ext in IMAGE_EXTS:
                cat = 'Images / Изображения'
            elif ext in ARCHIVE_EXTS:
                cat = 'Archives / Архивы'
            elif ext in PDF_EXTS:
                cat = 'PDF'
            elif ext in cat_office:
                cat = 'Office documents / Офисные документы'
            elif ext in MAIL_EXTS:
                cat = 'Mail (EML/MSG) / Почта'
                summary['mail_hits'] += 1
            elif ext in AUTOCAD_EXTS:
                cat = 'AutoCAD (DWG/DXF)'
                summary['cad_hits'] += 1
            elif ext in KOMPAS_EXTS:
                cat = 'KOMPAS / КОМПАС'
                summary['cad_hits'] += 1
            elif ext in GRANDSMETA_EXTS:
                cat = 'GrandSmeta / ГрандСмета'
                summary['cad_hits'] += 1
            elif ext in MACROMINE_EXTS:
                cat = 'MacroMine'
                summary['cad_hits'] += 1
            elif ext in CIVIL_EXTS:
                cat = 'Civil 3D'
                summary['cad_hits'] += 1
            elif ext in TEXT_EXTS:
                cat = 'Text/Code/Data / Текст/Код/Данные'
            elif ext in EXEC_EXTS:
                cat = 'Executables/Scripts / Исполняемые/Скрипты'
                summary['exec_hits'] += 1
            elif ext in FORENSIC_EXTS:
                cat = 'Forensic images / Форензик-образы'
                summary['forensic_hits'] += 1
            elif ext in REGISTRY_EXTS:
                cat = 'Registry/Logs / Реестр/Журналы'
                summary['registry_hits'] += 1
            else:
                cat = 'Other / Прочее'
            summary['by_category'][cat] = summary['by_category'].get(cat, 0) + 1

            e = ext or '(none / без)'
            summary['by_extension'][e] = summary['by_extension'].get(e, 0) + 1

            for kw in (r.keywords_matched or '').split(','):
                kw = kw.strip().lower()
                if kw:
                    summary['by_keyword'][kw] = summary['by_keyword'].get(kw, 0) + 1

            ow = (r.file_owner or '').strip() or '—'
            au = (r.document_author or '').strip() or '—'
            dk = (r.disk_letter or '').strip() or '—'
            summary['by_owner'][ow] = summary['by_owner'].get(ow, 0) + 1
            summary['by_author'][au] = summary['by_author'].get(au, 0) + 1
            summary['by_disk'][dk] = summary['by_disk'].get(dk, 0) + 1

            y = '—'
            try:
                if r.modified_time and len(r.modified_time) >= 10:
                    y = r.modified_time[-4:]
            except Exception:
                pass
            summary['by_year_modified'][y] = summary['by_year_modified'].get(y, 0) + 1

            if ext in IMAGE_EXTS:
                preview_low = (r.content_preview or '').lower()
                if '[exif]' in preview_low or 'exif' in preview_low:
                    summary['exif_summary']['with_exif'] += 1
                if 'gps' in preview_low:
                    summary['exif_summary']['with_gps'] += 1

            try:
                if ext in IMAGE_EXTS and int(r.size or 0) > 2 * 1024 * 1024 and not (r.keywords_matched or '').strip():
                    summary['stegano_candidates'] += 1
            except Exception:
                pass

            if ext in PDF_EXTS:
                pl = (r.content_preview or '').lower()
                if any(t in pl for t in ('javascript', '/js', '/openaction', '/launch', '/embeddedfile')):
                    summary['pdf_suspicious'] += 1

            if 'usb' in (r.drive_full_info or '').lower() or 'usb' in (r.disk_model or '').lower():
                summary['usb_hits'] += 1
        except Exception:
            continue

    def _top(d, n=10):
        return sorted(d.items(), key=lambda x: -x[1])[:n]

    summary['by_extension'] = dict(_top(summary['by_extension'], 15))
    summary['by_owner'] = dict(_top(summary['by_owner'], 10))
    summary['by_author'] = dict(_top(summary['by_author'], 10))
    summary['by_keyword'] = dict(_top(summary['by_keyword'], 20))
    return summary

# ======================================================================
# WORD REPORT
# ======================================================================
_FONT_CACHE = {}

def _get_font():
    try:
        ImageFont = _robust_import('PIL.ImageFont')
    except Exception:
        return None
    if 'font' in _FONT_CACHE:
        return _FONT_CACHE['font']
    font = None
    try:
        for cand in [
            r"C:\Windows\Fonts\consola.ttf",
            r"C:\Windows\Fonts\lucon.ttf",
            r"C:\Windows\Fonts\arial.ttf",
        ]:
            if os.path.isfile(cand):
                font = ImageFont.truetype(cand, 14)
                break
    except Exception:
        font = None
    if font is None:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
    _FONT_CACHE['font'] = font
    return font

def _render_content_to_image(record) -> Optional[str]:
    try:
        PIL_Image = _robust_import('PIL.Image')
        PIL_ImageDraw = _robust_import('PIL.ImageDraw')
    except Exception:
        return None

    try:
        path = record.path
        ext = (record.extension or '').lower()

        if ext in IMAGE_EXTS:
            try:
                img = PIL_Image.open(path)
                img.thumbnail((900, 900))
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                tmp = Path(tempfile.gettempdir()) / f"fa_pro_{int(time.time() * 1000)}.png"
                img.save(tmp, 'PNG')
                return str(tmp)
            except Exception:
                pass

        text = record.content_preview or "(content not extracted / содержимое не извлечено)"
        if not text.strip():
            text = "(empty / пусто)"
        text = text[:3000]

        font = _get_font()

        line_h = 18
        max_lines = 45
        lines = []
        for raw_line in text.splitlines() or [text]:
            raw_line = raw_line.replace('\t', '    ')
            while len(raw_line) > 110:
                lines.append(raw_line[:110])
                raw_line = raw_line[110:]
            lines.append(raw_line)
            if len(lines) >= max_lines:
                break
        if len(lines) >= max_lines:
            lines.append("… (truncated / сокращено)")

        width = 1000
        height = max(120, 40 + line_h * len(lines))
        img = PIL_Image.new('RGB', (width, height), (255, 255, 255))
        draw = PIL_ImageDraw.Draw(img)
        draw.rectangle([0, 0, width - 1, height - 1], outline=(180, 180, 180))
        try:
            draw.text((10, 6), f"Content / Содержимое: {Path(path).name}", fill=(0, 0, 0), font=font)
        except Exception:
            draw.text((10, 6), f"Content: {Path(path).name}", fill=(0, 0, 0))
        y = 30
        for ln in lines:
            try:
                draw.text((10, y), ln, fill=(0, 0, 0), font=font)
            except Exception:
                draw.text((10, y), ln, fill=(0, 0, 0))
            y += line_h

        tmp = Path(tempfile.gettempdir()) / f"fa_pro_{int(time.time() * 1000)}.png"
        img.save(tmp, 'PNG')
        return str(tmp)
    except Exception as e:
        register_error('word-screenshot', 'Screenshot generation error / Не удалось сгенерировать скриншот', str(e))
        return None


def _resolve_to_unc(path: str) -> str:
    """If path starts with a mapped drive letter (Z:\\...), try to resolve
    it to a UNC path (\\\\server\\share\\...) via WinAPI. Returns original
    path if not mapped or on non-Windows.
    Если путь начинается с буквы мапленного диска (Z:\\...), пытается
    преобразовать его в UNC-путь (\\\\server\\share\\...) через WinAPI.
    Возвращает исходный путь, если диск не маплен или ОС не Windows."""
    if sys.platform != 'win32':
        return path
    try:
        p = str(path)
        if len(p) < 2 or p[1] != ':':
            return path
        letter = p[0].upper()
        drive = f"{letter}:"
        buf_len = ctypes.c_ulong(1024)
        buf = ctypes.create_unicode_buffer(buf_len.value)
        res = ctypes.windll.mpr.WNetGetConnectionW(drive, buf, ctypes.byref(buf_len))
        if res == 0 and buf.value:
            unc_root = buf.value
            rest = p[2:].lstrip('\\')
            if rest:
                return unc_root.rstrip('\\') + '\\' + rest
            return unc_root
    except Exception:
        pass
    return path


def _quote_url_segment(segment: str) -> str:
    """Percent-encode a single URL path segment (UTF-8).
    Процентное кодирование одного сегмента URL (UTF-8)."""
    try:
        from urllib.parse import quote
        return quote(segment, safe='')
    except Exception:
        return segment


def _file_url(path: str) -> str:
    """Build a working file:// URL for local, mapped and UNC paths.
    For mapped drives it prefers UNC form (\\\\server\\share\\...) because
    Word opens UNC links more reliably than file:///Z:/...
    Формирует рабочую ссылку file:// для локальных, мапленных и UNC путей.
    Для мапленных дисков предпочитает UNC-форму, т.к. Word надёжнее
    открывает UNC-ссылки, чем file:///Z:/..."""
    try:
        p = str(path).strip()
        if not p:
            return ""
        p = p.replace('/', '\\')

        # Try to resolve mapped drive (Z:\...) to UNC (\\server\share\...)
        p = _resolve_to_unc(p)

        # UNC path (\\server\share\...) → file://server/share/...
        if p.startswith('\\\\'):
            body = p[2:].replace('\\', '/')
            segments = body.split('/')
            encoded = '/'.join(_quote_url_segment(s) for s in segments)
            return 'file://' + encoded

        # Local drive (C:\...) → file:///C:/...
        body = p.replace('\\', '/')
        segments = body.split('/')
        if segments and len(segments[0]) == 2 and segments[0][1] == ':':
            drive = segments[0]
            rest = segments[1:]
            encoded = '/'.join(_quote_url_segment(s) for s in rest)
            if encoded:
                return 'file:///' + drive + '/' + encoded
            return 'file:///' + drive + '/'
        # Fallback / Запасной вариант
        encoded = '/'.join(_quote_url_segment(s) for s in segments)
        return 'file:///' + encoded
    except Exception:
        try:
            return "file:///" + str(path).replace("\\", "/").lstrip("/")
        except Exception:
            return str(path)


def _add_hyperlink(paragraph, url: str, text: str, color: str = "0563C1", underline: bool = True):
    """Add a working hyperlink to a python-docx paragraph.
    Добавляет рабочую гиперссылку в параграф python-docx."""
    try:
        docx_mod = _robust_import('docx')
        OxmlElement = _robust_import('docx.oxml.shared').OxmlElement
        qn = _robust_import('docx.oxml.shared').qn
        part = paragraph.part

        if not url:
            paragraph.add_run(text)
            return None

        r_id = part.relate_to(
            url,
            docx_mod.opc.constants.RELATIONSHIP_TYPE.HYPERLINK,
            is_external=True,
        )
        hyperlink = OxmlElement('w:hyperlink')
        hyperlink.set(qn('r:id'), r_id)
        new_run = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        if color:
            c = OxmlElement('w:color')
            c.set(qn('w:val'), color)
            rPr.append(c)
        if underline:
            u = OxmlElement('w:u')
            u.set(qn('w:val'), 'single')
            rPr.append(u)
        new_run.append(rPr)
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = text
        new_run.append(t)
        hyperlink.append(new_run)
        paragraph._p.append(hyperlink)
        return hyperlink
    except Exception as e:
        register_error('word-hyperlink', 'Hyperlink add error / Не удалось добавить гиперссылку', str(e))
        try:
            paragraph.add_run(text)
        except Exception:
            pass
        return None


def save_docx_report(filepath: Path, records: List[Any], disk_info: List[Dict[str, Any]],
                     officer_info: Optional[Dict[str, str]] = None,
                     audit_started: str = "", audit_finished: str = "",
                     scan_targets: Optional[List[str]] = None,
                     scan_duration: str = "") -> bool:
    temp_images: List[str] = []
    try:
        Document = _robust_import('docx').Document
        Pt = _robust_import('docx.shared').Pt
        Cm = _robust_import('docx.shared').Cm
        WD_ALIGN_PARAGRAPH = _robust_import('docx.enum.text').WD_ALIGN_PARAGRAPH
        WD_TABLE_ALIGNMENT = _robust_import('docx.enum.table').WD_TABLE_ALIGNMENT
    except Exception as e:
        register_error('word', 'python-docx unavailable / недоступен', str(e))
        return False

    try:
        doc = Document()

        title = doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title.add_run(tr('word_title'))
        run.bold = True
        run.font.size = Pt(18)

        doc.add_paragraph()
        subtitle = doc.add_paragraph()
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sr = subtitle.add_run(tr('word_subtitle', name=PROGRAM_NAME, ver=VERSION))
        sr.bold = True
        sr.font.size = Pt(14)

        doc.add_paragraph()
        info = doc.add_paragraph()
        info.add_run(tr('word_author_prog', a=AUTHOR) + "\n").italic = True
        info.add_run(tr('word_license', l=LICENSE) + "\n")
        info.add_run(tr('word_github', g=GITHUB) + "\n")
        info.add_run(tr('word_generated', dt=datetime.now().strftime('%d.%m.%Y %H:%M:%S')) + "\n")
        info.add_run(tr('word_computer', c=get_computer_name()) + "\n")
        if audit_started:
            info.add_run(tr('word_audit_start', dt=audit_started) + "\n")
        if audit_finished:
            info.add_run(tr('word_audit_end', dt=audit_finished) + "\n")
        if scan_duration:
            info.add_run(f"{tr('word_elapsed')}: {scan_duration}\n")

        officer_info = officer_info or {}
        if officer_info.get('fio') or officer_info.get('position') or officer_info.get('department'):
            doc.add_paragraph()
            ob = doc.add_paragraph()
            ob.add_run(tr('word_officer_header') + "\n").bold = True
            if officer_info.get('fio'):
                ob.add_run(tr('word_officer_fio', v=officer_info['fio']) + "\n")
            if officer_info.get('position'):
                ob.add_run(tr('word_officer_position', v=officer_info['position']) + "\n")
            if officer_info.get('department'):
                ob.add_run(tr('word_officer_department', v=officer_info['department']) + "\n")
            if officer_info.get('contact'):
                ob.add_run(tr('word_officer_contact', v=officer_info['contact']) + "\n")

        doc.add_page_break()

        doc.add_heading(tr('word_h1_summary'), level=1)
        st = doc.add_table(rows=0, cols=2)
        st.style = 'Table Grid'
        for k, v in [
            (tr('word_total_found'), str(len(records))),
            (tr('word_computer_scan'), get_computer_name()),
            (tr('word_audit_started'), audit_started or "—"),
            (tr('word_audit_finished'), audit_finished or "—"),
            (tr('word_elapsed'), scan_duration or "—"),
            (tr('word_ocr_status'), f"EasyOCR: {'YES/ДА' if LIBRARY_STATUS.get('easyocr') else 'NO/НЕТ'}, "
                                     f"Tesseract: {'YES/ДА' if HAS_TESSERACT else 'NO/НЕТ'}"),
        ]:
            row = st.add_row().cells
            row[0].text = k
            row[1].text = v

        fs = collect_forensic_summary(records)
        doc.add_heading(tr('word_h1_1_conclusions'), level=2)

        doc.add_paragraph(tr('word_categories')).bold = True
        t = doc.add_table(rows=1, cols=2)
        t.style = 'Table Grid'
        hdr = t.rows[0].cells
        hdr[0].text = tr('word_category')
        hdr[1].text = tr('word_count')
        for cat, cnt in sorted(fs['by_category'].items(), key=lambda x: -x[1]):
            row = t.add_row().cells
            row[0].text = cat
            row[1].text = str(cnt)

        doc.add_paragraph()
        doc.add_paragraph(tr('word_extensions_top')).bold = True
        t = doc.add_table(rows=1, cols=2)
        t.style = 'Table Grid'
        hdr = t.rows[0].cells
        hdr[0].text = tr('word_extension')
        hdr[1].text = tr('word_count')
        for ext, cnt in fs['by_extension'].items():
            row = t.add_row().cells
            row[0].text = str(ext)
            row[1].text = str(cnt)

        if fs['by_keyword']:
            doc.add_paragraph()
            doc.add_paragraph(tr('word_keywords_top')).bold = True
            t = doc.add_table(rows=1, cols=2)
            t.style = 'Table Grid'
            hdr = t.rows[0].cells
            hdr[0].text = tr('word_keyword')
            hdr[1].text = tr('word_files_found')
            for kw, cnt in fs['by_keyword'].items():
                row = t.add_row().cells
                row[0].text = str(kw)
                row[1].text = str(cnt)

        if fs['by_owner']:
            doc.add_paragraph()
            doc.add_paragraph(tr('word_owners_top')).bold = True
            t = doc.add_table(rows=1, cols=2)
            t.style = 'Table Grid'
            hdr = t.rows[0].cells
            hdr[0].text = tr('word_owner')
            hdr[1].text = tr('word_count')
            for ow, cnt in fs['by_owner'].items():
                row = t.add_row().cells
                row[0].text = str(ow)
                row[1].text = str(cnt)

        if fs['by_author']:
            doc.add_paragraph()
            doc.add_paragraph(tr('word_authors_top')).bold = True
            t = doc.add_table(rows=1, cols=2)
            t.style = 'Table Grid'
            hdr = t.rows[0].cells
            hdr[0].text = tr('word_author')
            hdr[1].text = tr('word_count')
            for au, cnt in fs['by_author'].items():
                row = t.add_row().cells
                row[0].text = str(au)
                row[1].text = str(cnt)

        doc.add_paragraph()
        doc.add_paragraph(tr('word_forensic_metrics')).bold = True
        t = doc.add_table(rows=0, cols=2)
        t.style = 'Table Grid'
        for k, v in [
            (tr('word_exif'), str(fs['exif_summary']['with_exif'])),
            (tr('word_gps'), str(fs['exif_summary']['with_gps'])),
            (tr('word_stegano'), str(fs['stegano_candidates'])),
            (tr('word_pdf_susp'), str(fs['pdf_suspicious'])),
            (tr('word_registry'), str(fs['registry_hits'])),
            (tr('word_mail'), str(fs.get('mail_hits', 0))),
            (tr('word_usb'), str(fs['usb_hits'])),
            (tr('word_forensic'), str(fs['forensic_hits'])),
            (tr('word_exec'), str(fs['exec_hits'])),
            (tr('word_cad'), str(fs.get('cad_hits', 0))),
        ]:
            row = t.add_row().cells
            row[0].text = k
            row[1].text = v

        doc.add_heading(tr('word_h2_media'), level=1)
        if disk_info:
            for i, d in enumerate(disk_info, 1):
                doc.add_heading(tr('word_h2_disk', i=i), level=2)
                t = doc.add_table(rows=0, cols=2)
                t.style = 'Table Grid'
                for k, v in [
                    (tr('word_model'), safe_decode(d.get('model', '—'))),
                    (tr('word_manufacturer'), safe_decode(d.get('manufacturer', '—'))),
                    (tr('word_serial'), safe_decode(d.get('serial_number', '—'))),
                    (tr('word_interface'), safe_decode(d.get('interface_type', '—'))),
                    (tr('word_size'), str(d.get('size', '—'))),
                    (tr('word_partitions'), str(d.get('partitions', 0))),
                    (tr('word_drive_letters'), ", ".join(d.get('drive_letter', []))),
                ]:
                    row = t.add_row().cells
                    row[0].text = k
                    row[1].text = v
        else:
            doc.add_paragraph("Disk info unavailable / Информация о дисках недоступна.")

        if scan_targets:
            doc.add_heading(tr('word_h2_1_scan_media'), level=2)
            for i, tgt in enumerate(scan_targets, 1):
                info = get_volume_full_info(tgt)
                block = format_drive_info_block(info)
                if not block:
                    continue
                doc.add_heading(f"2.1.{i}. {tgt}", level=3)
                t = doc.add_table(rows=0, cols=2)
                t.style = 'Table Grid'
                for line in block.splitlines():
                    if ':' in line:
                        k, v = line.split(':', 1)
                        row = t.add_row().cells
                        row[0].text = k.strip()
                        row[1].text = v.strip()

        doc.add_heading(tr('word_h3_files_table'), level=1)
        t = doc.add_table(rows=1, cols=7)
        t.style = 'Table Grid'
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr = t.rows[0].cells
        for idx, text in enumerate([tr('word_num'), tr('word_filename'), tr('word_path'), tr('word_size'),
                                     tr('word_keywords'), tr('word_owner'), tr('word_modified')]):
            hdr[idx].text = text
            for p in hdr[idx].paragraphs:
                for r in p.runs:
                    r.bold = True

        for i, rec in enumerate(records, 1):
            row = t.add_row().cells
            row[0].text = str(i)
            row[1].text = safe_decode(rec.filename)
            try:
                p = row[2].paragraphs[0]
                for r in list(p.runs):
                    r.text = ""
                file_url = _file_url(rec.path)
                _add_hyperlink(p, file_url, safe_decode(rec.path))
            except Exception:
                row[2].text = safe_decode(rec.path)
            row[3].text = rec.size_human
            row[4].text = safe_decode(rec.keywords_matched)
            row[5].text = safe_decode(rec.file_owner)
            row[6].text = rec.modified_time

        doc.add_page_break()
        doc.add_heading(tr('word_h4_details'), level=1)

        for i, rec in enumerate(records, 1):
            doc.add_heading(f"4.{i}. {safe_decode(rec.filename)}", level=2)

            meta = doc.add_table(rows=0, cols=2)
            meta.style = 'Table Grid'

            rows_meta = [
                (tr('word_full_path'), safe_decode(rec.path)),
                (tr('word_extension2'), safe_decode(rec.extension)),
                (tr('word_size2'), f"{rec.size:,} bytes / байт ({rec.size_human})"),
                (tr('word_created'), rec.created_time),
                (tr('word_modified2'), rec.modified_time),
                (tr('word_accessed'), rec.accessed_time),
                (tr('word_file_creator'), safe_decode(getattr(rec, 'creator', '') or tr('word_not_specified'))),
                (tr('word_file_owner'), safe_decode(rec.file_owner)),
                (tr('word_doc_author'), safe_decode(rec.document_author)),
                (tr('word_last_saved_by'), safe_decode(rec.last_saved_by)),
                (tr('word_computer_scan'), safe_decode(rec.computer_name)),
                (tr('word_readonly'), tr('word_yes') if rec.is_readonly else tr('word_no')),
                (tr('word_hidden'), tr('word_yes') if rec.is_hidden else tr('word_no')),
                (tr('word_system'), tr('word_yes') if rec.is_system else tr('word_no')),
                (tr('word_archive'), tr('word_yes') if rec.is_archive else tr('word_no')),
                (tr('word_disk_letter'), rec.disk_letter or "—"),
                (tr('word_disk_model'), safe_decode(rec.disk_model)),
                (tr('word_disk_serial'), safe_decode(rec.disk_serial)),
                (tr('word_keywords2'), safe_decode(rec.keywords_matched)),
            ]

            ext_low = (rec.extension or '').lower()
            if ext_low in MAIL_EXTS:
                email_from = safe_decode(getattr(rec, 'email_from', '') or '')
                email_to = safe_decode(getattr(rec, 'email_to', '') or '')
                idx_creator = None
                for j, (k, v) in enumerate(rows_meta):
                    if k == tr('word_file_creator'):
                        idx_creator = j
                        break
                insert_pos = (idx_creator + 1) if idx_creator is not None else 1
                email_rows = []
                if email_from:
                    email_rows.append((tr('word_mail_sender'), email_from))
                if email_to:
                    email_rows.append((tr('word_mail_recipient'), email_to))
                for k, v in reversed(email_rows):
                    rows_meta.insert(insert_pos, (k, v))

            for k, v in rows_meta:
                row = meta.add_row().cells
                row[0].text = k
                if k == tr('word_full_path'):
                    try:
                        p = row[1].paragraphs[0]
                        for r in list(p.runs):
                            r.text = ""
                        file_url = _file_url(rec.path)
                        _add_hyperlink(p, file_url, safe_decode(rec.path))
                    except Exception:
                        row[1].text = v
                else:
                    row[1].text = v

            if rec.drive_full_info:
                doc.add_paragraph(tr('word_drive_chars')).bold = True
                tn = doc.add_table(rows=0, cols=2)
                tn.style = 'Table Grid'
                for line in rec.drive_full_info.splitlines():
                    if ':' in line:
                        k, v = line.split(':', 1)
                        row = tn.add_row().cells
                        row[0].text = k.strip()
                        row[1].text = v.strip()

            p = doc.add_paragraph()
            p.add_run(tr('word_screenshot')).bold = True
            img_path = _render_content_to_image(rec)
            if img_path and os.path.isfile(img_path):
                temp_images.append(img_path)
                try:
                    doc.add_picture(img_path, width=Cm(16))
                except Exception as e:
                    register_error('word', 'Picture insert error / Не удалось вставить картинку', str(e))
                    doc.add_paragraph("(picture insert failed / не удалось вставить изображение)")
            else:
                fallback = doc.add_paragraph()
                fallback.add_run("(image unavailable, text preview below / изображение недоступно, превью ниже)\n").italic = True
                fallback.add_run((rec.content_preview or "")[:1500])

            doc.add_paragraph()

        doc.add_paragraph()
        doc.add_paragraph("_" * 60)
        sign = doc.add_paragraph()
        sign.add_run(tr('word_sign_off', fio=officer_info.get('fio', ''))).italic = True
        doc.add_paragraph(tr('word_date', dt=datetime.now().strftime('%d.%m.%Y')))

        doc.save(str(filepath))
        return True
    except Exception as e:
        register_error('word', 'Word report error / Ошибка формирования Word-отчёта', str(e))
        traceback.print_exc()
        return False
    finally:
        for p in temp_images:
            try:
                if os.path.isfile(p):
                    os.remove(p)
            except Exception:
                pass

# ======================================================================
# FileAuditorPro — main scanner class
# ======================================================================
class FileAuditorPro:
    def __init__(self):
        refresh_library_flags()
        self.results: List[Any] = []
        self.total_files = 0
        self.total_folders = 0
        self.keywords = list(KEYWORDS)
        self.computer_name = get_computer_name()
        try:
            self.disk_info_list = get_detailed_disk_info()
        except Exception as e:
            register_error('disks', 'Disk info error / Не удалось получить информацию о дисках', str(e))
            self.disk_info_list = []
        self.stop_flag = False
        self._drive_info_cache: Dict[str, str] = {}
        self.names_only = bool(SETTINGS.get('names_only_mode', False))

    def _get_drive_full_info(self, path) -> str:
        try:
            p = str(path)
            letter = ''
            m = re.match(r'^([A-Za-z]):', p)
            if m:
                letter = m.group(1).upper()
            elif len(p) >= 2 and p[1] == ':':
                letter = p[0].upper()
            if not letter:
                return ""
            key = f"{letter}:"
            if key in self._drive_info_cache:
                return self._drive_info_cache[key]
            info = get_volume_full_info(p)
            block = format_drive_info_block(info)
            self._drive_info_cache[key] = block
            return block
        except Exception:
            return ""

    def _get_disk_info_for_path(self, path):
        try:
            drive = str(Path(path).drive)
            letter = drive.rstrip('\\')
            for d in self.disk_info_list:
                if letter.upper() in [l.upper().rstrip('\\') for l in d.get('drive_letter', [])]:
                    return (letter,
                            f"{safe_decode(d.get('model', '?'))} ({d.get('size', '?')})",
                            safe_decode(d.get('serial_number', '?')),
                            safe_decode(d.get('model', '?')))
            return (letter, "Unknown / Неизвестно", "Unknown / Неизвестно", "Unknown / Неизвестно")
        except Exception:
            return ("", "Unknown", "Unknown", "Unknown")

    def _check_keywords(self, text):
        if not text:
            return []
        try:
            tl = text.lower()
            return [kw for kw in self.keywords if kw.lower() in tl]
        except Exception:
            return []

    def _extract_any(self, path: Path) -> str:
        ext = path.suffix.lower()
        p_low = path.name.lower()
        if ext in TEXT_EXTS:
            return extract_text_from_txt(str(path))
        if ext in PDF_EXTS:
            return extract_text_from_pdf(str(path))
        if ext in DOCX_EXTS:
            return extract_text_from_docx(str(path))
        if ext in DOC_EXTS:
            return extract_text_from_doc(str(path))
        if ext in XLSX_EXTS:
            return extract_text_from_xlsx(str(path))
        if ext in XLS_EXTS:
            return extract_text_from_xls(str(path))
        if ext in PPTX_EXTS:
            return extract_text_from_pptx(str(path))
        if ext in ODF_EXTS:
            return extract_text_from_odf(str(path))
        if ext in RTF_EXTS:
            return extract_text_from_rtf(str(path))
        if ext in VSDX_EXTS:
            return extract_text_from_vsdx(str(path))
        if ext in IMAGE_EXTS:
            if ext == '.gif':
                return extract_text_from_gif(str(path))
            return extract_text_from_image(str(path))
        if ext in MAIL_EXTS:
            return extract_text_from_eml(str(path))

        if ext in AUTOCAD_EXTS:
            if ext in ('.dxf', '.dwt', '.dws'):
                return _extract_dxf_text(path)
            return _extract_dwg_text(path)
        if ext in KOMPAS_EXTS:
            return _extract_kompas_text(path)
        if ext in GRANDSMETA_EXTS:
            return _extract_grandmeta_text(path)
        if ext in MACROMINE_EXTS:
            return _extract_macromine_text(path)
        if ext in CIVIL_EXTS:
            return _extract_civil_text(path)

        if ext in EXEC_EXTS:
            parts = []
            m = _get_magic_type(path)
            if m:
                parts.append(f"[MIME] {m}")
            pe = _get_pefile_info(path)
            if pe:
                parts.append(f"[PE] {pe}")
            return '\n'.join(parts)

        if ext in FORENSIC_EXTS:
            parts = []
            if HAS_PYTSK3:
                try:
                    mod = _robust_import('pytsk3')
                    img = mod.Img_Info(str(path))
                    parts.append(f"[pytsk3] Image opened / Образ открыт: {img.get_size()} bytes")
                except Exception as e:
                    parts.append(f"[pytsk3] Error / Ошибка: {e}")
            if HAS_DISSECT:
                parts.append("[dissect] dissect available / доступен")
            return '\n'.join(parts)

        if ext in REGISTRY_EXTS:
            parts = []
            if HAS_REGISTRY:
                try:
                    mod = _robust_import('Registry')
                    reg = mod.Registry(str(path))
                    parts.append(f"[registry] Root key / Корневой ключ: {reg.root().name()}")
                except Exception as e:
                    parts.append(f"[registry] Error / Ошибка: {e}")
            if HAS_REGIPY:
                try:
                    _robust_import('regipy')
                    with open(str(path), 'rb') as f:
                        pass
                    parts.append("[regipy] regipy available / доступен")
                except Exception:
                    pass
            return '\n'.join(parts)

        if ext in ARCHIVE_EXTS or p_low.endswith(('.tar.gz', '.tar.bz2', '.tar.xz', '.tar.lzma')):
            return extract_text_from_archive(path)
        return ""

    def _process_file(self, path: Path):
        try:
            name = path.name
            ext = path.suffix.lower()
            sz = path.stat().st_size
            sz_h = get_file_size_human(sz)
            ct, mt, at = get_file_times(str(path))
            owner = get_file_owner_detailed(str(path))

            if self.names_only:
                author, last_saved = "Не указан", "Не указан"
            else:
                author, last_saved = get_document_author_detailed(str(path))

            attrs = get_file_attributes_windows(str(path))
            disk_letter, disk_info_str, disk_serial, disk_model = self._get_disk_info_for_path(str(path))
            drive_full_info = self._get_drive_full_info(str(path))

            matched = self._check_keywords(name)
            content = ""
            preview = ""
            if not self.names_only:
                try:
                    content = self._extract_any(path)
                except Exception as e:
                    register_error('extract', f'Text extraction error / Ошибка извлечения текста {path}', str(e))
                if content:
                    preview = content[:300]
                    for kw in self._check_keywords(content):
                        if kw not in matched:
                            matched.append(kw)
            else:
                preview = "(names-only mode / режим только по именам)"

            creator = ""
            email_from = ""
            email_to = ""

            if ext in MAIL_EXTS and not self.names_only:
                meta = get_eml_meta_for_path(path)
                email_from = meta.get('from', '') or ""
                to_parts = []
                if meta.get('to'):
                    to_parts.append(f"To: {meta['to']}")
                if meta.get('cc'):
                    to_parts.append(f"Cc: {meta['cc']}")
                if meta.get('bcc'):
                    to_parts.append(f"Bcc: {meta['bcc']}")
                email_to = "; ".join(to_parts) if to_parts else ""
                creator = email_from or ""
            else:
                if author and author != "Не указан":
                    creator = author
                elif owner and owner != "Не определен":
                    creator = owner
                else:
                    creator = "Не указан"

            if matched:
                return FileExtendedInfo(
                    path=str(path), filename=name,
                    extension=ext or "(no ext / без расширения)",
                    size=sz, size_human=sz_h,
                    created_time=ct, modified_time=mt, accessed_time=at,
                    file_owner=owner, document_author=author, last_saved_by=last_saved,
                    computer_name=self.computer_name,
                    is_readonly=attrs['readonly'], is_hidden=attrs['hidden'],
                    is_system=attrs['system'], is_archive=attrs['archive'],
                    keywords_matched=', '.join(matched[:10]),
                    content_preview=preview[:300] if preview else "(text not extracted / текст не извлечён)",
                    disk_info=disk_info_str, disk_serial=disk_serial,
                    disk_model=disk_model, disk_letter=disk_letter,
                    creator=creator, email_from=email_from, email_to=email_to,
                    drive_full_info=drive_full_info,
                )
        except Exception as e:
            register_error('process', f'File processing error / Ошибка обработки {path}', str(e))
        return None

    def scan_folder(self, folder: Path, stop_flag_ref=None,
                    pause_flag_ref=None, log_callback=None, progress_callback=None,
                    on_find_callback=None):
        """Scan a folder recursively with checkpoints."""
        global stop_scan
        if stop_flag_ref is None:
            stop_flag_ref = lambda: stop_scan
        if pause_flag_ref is None:
            pause_flag_ref = lambda: False

        def log(msg, level='info'):
            if log_callback:
                log_callback(msg, level)
            else:
                if level == 'success':
                    print_success(msg)
                elif level == 'error':
                    print_error(msg)
                elif level == 'warning':
                    print_warning(msg)
                elif level == 'header':
                    print_header(msg)
                else:
                    print_info(msg)

        if progress_callback:
            try:
                progress_callback(-1, -1)
            except Exception:
                pass

        log(f"SCANNING / СКАНИРОВАНИЕ: {folder}", 'header')
        try:
            next(os.scandir(str(folder)), None)
            log("Folder access granted / Доступ к папке получен", 'success')
        except Exception as e:
            log(f"No access / Нет доступа: {e}", 'error')
            register_error('scan', f'No access / Нет доступа к {folder}', str(e))
            if progress_callback:
                try:
                    progress_callback(0, 0)
                except Exception:
                    pass
            return 0

        files = []
        folders = 0
        skip = {'System Volume Information', '$Recycle.Bin', 'Windows',
                'Program Files', 'Program Files (x86)'}
        log("Collecting files / Сбор файлов...", 'info')
        try:
            for root, dirs, filenames in os.walk(str(folder)):
                if stop_flag_ref():
                    log("Scan interrupted by user / Сканирование прервано пользователем", 'warning')
                    break
                dirs[:] = [d for d in dirs if d not in skip and not d.startswith('.')]
                folders += 1
                for f in filenames:
                    files.append(Path(root) / f)
        except PermissionError as e:
            log("No access to some folders / Нет доступа к некоторым папкам", 'warning')
            register_error('scan', 'No access to some folders / Нет доступа к некоторым папкам', str(e))
        except Exception as e:
            log(f"Walk error / Ошибка обхода: {e}", 'error')
            register_error('scan', f'Walk error / Ошибка обхода {folder}', str(e))
            return 0

        if stop_flag_ref():
            log("Stop requested before processing / Остановка запрошена до обработки", 'warning')
            if progress_callback:
                try:
                    progress_callback(0, 0)
                except Exception:
                    pass
            return 0

        total = len(files)
        self.total_files = total
        self.total_folders = folders
        if total == 0:
            log("No files found / Файлы не найдены", 'warning')
            if progress_callback:
                try:
                    progress_callback(0, 0)
                except Exception:
                    pass
            return 0

        checkpoint_loaded = False
        processed_set: set = set()
        started_at = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        ck = _load_checkpoint([folder])
        if ck is not None:
            processed_set, prev_results, prev_total, prev_started = ck
            if prev_total == total and processed_set:
                self.results = list(prev_results)
                started_at = prev_started or started_at
                checkpoint_loaded = True
                log(f"[CHECKPOINT] Found save: processed {len(processed_set)} of {total}. Continuing... "
                    f"[ЧЕКПОИНТ] Найдено сохранение: обработано {len(processed_set)} из {total}. Продолжаем...", 'success')

        log(f"Found / Найдено: {total:,} files in {folders:,} folders / файлов в папках", 'success')
        log(f"OCR: {'AVAILABLE / ДОСТУПЕН' if HAS_OCR else 'NOT AVAILABLE / НЕ ДОСТУПЕН'}", 'info')
        if self.names_only:
            log("Mode: NAMES ONLY / Режим: ТОЛЬКО ИМЕНА", 'warning')

        if progress_callback:
            try:
                progress_callback(len(processed_set) if checkpoint_loaded else 0, total)
            except Exception:
                pass

        found = len(self.results) if checkpoint_loaded else 0
        start = time.monotonic()
        pb = ColoredProgressBar(total, "Scanning / Сканирование", 50, Fore.GREEN)
        if checkpoint_loaded:
            pb.current = len(processed_set)

        last_report = [0.0]
        last_checkpoint = [time.monotonic()]
        processed_since_checkpoint = [0]

        def report_progress(cur, tot):
            if not progress_callback:
                return
            now = time.monotonic()
            if (now - last_report[0]) >= 0.2 or cur >= tot:
                last_report[0] = now
                try:
                    progress_callback(cur, tot)
                except Exception:
                    pass

        def maybe_save_checkpoint(force=False):
            now = time.monotonic()
            if not force:
                if processed_since_checkpoint[0] < 100 and (now - last_checkpoint[0]) < 5.0:
                    return
            last_checkpoint[0] = now
            processed_since_checkpoint[0] = 0
            with CHECKPOINT_LOCK:
                _save_checkpoint([folder], processed_set, self.results, total, started_at)

        pool = None
        try:
            pool = ThreadPoolExecutor(max_workers=4)
            future_to_path = {}
            for f in files:
                if stop_flag_ref():
                    break
                key = str(f).lower()
                if key in processed_set:
                    continue
                fut = pool.submit(self._process_file, f)
                future_to_path[fut] = f

            done = len(processed_set)
            for fut in as_completed(future_to_path):
                while pause_flag_ref() and not stop_flag_ref():
                    time.sleep(0.2)
                if stop_flag_ref():
                    try:
                        for f2 in list(future_to_path.keys()):
                            f2.cancel()
                    except Exception:
                        pass
                    log("Scan interrupted. Saving checkpoint... / Сканирование прервано. Сохраняем чекпоинт...", 'warning')
                    maybe_save_checkpoint(force=True)
                    break

                fpath = future_to_path[fut]
                done += 1
                processed_since_checkpoint[0] += 1
                pb.update()
                report_progress(min(done, total), total)

                try:
                    r = fut.result()
                except Exception as e:
                    register_error('scan-future', 'File thread error / Ошибка в потоке обработки файла', str(e))
                    r = None

                if r:
                    self.results.append(r)
                    found += 1
                    if log_callback:
                        log_callback(f"[FILE / ФАЙЛ] {safe_decode(r.filename)} | "
                                     f"Keywords / Ключевые слова: {safe_decode(r.keywords_matched)}", 'found')
                    if on_find_callback:
                        try:
                            on_find_callback(r)
                        except Exception:
                            pass

                try:
                    processed_set.add(str(fpath).lower())
                except Exception:
                    pass

                maybe_save_checkpoint()
        except Exception as e:
            register_error('scan-pool', 'Pool processing error / Ошибка в пуле обработки', str(e))
            maybe_save_checkpoint(force=True)
        finally:
            if pool is not None:
                try:
                    pool.shutdown(wait=False, cancel_futures=True)
                except TypeError:
                    try:
                        pool.shutdown(wait=False)
                    except Exception:
                        pass
                except Exception:
                    pass

        elapsed = time.monotonic() - start
        pb.finish()
        log(f"Time / Время: {elapsed:.1f} s", 'success')
        log(f"Checked files / Проверено файлов: {total:,} / processed: {len(self.results)}", 'success')
        log(f"Matches found / Найдено совпадений: {found}", 'success')
        if progress_callback:
            try:
                progress_callback(total, total)
            except Exception:
                pass

        if not stop_flag_ref():
            _clear_checkpoint()
        else:
            maybe_save_checkpoint(force=True)

        return found

    def save_report_txt(self, filepath, scan_targets=None, scan_duration=""):
        try:
            filepath = Path(filepath)
            if not self.results:
                return False

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"{PROGRAM_NAME:^80}\n")
                f.write("=" * 80 + "\n")
                f.write(f" Version / Версия: {VERSION}\n")
                f.write(f" Author / Автор: {AUTHOR}\n")
                f.write(f" License / Лицензия: {LICENSE}\n")
                f.write(f" GitHub: {GITHUB}\n")
                f.write(f" Date / Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write(f" Scanning computer / Компьютер сканирующий: {safe_decode(self.computer_name)}\n")
                f.write(f" Matches found / Найдено совпадений: {len(self.results)}\n")
                if self.names_only:
                    f.write(" Scan mode / Режим сканирования: NAMES ONLY / ТОЛЬКО ИМЕНА\n")
                if scan_duration:
                    f.write(f" Scan duration / Время сканирования: {scan_duration}\n")
                f.write("=" * 80 + "\n\n")
                f.write("#" * 80 + "\n")
                f.write("#  DISKS AND MEDIA INFO / ИНФОРМАЦИЯ О ДИСКАХ И НОСИТЕЛЯХ\n")
                f.write("#" * 80 + "\n")
                for i, d in enumerate(self.disk_info_list, 1):
                    f.write(f"\n [{i}] PHYSICAL DISK / ФИЗИЧЕСКИЙ ДИСК\n")
                    f.write(f"    Drive letters / Буквы дисков : {', '.join(d.get('drive_letter', []))}\n")
                    f.write(f"    Model / Модель       : {safe_decode(d.get('model', 'Unknown'))}\n")
                    f.write(f"    Manufacturer / Производитель: {safe_decode(d.get('manufacturer', 'Unknown'))}\n")
                    f.write(f"    Serial / Серийный номер: {safe_decode(d.get('serial_number', 'Unknown'))}\n")
                    f.write(f"    Interface / Интерфейс    : {safe_decode(d.get('interface_type', 'Unknown'))}\n")
                    f.write(f"    Size / Размер       : {d.get('size', 'Unknown')}\n")
                    f.write(f"    Partitions / Разделов     : {d.get('partitions', 0)}\n")
                    if d.get('firmware'):
                        f.write(f"    Firmware / Прошивка     : {safe_decode(d['firmware'])}\n")
                if scan_targets:
                    f.write("\n" + "#" * 80 + "\n")
                    f.write("#  SCANNED MEDIA CHARACTERISTICS / ХАРАКТЕРИСТИКИ ПРОСКАНИРОВАННЫХ НОСИТЕЛЕЙ\n")
                    f.write("#" * 80 + "\n")
                    for tgt in scan_targets:
                        info = get_volume_full_info(tgt)
                        block = format_drive_info_block(info)
                        if block:
                            f.write(f"\n  Media / Носитель: {tgt}\n")
                            for line in block.splitlines():
                                f.write(f"    {line}\n")
                f.write("\n")

                f.write("#" * 80 + "\n")
                f.write("#  AGGREGATED CONCLUSIONS / ОБОБЩЁННЫЕ ВЫВОДЫ\n")
                f.write("#" * 80 + "\n")
                try:
                    fs = collect_forensic_summary(self.results)
                    f.write("\n  File categories / Категории файлов:\n")
                    for cat, cnt in sorted(fs['by_category'].items(), key=lambda x: -x[1]):
                        f.write(f"    {cat:<60} {cnt:>8}\n")
                    f.write("\n  Top-15 extensions / Топ-15 расширений:\n")
                    for ext, cnt in fs['by_extension'].items():
                        f.write(f"    {str(ext):<60} {cnt:>8}\n")
                    if fs['by_keyword']:
                        f.write("\n  Top keywords / Топ ключевых слов:\n")
                        for kw, cnt in fs['by_keyword'].items():
                            f.write(f"    {str(kw):<60} {cnt:>8}\n")
                    if fs['by_owner']:
                        f.write("\n  Top owners / Топ владельцев:\n")
                        for ow, cnt in fs['by_owner'].items():
                            f.write(f"    {str(ow):<60} {cnt:>8}\n")
                    if fs['by_author']:
                        f.write("\n  Top document authors / Топ авторов документов:\n")
                        for au, cnt in fs['by_author'].items():
                            f.write(f"    {str(au):<60} {cnt:>8}\n")
                    f.write("\n  Forensic metrics / Форензик-метрики:\n")
                    for k, v in [
                        ("Images with EXIF / Изображений с EXIF", fs['exif_summary']['with_exif']),
                        ("Images with GPS / Изображений с GPS", fs['exif_summary']['with_gps']),
                        ("Steganography candidates / Кандидатов на стеганографию", fs['stegano_candidates']),
                        ("PDF with dangerous objects / PDF с опасными объектами", fs['pdf_suspicious']),
                        ("Registry/log files / Файлов реестра/журналов", fs['registry_hits']),
                        ("Mail files (EML/MSG) / Файлов почты", fs.get('mail_hits', 0)),
                        ("Files on USB / Файлов на USB", fs['usb_hits']),
                        ("Forensic images / Форензик-образов", fs['forensic_hits']),
                        ("Executables / Исполняемых файлов", fs['exec_hits']),
                        ("CAD/Estimating files / CAD/Сметных файлов", fs.get('cad_hits', 0)),
                    ]:
                        f.write(f"    {k:<60} {v:>8}\n")
                except Exception as e:
                    f.write(f"    [summary unavailable / обобщение недоступно: {e}]\n")
                f.write("\n")

                f.write("#" * 80 + "\n")
                f.write("#  FOUND FILES / НАЙДЕННЫЕ ФАЙЛЫ\n")
                f.write("#" * 80 + "\n\n")
                for idx, r in enumerate(self.results, 1):
                    f.write("-" * 80 + "\n")
                    f.write(f"[{idx}] {safe_decode(r.filename)}\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"  Path / Путь:          {safe_decode(r.path)}\n")
                    try:
                        f.write(f"  Open / Открыть:       {_file_url(r.path)}\n")
                    except Exception:
                        pass
                    f.write(f"  Extension / Расширение:    {safe_decode(r.extension)}\n")
                    f.write(f"  Size / Размер:        {r.size:,} bytes / байт ({r.size_human})\n")
                    f.write(f"\n  [DATE AND TIME / ДАТА И ВРЕМЯ]\n")
                    f.write(f"    Created / Создан:      {r.created_time}\n")
                    f.write(f"    Modified / Изменён:     {r.modified_time}\n")
                    f.write(f"    Accessed / Открыт:      {r.accessed_time}\n")
                    f.write(f"\n  [CREATOR AND OWNER / СОЗДАТЕЛЬ И ВЛАДЕЛЕЦ]\n")
                    f.write(f"    File creator / Создатель файла: {safe_decode(getattr(r, 'creator', '') or 'Not specified / Не указан')}\n")
                    f.write(f"    File owner / Владелец файла:  {safe_decode(r.file_owner)}\n")
                    f.write(f"    Document author / Автор документа: {safe_decode(r.document_author)}\n")
                    f.write(f"    Last saved by / Кем изменён:     {safe_decode(r.last_saved_by)}\n")
                    f.write(f"    Scanning computer / Компьютер сканирующий: {safe_decode(r.computer_name)}\n")
                    ext_low = (r.extension or '').lower()
                    if ext_low in MAIL_EXTS:
                        f.write(f"\n  [MAIL MESSAGE / ПОЧТОВОЕ СООБЩЕНИЕ]\n")
                        em_from = safe_decode(getattr(r, 'email_from', '') or '')
                        em_to = safe_decode(getattr(r, 'email_to', '') or '')
                        f.write(f"    Sent by / Кто отправил:     {em_from or 'Not specified / Не указано'}\n")
                        f.write(f"    Recipient / Кому отправлено:  {em_to or 'Not specified / Не указано'}\n")
                    f.write(f"\n  [FILE ATTRIBUTES / АТРИБУТЫ ФАЙЛА]\n")
                    f.write(f"    Read-only / Только чтение: {'Yes / Да' if r.is_readonly else 'No / Нет'}\n")
                    f.write(f"    Hidden / Скрытый:       {'Yes / Да' if r.is_hidden else 'No / Нет'}\n")
                    f.write(f"    System / Системный:     {'Yes / Да' if r.is_system else 'No / Нет'}\n")
                    f.write(f"    Archive / Архивный:      {'Yes / Да' if r.is_archive else 'No / Нет'}\n")
                    f.write(f"\n  [MEDIA INFO / ИНФОРМАЦИЯ О НОСИТЕЛЕ]\n")
                    if r.disk_letter:
                        f.write(f"    Disk letter / Буква диска:     {r.disk_letter}\n")
                    f.write(f"    Disk model / Модель диска:    {safe_decode(r.disk_model)}\n")
                    f.write(f"    Serial / Серийный номер:  {safe_decode(r.disk_serial)}\n")
                    if r.drive_full_info:
                        f.write(f"    --- Media characteristics / Характеристики носителя ---\n")
                        for line in r.drive_full_info.splitlines():
                            f.write(f"    {line}\n")
                    f.write(f"\n  [KEYWORDS / КЛЮЧЕВЫЕ СЛОВА]\n")
                    f.write(f"    {safe_decode(r.keywords_matched)}\n")
                    f.write(f"\n  [CONTENT PREVIEW / ПРЕДПРОСМОТР СОДЕРЖИМОГО]\n")
                    preview = safe_decode(r.content_preview).replace('\n', ' ')
                    for line in [preview[i:i + 76] for i in range(0, len(preview), 76)]:
                        f.write(f"    {line}\n")
                    f.write("\n")
            return True
        except Exception as e:
            register_error('report', 'TXT save error / Ошибка сохранения TXT-отчёта', str(e))
            print_error(f"Save error / Ошибка сохранения: {e}")
            return False

# ======================================================================
# GUI
# ======================================================================
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# ----------------------------------------------------------------------
# Sound: "pig squeal"
# ----------------------------------------------------------------------
def play_find_sound():
    if not SETTINGS.get('sound_on_find', True):
        return
    try:
        if sys.platform == 'win32':
            import winsound
            squeal = [
                (1200, 60), (1600, 55), (2000, 50), (2400, 45),
                (2800, 40), (3200, 35), (2800, 35), (2400, 40),
                (2000, 45), (1600, 55), (1200, 70), (1600, 55),
                (2000, 45), (2400, 40), (2800, 35), (3200, 30),
            ]
            try:
                for freq, dur in squeal:
                    winsound.Beep(int(freq), int(dur))
            except Exception:
                try:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    pass
        else:
            sys.stdout.write('\a')
            sys.stdout.flush()
    except Exception:
        try:
            sys.stdout.write('\a')
            sys.stdout.flush()
        except Exception:
            pass

# ----------------------------------------------------------------------
# Copy helpers
# ----------------------------------------------------------------------
def _copy_selection(widget):
    try:
        if isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
            try:
                sel = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                return "break"
            widget.clipboard_clear()
            widget.clipboard_append(sel)
        elif isinstance(widget, ttk.Treeview):
            sel = widget.selection()
            if not sel:
                return "break"
            lines = []
            for iid in sel:
                vals = widget.item(iid, 'values')
                lines.append('\t'.join(str(v) for v in vals))
            widget.clipboard_clear()
            widget.clipboard_append('\n'.join(lines))
        elif isinstance(widget, tk.Entry):
            try:
                sel = widget.selection_get()
            except tk.TclError:
                return "break"
            widget.clipboard_clear()
            widget.clipboard_append(sel)
    except Exception:
        pass
    return "break"

def _select_all(widget):
    try:
        if isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
            widget.tag_add(tk.SEL, "1.0", tk.END)
            widget.mark_set(tk.INSERT, "1.0")
            widget.see(tk.INSERT)
            return "break"
        elif isinstance(widget, ttk.Treeview):
            widget.selection_set(widget.get_children())
            return "break"
        elif isinstance(widget, tk.Entry):
            widget.select_range(0, tk.END)
            return "break"
    except Exception:
        pass
    return "break"

def _copy_all(widget):
    try:
        if isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
            content = widget.get("1.0", tk.END)
            widget.clipboard_clear()
            widget.clipboard_append(content)
        elif isinstance(widget, ttk.Treeview):
            lines = []
            for iid in widget.get_children():
                vals = widget.item(iid, 'values')
                lines.append('\t'.join(str(v) for v in vals))
            widget.clipboard_clear()
            widget.clipboard_append('\n'.join(lines))
    except Exception:
        pass

def add_copy_context_menu(widget, root=None):
    try:
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Copy / Копировать", accelerator="Ctrl+C",
                         command=lambda: _copy_selection(widget))
        menu.add_command(label="Select all / Выделить всё", accelerator="Ctrl+A",
                         command=lambda: _select_all(widget))
        menu.add_separator()
        menu.add_command(label="Copy all / Копировать всё", command=lambda: _copy_all(widget))

        def _show_menu(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                try:
                    menu.grab_release()
                except Exception:
                    pass
            return "break"

        widget.bind("<Button-3>", _show_menu)
        widget.bind("<Button-2>", _show_menu)
        widget.bind("<Control-c>", lambda e: _copy_selection(widget))
        widget.bind("<Control-C>", lambda e: _copy_selection(widget))
        widget.bind("<Control-a>", lambda e: _select_all(widget))
        widget.bind("<Control-A>", lambda e: _select_all(widget))
    except Exception:
        pass

# ----------------------------------------------------------------------
# Sortable Treeview
# ----------------------------------------------------------------------
def _make_sortable(treeview, numeric_cols=None):
    if numeric_cols is None:
        numeric_cols = set()
    _sort_state = {}

    def _sort_by(col):
        try:
            reverse = _sort_state.get(col, False)
            items = [(treeview.set(k, col), k) for k in treeview.get_children('')]

            def _key(pair):
                val = pair[0]
                if col in numeric_cols:
                    try:
                        cleaned = str(val).replace(' ', '').replace(',', '.')
                        m = re.match(r'^(-?\d+(?:\.\d+)?)', cleaned)
                        if m:
                            return float(m.group(1))
                        return 0.0
                    except Exception:
                        return 0.0
                return str(val).lower()

            try:
                items.sort(key=_key, reverse=reverse)
            except Exception:
                items.sort(key=lambda x: str(x[0]).lower(), reverse=reverse)

            for index, (_, k) in enumerate(items):
                treeview.move(k, '', index)

            _sort_state[col] = not reverse
        except Exception:
            pass

    try:
        for col in treeview['columns']:
            treeview.heading(
                col,
                text=treeview.heading(col)['text'],
                command=lambda c=col: _sort_by(c)
            )
    except Exception:
        pass

# ----------------------------------------------------------------------
# Officer info dialog
# ----------------------------------------------------------------------
class OfficerInfoDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(tr('dlg_officer_title'))
        self.geometry("640x360")
        self.minsize(480, 320)
        self.transient(parent)
        try:
            self.grab_set()
        except Exception:
            pass
        self.resizable(True, True)
        self.result: Optional[Dict[str, str]] = None

        tk.Label(self, text=tr('dlg_officer_header'),
                 font=("Arial", 11, "bold"), bg="#1a237e", fg="white").pack(fill=tk.X)

        body = tk.Frame(self, bg="#f5f5f5")
        body.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.vars = {}
        for key, label, default in [
            ("fio", tr('dlg_officer_fio'), ""),
            ("position", tr('dlg_officer_position'), tr('dlg_officer_position_default')),
            ("department", tr('dlg_officer_department'), ""),
            ("contact", tr('dlg_officer_contact'), ""),
        ]:
            row = tk.Frame(body, bg="#f5f5f5")
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=label, width=22, anchor='w', bg="#f5f5f5").pack(side=tk.LEFT)
            var = tk.StringVar(value=default)
            self.vars[key] = var
            e = tk.Entry(row, textvariable=var)
            e.pack(side=tk.LEFT, fill=tk.X, expand=True)
            e.bind("<Control-a>", lambda ev, w=e: _select_all(w))
            e.bind("<Control-A>", lambda ev, w=e: _select_all(w))
            e.bind("<Control-c>", lambda ev, w=e: _copy_selection(w))
            e.bind("<Control-C>", lambda ev, w=e: _copy_selection(w))

        btn = tk.Frame(self, bg="#f5f5f5")
        btn.pack(fill=tk.X, pady=8)
        tk.Button(btn, text=tr('dlg_officer_ok'), width=22, bg="#2e7d32", fg="white",
                  font=("Arial", 10, "bold"), command=self._on_ok).pack(side=tk.LEFT, padx=15)
        tk.Button(btn, text=tr('dlg_officer_cancel'), width=12, bg="#c62828", fg="white",
                  font=("Arial", 10, "bold"), command=self._on_cancel).pack(side=tk.RIGHT, padx=15)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_ok(self):
        self.result = {k: v.get().strip() for k, v in self.vars.items()}
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

    def _on_cancel(self):
        self.result = None
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

# ----------------------------------------------------------------------
# Drive select dialog
# ----------------------------------------------------------------------
class DriveSelectDialog(tk.Toplevel):
    def __init__(self, parent, drives: List[Dict[str, Any]],
                 title: str = None,
                 preselect_usb_only: bool = False,
                 preselect_all: bool = False):
        super().__init__(parent)
        if title is None:
            title = tr('dlg_drives_title')
        self.title(title)
        self.geometry("1100x620")
        self.minsize(800, 420)
        self.transient(parent)
        try:
            self.grab_set()
        except Exception:
            pass
        self.resizable(True, True)

        self.result: Optional[List[str]] = None
        self.drives = drives
        self._vars: Dict[str, tk.BooleanVar] = {}

        tk.Label(self, text=title, font=("Arial", 12, "bold"),
                 bg="#1a237e", fg="white").pack(fill=tk.X)

        tk.Label(self, text=tr('dlg_drives_hint'),
                 font=("Arial", 10), anchor='w').pack(fill=tk.X, padx=10, pady=(8, 4))

        quick = tk.Frame(self)
        quick.pack(fill=tk.X, padx=10, pady=2)
        tk.Button(quick, text=tr('dlg_drives_select_all'), width=18,
                  command=lambda: self._set_all(True)).pack(side=tk.LEFT, padx=2)
        tk.Button(quick, text=tr('dlg_drives_deselect_all'), width=18,
                  command=lambda: self._set_all(False)).pack(side=tk.LEFT, padx=2)
        tk.Button(quick, text=tr('dlg_drives_internal'), width=22,
                  command=self._select_internal).pack(side=tk.LEFT, padx=2)
        tk.Button(quick, text=tr('dlg_drives_usb'), width=14,
                  command=self._select_usb).pack(side=tk.LEFT, padx=2)

        header = tk.Frame(self, bg="#e8eaf6")
        header.pack(fill=tk.X, padx=10, pady=(8, 0))
        for text, w in [("✓", 3), (tr('dlg_drives_col_disk'), 8), (tr('dlg_drives_col_type'), 16),
                        (tr('dlg_drives_col_label'), 20), (tr('dlg_drives_col_fs'), 8),
                        (tr('dlg_drives_col_total'), 10), (tr('dlg_drives_col_free'), 10),
                        (tr('dlg_drives_col_usb'), 6), (tr('dlg_drives_col_serial'), 14),
                        (tr('dlg_drives_col_model'), 30)]:
            tk.Label(header, text=text, width=w, anchor='w',
                     font=("Arial", 9, "bold"), bg="#e8eaf6").pack(side=tk.LEFT)

        canvas = tk.Canvas(self, bg="white", highlightthickness=1,
                           highlightbackground="#c5cae9")
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        scroll_frame = tk.Frame(canvas, bg="white")
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        vsb.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=(5, 20))
        hsb.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 5))

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        try:
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        except Exception:
            pass

        for d in drives:
            row = tk.Frame(scroll_frame, bg="white")
            row.pack(fill=tk.X, pady=1)

            var = tk.BooleanVar(value=False)
            self._vars[d['root']] = var

            tk.Checkbutton(row, variable=var, bg="white",
                           width=2).pack(side=tk.LEFT)
            tk.Label(row, text=f"{d['letter']}:", width=4, anchor='w',
                     font=("Consolas", 10, "bold"), bg="white").pack(side=tk.LEFT)

            type_str = d['type_name']
            if d['is_usb']:
                type_str += " [USB]"
            tk.Label(row, text=type_str, width=16, anchor='w',
                     font=("Arial", 9), bg="white").pack(side=tk.LEFT)
            tk.Label(row, text=d['label'] or "—", width=20, anchor='w',
                     font=("Arial", 9), bg="white").pack(side=tk.LEFT)
            tk.Label(row, text=d['fs'] or "—", width=8, anchor='w',
                     font=("Arial", 9), bg="white").pack(side=tk.LEFT)
            tk.Label(row, text=d['total_human'], width=10, anchor='e',
                     font=("Arial", 9), bg="white").pack(side=tk.LEFT)
            tk.Label(row, text=d['free_human'], width=10, anchor='e',
                     font=("Arial", 9), bg="white").pack(side=tk.LEFT)
            tk.Label(row, text="yes/да" if d['is_usb'] else "—", width=6, anchor='w',
                     font=("Arial", 9, "bold"),
                     fg="#2e7d32" if d['is_usb'] else "#888888",
                     bg="white").pack(side=tk.LEFT)
            tk.Label(row, text=d.get('serial', '') or "—", width=14, anchor='w',
                     font=("Consolas", 8), bg="white").pack(side=tk.LEFT)
            tk.Label(row, text=d['model'][:40] or "—", width=30, anchor='w',
                     font=("Arial", 9), bg="white").pack(side=tk.LEFT)

        if preselect_all:
            for v in self._vars.values():
                v.set(True)
        elif preselect_usb_only:
            for d in self.drives:
                if d['is_usb']:
                    self._vars[d['root']].set(True)

        btns = tk.Frame(self)
        btns.pack(fill=tk.X, pady=8)
        tk.Button(btns, text=tr('dlg_drives_scan'), width=22,
                  bg="#2e7d32", fg="white", font=("Arial", 10, "bold"),
                  command=self._on_ok).pack(side=tk.LEFT, padx=10)
        tk.Button(btns, text=tr('dlg_drives_cancel'), width=14,
                  bg="#c62828", fg="white", font=("Arial", 10, "bold"),
                  command=self._on_cancel).pack(side=tk.RIGHT, padx=10)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind('<Return>', lambda e: self._on_ok())
        self.bind('<Escape>', lambda e: self._on_cancel())

        self.update_idletasks()
        try:
            w = self.winfo_width()
            h = self.winfo_height()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x = (sw - w) // 2
            y = (sh - h) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _set_all(self, value: bool):
        for v in self._vars.values():
            v.set(value)

    def _select_internal(self):
        for d in self.drives:
            self._vars[d['root']].set(bool(d['is_fixed'] and not d['is_usb']))

    def _select_usb(self):
        for d in self.drives:
            self._vars[d['root']].set(bool(d['is_usb']))

    def _on_ok(self):
        sel = [root for root, v in self._vars.items() if v.get()]
        if not sel:
            messagebox.showwarning("Selection / Выбор", tr('dlg_drives_warn'))
            return
        self.result = sel
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

    def _on_cancel(self):
        self.result = None
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

# ----------------------------------------------------------------------
# Main GUI window
# ----------------------------------------------------------------------
class FileAuditorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{PROGRAM_NAME} v{VERSION}")
        self.root.geometry("1300x800")
        self.root.minsize(900, 600)
        self.root.resizable(True, True)

        self.auditor: Optional[FileAuditorPro] = None
        self.scan_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.log_queue = queue.Queue()
        self.lib_queue = queue.Queue()
        self.lib_install_thread: Optional[threading.Thread] = None
        self.libs_ready = threading.Event()

        self.disk_info_list = []
        self._splash = None
        self._scan_targets: List[str] = []

        self.audit_started_str = ""
        self.audit_finished_str = ""
        self.scan_duration_str = ""

        # Timer state
        self._scan_start_monotonic = 0.0
        self._elapsed_timer_id = None
        self._last_log_elapsed = 0
        self._scan_running = False

        # Counter state
        self._current_scanned = 0
        self._current_total = 0
        self._current_found = 0

        self._show_startup_splash()
        self._build_ui()
        self._poll_log_queue()
        self._poll_lib_queue()
        self._start_background_library_install()

    # ------------------------------------------------------------------
    # Splash
    # ------------------------------------------------------------------
    def _show_startup_splash(self):
        splash = tk.Toplevel(self.root)
        splash.title("About / О программе")
        splash.geometry("680x480")
        splash.minsize(520, 420)
        splash.resizable(True, True)
        splash.transient(self.root)
        try:
            splash.grab_set()
        except Exception:
            pass

        top = tk.Frame(splash, bg="#1a237e", height=80)
        top.pack(fill=tk.X)
        top.pack_propagate(False)
        tk.Label(top, text=PROGRAM_NAME, font=("Arial", 20, "bold"),
                 fg="white", bg="#1a237e").pack(pady=20)

        info = tk.Frame(splash, bg="#f5f5f5")
        info.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        rows = [
            (tr('dlg_splash_author'), AUTHOR),
            (tr('dlg_splash_github'), GITHUB),
            (tr('dlg_splash_license'), LICENSE),
            (tr('dlg_splash_program'), PROGRAM_NAME),
            (tr('dlg_splash_version'), VERSION),
        ]
        for label, value in rows:
            row = tk.Frame(info, bg="#f5f5f5")
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=label, font=("Arial", 10, "bold"),
                     bg="#f5f5f5", width=12, anchor='w').pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Arial", 10),
                     bg="#f5f5f5", anchor='w', justify=tk.LEFT,
                     wraplength=460).pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_frame = tk.Frame(splash, bg="#f5f5f5")
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="OK", width=14, bg="#3949ab", fg="white",
                  font=("Arial", 11, "bold"),
                  command=lambda: self._close_splash(splash)).pack(pady=5)

        splash.bind('<Return>', lambda e: self._close_splash(splash))
        splash.bind('<Escape>', lambda e: self._close_splash(splash))
        splash.protocol("WM_DELETE_WINDOW", lambda: self._close_splash(splash))

        splash.update_idletasks()
        try:
            w = splash.winfo_width()
            h = splash.winfo_height()
            sw = splash.winfo_screenwidth()
            sh = splash.winfo_screenheight()
            x = (sw - w) // 2
            y = (sh - h) // 2
            splash.geometry(f"+{x}+{y}")
        except Exception:
            pass

        self._splash = splash

    def _close_splash(self, splash):
        try:
            splash.grab_release()
        except Exception:
            pass
        try:
            splash.destroy()
        except Exception:
            pass
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        header_frame = tk.Frame(self.root, bg="#1a237e", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text=f"{PROGRAM_NAME} v{VERSION}",
                 font=("Arial", 16, "bold"), fg="white", bg="#1a237e").pack(pady=15)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tab_info = tk.Frame(self.notebook, bg="#f5f5f5")
        self.notebook.add(self.tab_info, text=tr('tab_info'))
        self._build_info_tab(self.tab_info)

        self.tab_scan = tk.Frame(self.notebook, bg="#f5f5f5")
        self.notebook.add(self.tab_scan, text=tr('tab_scan'))
        self._build_scan_tab(self.tab_scan)

        self.tab_libs = tk.Frame(self.notebook, bg="#f5f5f5")
        self.notebook.add(self.tab_libs, text=tr('tab_libs'))
        self._build_libs_tab(self.tab_libs)

        self.status_bar = tk.Label(self.root, text=tr('status_ready'), bd=1, relief=tk.SUNKEN,
                                    anchor=tk.W, bg="#1a237e", fg="white")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=tr('menu_select_folder'), command=self.select_folder)
        file_menu.add_command(label=tr('menu_select_drives'), command=self.select_drives_dialog)
        file_menu.add_separator()
        file_menu.add_command(label=tr('menu_export_txt'), command=lambda: self.export('txt'))
        file_menu.add_command(label=tr('menu_export_word'), command=self.export_word)
        file_menu.add_separator()
        file_menu.add_command(label=tr('menu_exit'), command=self.root.quit)
        menubar.add_cascade(label=tr('menu_file'), menu=file_menu)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label=tr('menu_show_keywords'), command=self.show_keywords)
        tools_menu.add_command(label=tr('menu_edit_keywords'), command=self.edit_keywords)
        tools_menu.add_command(label=tr('menu_reload_keywords'), command=self.reload_keywords)
        tools_menu.add_separator()
        tools_menu.add_command(label=tr('menu_reinstall_libs'), command=self.reinstall_libraries)
        tools_menu.add_command(label=tr('menu_errors'), command=self.show_errors)
        tools_menu.add_separator()
        tools_menu.add_command(label=tr('menu_reset_checkpoint'), command=self.reset_checkpoint_dialog)
        tools_menu.add_command(label=tr('menu_checkpoint_info'), command=self.show_checkpoint_info)
        menubar.add_cascade(label=tr('menu_tools'), menu=tools_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=tr('menu_about'), command=self.show_about)
        menubar.add_cascade(label=tr('menu_help'), menu=help_menu)
        self.root.config(menu=menubar)

    # ------------------------------------------------------------------
    # Toggle handlers
    # ------------------------------------------------------------------
    def _update_sound_button(self):
        try:
            if SETTINGS.get('sound_on_find', True):
                self.sound_btn.config(text=tr('btn_sound_on'), bg="#2e7d32")
            else:
                self.sound_btn.config(text=tr('btn_sound_off'), bg="#9e9e9e")
        except Exception:
            pass

    def _update_names_button(self):
        try:
            if SETTINGS.get('names_only_mode', False):
                self.names_btn.config(text=tr('btn_names_on'), bg="#c62828")
            else:
                self.names_btn.config(text=tr('btn_names_off'), bg="#2e7d32")
        except Exception:
            pass

    def _update_lang_button(self):
        try:
            lang = SETTINGS.get('ui_language', 'ru')
            if lang == 'ru':
                self.lang_btn.config(text="🌐 Язык: RU", bg="#3949ab")
            else:
                self.lang_btn.config(text="🌐 Lang: EN", bg="#3949ab")
        except Exception:
            pass

    def _toggle_sound(self):
        SETTINGS['sound_on_find'] = not SETTINGS.get('sound_on_find', True)
        save_settings(SETTINGS)
        self._update_sound_button()

    def _toggle_names_only(self):
        SETTINGS['names_only_mode'] = not SETTINGS.get('names_only_mode', False)
        save_settings(SETTINGS)
        self._update_names_button()
        lang = SETTINGS.get('ui_language', 'ru')
        if SETTINGS['names_only_mode']:
            msg = ("Names-only mode: ON / Режим «только имена»: ВКЛ"
                   if lang == 'en' else "Режим «только имена»: ВКЛ")
            self.log(msg, 'warning')
        else:
            msg = ("Names-only mode: OFF / Режим «только имена»: ВЫКЛ"
                   if lang == 'en' else "Режим «только имена»: ВЫКЛ")
            self.log(msg, 'info')

    def _toggle_lang(self):
        cur = SETTINGS.get('ui_language', 'ru')
        SETTINGS['ui_language'] = 'en' if cur == 'ru' else 'ru'
        save_settings(SETTINGS)
        self._update_lang_button()
        self._apply_language()

    def _apply_language(self):
        try:
            self.notebook.tab(self.tab_info, text=tr('tab_info'))
            self.notebook.tab(self.tab_scan, text=tr('tab_scan'))
            self.notebook.tab(self.tab_libs, text=tr('tab_libs'))

            self.status_bar.config(text=tr('status_ready'))

            self.sound_btn.config(text=tr('btn_sound_on') if SETTINGS.get('sound_on_find', True) else tr('btn_sound_off'))
            self.names_btn.config(text=tr('btn_names_on') if SETTINGS.get('names_only_mode', False) else tr('btn_names_off'))
            self.lang_btn.config(text=tr('btn_lang'))
            self.folder_btn.config(text=tr('btn_folder'))
            self.drives_btn.config(text=tr('btn_drives'))
            self.stop_btn.config(text=tr('btn_stop'))
            self.pause_btn.config(text=tr('btn_pause'))
            self.export_txt_btn.config(text=tr('btn_export_txt'))
            self.export_word_btn.config(text=tr('btn_export_word'))
            self.errors_btn.config(text=tr('btn_errors'))

            self.scan_header_lbl.config(text=tr('scan_header'))
            self.log_header_lbl.config(text=tr('log_header'))
            self._update_timer_labels()

            self.info_header_lbl.config(text=tr('info_header'))
            self.info_subheader_lbl.config(text=tr('info_subheader'))
            self.boot_frame.config(text=tr('info_boot_log'))
            self.disk_frame.config(text=tr('info_disks'))
            self.fmt_frame.config(text=tr('info_formats'))
            self.ocr_frame.config(text=tr('info_ocr_status'))
            self.kw_frame.config(text=tr('info_keywords'))

            self.libs_header_lbl.config(text=tr('libs_header'))
            self.libs_current_lbl.config(text=tr('libs_current'))
            self.libs_log_frame.config(text=tr('libs_log'))

            for col, key in zip(self.tree['columns'],
                                ['col_filename', 'col_keywords', 'col_size',
                                 'col_owner', 'col_author', 'col_modified', 'col_disk']):
                self.tree.heading(col, text=tr(key))

            for col, key in zip(self.lib_tree['columns'],
                                ['libs_col_name', 'libs_col_type', 'libs_col_pip',
                                 'libs_col_fallbacks', 'libs_col_status', 'libs_col_version']):
                self.lib_tree.heading(col, text=tr(key))

            self._fill_keywords()
            self._fill_supported_formats_retranslate()

            try:
                menubar = self.root.nametowidget(self.root.cget('menu'))
                for i in range(menubar.index('end') + 1):
                    try:
                        entry_type = menubar.type(i)
                    except Exception:
                        continue
                    if entry_type != 'cascade':
                        continue
                    try:
                        submenu_name = menubar.entrycget(i, 'menu')
                        if not submenu_name:
                            continue
                        submenu = self.root.nametowidget(submenu_name)
                        for j in range(submenu.index('end') + 1):
                            try:
                                et = submenu.type(j)
                            except Exception:
                                continue
                            if et != 'command':
                                continue
                            label = submenu.entrycget(j, 'label')
                            if label in ("Сбросить чекпоинт", "Reset checkpoint"):
                                submenu.entryconfig(j, label=tr('menu_reset_checkpoint'))
                            elif label in ("Информация о чекпоинте", "Checkpoint info"):
                                submenu.entryconfig(j, label=tr('menu_checkpoint_info'))
                            elif label in ("Файл", "File"):
                                menubar.entryconfig(i, label=tr('menu_file'))
                            elif label in ("Инструменты", "Tools"):
                                menubar.entryconfig(i, label=tr('menu_tools'))
                            elif label in ("Справка", "Help"):
                                menubar.entryconfig(i, label=tr('menu_help'))
                    except Exception:
                        continue
            except Exception:
                pass

        except Exception as e:
            register_error('i18n', 'Language apply error / Ошибка применения языка', str(e))

    # ------------------------------------------------------------------
    # Info tab
    # ------------------------------------------------------------------
    def _build_info_tab(self, parent):
        top = tk.Frame(parent, bg="#e8eaf6")
        top.pack(fill=tk.X)
        self.info_header_lbl = tk.Label(top, text=tr('info_header'),
                                         font=("Arial", 13, "bold"), bg="#e8eaf6", fg="#1a237e")
        self.info_header_lbl.pack(pady=6)
        self.info_subheader_lbl = tk.Label(top, text=tr('info_subheader'),
                                            bg="#e8eaf6", fg="#3949ab", font=("Arial", 9))
        self.info_subheader_lbl.pack(pady=(0, 6))

        paned = ttk.PanedWindow(parent, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.boot_frame = tk.LabelFrame(paned, text=tr('info_boot_log'),
                                         font=("Arial", 10, "bold"))
        paned.add(self.boot_frame, weight=1)

        self.boot_log = scrolledtext.ScrolledText(self.boot_frame, wrap=tk.WORD,
                                                    font=("Consolas", 9), height=10)
        self.boot_log.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self.boot_log.tag_config('info', foreground='#0d47a1')
        self.boot_log.tag_config('success', foreground='#2e7d32')
        self.boot_log.tag_config('error', foreground='#c62828')
        self.boot_log.tag_config('warning', foreground='#ef6c00')
        self.boot_log.tag_config('header', foreground='#1a237e', font=("Consolas", 10, "bold"))
        add_copy_context_menu(self.boot_log, self.root)

        bottom = tk.Frame(paned, bg="#f5f5f5")
        paned.add(bottom, weight=2)

        bottom_pane = ttk.PanedWindow(bottom, orient=tk.HORIZONTAL)
        bottom_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left = tk.Frame(bottom_pane, bg="#f5f5f5")
        bottom_pane.add(left, weight=1)

        left_pane = ttk.PanedWindow(left, orient=tk.VERTICAL)
        left_pane.pack(fill=tk.BOTH, expand=True)

        self.disk_frame = tk.LabelFrame(left_pane, text=tr('info_disks'),
                                         font=("Arial", 10, "bold"))
        left_pane.add(self.disk_frame, weight=1)

        self.disk_text = scrolledtext.ScrolledText(self.disk_frame, wrap=tk.WORD,
                                                     font=("Consolas", 9), height=8)
        self.disk_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self.disk_text.insert(tk.END, tr('info_loading_disks'))
        self.disk_text.config(state=tk.DISABLED)
        add_copy_context_menu(self.disk_text, self.root)

        self.fmt_frame = tk.LabelFrame(left_pane, text=tr('info_formats'),
                                        font=("Arial", 10, "bold"))
        left_pane.add(self.fmt_frame, weight=1)

        self.fmt_text = scrolledtext.ScrolledText(self.fmt_frame, wrap=tk.WORD,
                                                    font=("Consolas", 9), height=10)
        self.fmt_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self._fill_supported_formats_retranslate()
        self.fmt_text.config(state=tk.DISABLED)
        add_copy_context_menu(self.fmt_text, self.root)

        right = tk.Frame(bottom_pane, bg="#f5f5f5")
        bottom_pane.add(right, weight=1)

        right_pane = ttk.PanedWindow(right, orient=tk.VERTICAL)
        right_pane.pack(fill=tk.BOTH, expand=True)

        self.ocr_frame = tk.LabelFrame(right_pane, text=tr('info_ocr_status'),
                                        font=("Arial", 10, "bold"))
        right_pane.add(self.ocr_frame, weight=1)

        self.ocr_label = tk.Label(self.ocr_frame, text=tr('info_ocr_init'),
                                   font=("Consolas", 10), bg="#f5f5f5",
                                   fg="#1a237e", anchor=tk.W, justify=tk.LEFT)
        self.ocr_label.pack(fill=tk.X, padx=5, pady=5)

        self.kw_frame = tk.LabelFrame(right_pane, text=tr('info_keywords'),
                                       font=("Arial", 10, "bold"))
        right_pane.add(self.kw_frame, weight=2)

        self.kw_text = scrolledtext.ScrolledText(self.kw_frame, wrap=tk.WORD,
                                                   font=("Consolas", 9), height=14)
        self.kw_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self._fill_keywords()
        self.kw_text.config(state=tk.DISABLED)
        add_copy_context_menu(self.kw_text, self.root)

    def _fill_supported_formats_retranslate(self):
        try:
            self.fmt_text.config(state=tk.NORMAL)
            self.fmt_text.delete("1.0", tk.END)
        except Exception:
            pass
        lang = SETTINGS.get('ui_language', 'ru')
        if lang == 'en':
            lines = [
                "  • PDF: .pdf",
                "    └─ PDFPlumber / PyPDF2 / pypdf / PyMuPDF / pdfminer.six / peepdf / pdfid / pdf2image+OCR",
                "  • Word: .docx, .docm, .doc, .dot",
                "    └─ python-docx / docx2txt / mammoth / textract / olefile",
                "  • Excel: .xlsx, .xlsm, .xltx, .xltm, .xls",
                "    └─ openpyxl / xlrd / pandas",
                "  • PowerPoint: .pptx, .pptm",
                "    └─ python-pptx / direct XML parsing",
                "  • OpenDocument: .odt, .ods, .odp, .odg, .odf",
                "    └─ odfpy",
                "  • RTF: .rtf",
                "    └─ striprtf / regex-fallback",
                "  • Visio: .vsdx, .vsd, .vssx, .vstx",
                "    └─ textract / direct XML",
                "  • Mail: .eml, .msg, .mbox",
                "    └─ Extract subject, sender, recipients (To/Cc/Bcc)",
                "    └─ Body (text/plain, text/html) + attachments as regular files",
                "  • Images: .jpg, .jpeg, .png, .bmp, .tif, .tiff, .gif (all frames),",
                "    .webp, .ico, .heic, .heif, .avif, .svg, .tga, .psd, .raw, .cr2,",
                "    .nef, .dng, .arw and more",
                "    └─ Pillow + EasyOCR/Tesseract (+ pillow-heif, pillow-avif-plugin)",
                "    └─ exifread (EXIF/GPS) + Stegano (LSB heuristic)",
                "  • Text/Code/Data: .txt, .md, .rst, .log, .csv, .tsv, .json, .jsonl,",
                "    .xml, .yaml, .toml, .ini, .cfg, .html, .css, .py, .js, .ts, .java,",
                "    .cs, .cpp, .c, .go, .rs, .rb, .php, .sql, .bat, .ps1, .sh etc.",
                "    └─ Built-in + chardet / cchardet",
                "  • Archives (recursive): .zip, .rar, .7z, .tar, .gz, .tgz, .bz2, .tbz2,",
                "    .xz, .txz, .lzma, .cab, .iso, .jar, .war, .ear, .apk, .ipa, .whl, .egg",
                "    └─ zipfile / tarfile / rarfile / py7zr / gzip / bz2 / lzma",
                "    └─ RAR requires 7-Zip (https://www.7-zip.org/) or WinRAR",
                "  • ★ AutoCAD: .dwg, .dxf, .dwt, .dws, .dwf, .dwfx",
                "    └─ DXF sections, ASCII/UTF-16 strings, ezdxf",
                "  • ★ KOMPAS: .cdw, .frw, .spw, .m3d, .a3d, .c3d, .kdw, .cdt",
                "    └─ zlib + ASCII/UTF-16/cp1251 strings",
                "  • ★ GrandSmeta: .gsfx, .gsf, .grs, .gs1, .gs2, .sfx",
                "    └─ XML + zlib + cp1251/UTF-16",
                "  • ★ MacroMine: .mmd, .mmx, .mmz, .mma",
                "    └─ zlib + cp1251/UTF-16 strings",
                "  • ★ Civil 3D / Geodesy: .landxml, .tin, .dem, .pts, .dwg, .dxf",
                "    └─ XML/CSV + binary strings",
                "  • Executables: .exe, .dll, .sys, .scr, .com, .msi",
                "    └─ pefile + python-magic",
                "  • Forensic images: .e01, .raw, .dd, .img, .vmdk, .vhd, .mem, .dmp",
                "    └─ pytsk3 / pyewf / pyvmdk / dissect",
                "  • Registry/logs: .reg, .dat, .hiv, .evt, .evtx",
                "    └─ python-registry / regipy",
                "  • USB artifacts: pyusb, usbinfo, usb_parser, python-usbescape",
                "  • Memory analysis: volatility3 (ext.), hindsight, triage, dftimewolf",
                "",
                "  ★ Media characteristics (USB/HDD/SSD/flash) are included",
                "    in the report: letter, label, FS, type, model, interface,",
                "    serial numbers, size, USB flag.",
            ]
        else:
            lines = [
                "  • PDF: .pdf",
                "    └─ PDFPlumber / PyPDF2 / pypdf / PyMuPDF / pdfminer.six / peepdf / pdfid / pdf2image+OCR",
                "  • Word: .docx, .docm, .doc, .dot",
                "    └─ python-docx / docx2txt / mammoth / textract / olefile",
                "  • Excel: .xlsx, .xlsm, .xltx, .xltm, .xls",
                "    └─ openpyxl / xlrd / pandas",
                "  • PowerPoint: .pptx, .pptm",
                "    └─ python-pptx / прямой разбор XML",
                "  • OpenDocument: .odt, .ods, .odp, .odg, .odf",
                "    └─ odfpy",
                "  • RTF: .rtf",
                "    └─ striprtf / regex-fallback",
                "  • Visio: .vsdx, .vsd, .vssx, .vstx",
                "    └─ textract / прямой XML",
                "  • Почта: .eml, .msg, .mbox",
                "    └─ Извлечение темы, отправителя, получателей (To/Cc/Bcc)",
                "    └─ Тело (text/plain, text/html) + вложения как обычные файлы",
                "  • Изображения: .jpg, .jpeg, .png, .bmp, .tif, .tiff, .gif (все кадры),",
                "    .webp, .ico, .heic, .heif, .avif, .svg, .tga, .psd, .raw, .cr2,",
                "    .nef, .dng, .arw и др.",
                "    └─ Pillow + EasyOCR/Tesseract (+ pillow-heif, pillow-avif-plugin)",
                "    └─ exifread (EXIF/GPS) + Stegano (LSB-эвристика)",
                "  • Текст/Код/Данные: .txt, .md, .rst, .log, .csv, .tsv, .json, .jsonl,",
                "    .xml, .yaml, .toml, .ini, .cfg, .html, .css, .py, .js, .ts, .java,",
                "    .cs, .cpp, .c, .go, .rs, .rb, .php, .sql, .bat, .ps1, .sh и др.",
                "    └─ Встроенный + chardet / cchardet",
                "  • Архивы (рекурсивно): .zip, .rar, .7z, .tar, .gz, .tgz, .bz2, .tbz2,",
                "    .xz, .txz, .lzma, .cab, .iso, .jar, .war, .ear, .apk, .ipa, .whl, .egg",
                "    └─ zipfile / tarfile / rarfile / py7zr / gzip / bz2 / lzma",
                "    └─ RAR требует 7-Zip (https://www.7-zip.org/) или WinRAR",
                "  • ★ AutoCAD: .dwg, .dxf, .dwt, .dws, .dwf, .dwfx",
                "    └─ Парсинг DXF-секций, ASCII/UTF-16 строки, ezdxf",
                "  • ★ КОМПАС: .cdw, .frw, .spw, .m3d, .a3d, .c3d, .kdw, .cdt",
                "    └─ zlib-распаковка + ASCII/UTF-16/cp1251 строки",
                "  • ★ ГрандСмета: .gsfx, .gsf, .grs, .gs1, .gs2, .sfx",
                "    └─ XML-парсинг + zlib + cp1251/UTF-16",
                "  • ★ MacroMine: .mmd, .mmx, .mmz, .mma",
                "    └─ zlib + cp1251/UTF-16 строки",
                "  • ★ Civil 3D / Геодезия: .landxml, .tin, .dem, .pts, .dwg, .dxf",
                "    └─ XML/CSV + бинарные строки",
                "  • Исполняемые: .exe, .dll, .sys, .scr, .com, .msi",
                "    └─ pefile + python-magic",
                "  • Форензик-образы: .e01, .raw, .dd, .img, .vmdk, .vhd, .mem, .dmp",
                "    └─ pytsk3 / pyewf / pyvmdk / dissect",
                "  • Реестр/журналы: .reg, .dat, .hiv, .evt, .evtx",
                "    └─ python-registry / regipy",
                "  • USB-артефакты: pyusb, usbinfo, usb_parser, python-usbescape",
                "  • Анализ памяти: volatility3 (внешн.), hindsight, triage, dftimewolf",
                "",
                "  ★ Характеристики носителя (USB/HDD/SSD/флешка) включаются",
                "    в отчёт: буква, метка, ФС, тип, модель, интерфейс,",
                "    серийные номера, объём, флаг USB.",
            ]
        try:
            self.fmt_text.insert(tk.END, "\n".join(lines))
            self.fmt_text.config(state=tk.DISABLED)
        except Exception:
            pass

    def _fill_keywords(self):
        try:
            self.kw_text.config(state=tk.NORMAL)
            self.kw_text.delete("1.0", tk.END)
            lang = SETTINGS.get('ui_language', 'ru')
            if lang == 'en':
                self.kw_text.insert(tk.END, f"  Total: {len(KEYWORDS)}\n")
                self.kw_text.insert(tk.END, f"  File: {KEYWORDS_FILE}\n\n")
            else:
                self.kw_text.insert(tk.END, f"  Всего: {len(KEYWORDS)}\n")
                self.kw_text.insert(tk.END, f"  Файл: {KEYWORDS_FILE}\n\n")
            for i, kw in enumerate(KEYWORDS, 1):
                self.kw_text.insert(tk.END, f"  {i:>3}. {kw}\n")
            self.kw_text.config(state=tk.DISABLED)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Scan tab
    # ------------------------------------------------------------------
    def _build_scan_tab(self, parent):
        control_frame = tk.Frame(parent, bg="#e8eaf6")
        control_frame.pack(fill=tk.X)

        settings_frame = tk.Frame(control_frame, bg="#e8eaf6")
        settings_frame.pack(fill=tk.X, pady=(6, 3))

        self.sound_btn = tk.Button(
            settings_frame, text=tr('btn_sound_on'), width=18,
            bg="#2e7d32", fg="white",
            font=("Arial", 10, "bold"), command=self._toggle_sound
        )
        self.sound_btn.pack(side=tk.LEFT, padx=(5, 3))

        self.names_btn = tk.Button(
            settings_frame, text=tr('btn_names_off'), width=22,
            bg="#2e7d32", fg="white",
            font=("Arial", 10, "bold"), command=self._toggle_names_only
        )
        self.names_btn.pack(side=tk.LEFT, padx=3)

        self.lang_btn = tk.Button(
            settings_frame, text=tr('btn_lang'), width=16,
            bg="#3949ab", fg="white",
            font=("Arial", 10, "bold"), command=self._toggle_lang
        )
        self.lang_btn.pack(side=tk.LEFT, padx=3)

        btn_frame = tk.Frame(control_frame, bg="#e8eaf6")
        btn_frame.pack(fill=tk.X, pady=3)

        self.folder_btn = tk.Button(btn_frame, text=tr('btn_folder'), width=16, bg="#3949ab", fg="white",
                                     font=("Arial", 10, "bold"), command=self.select_folder)
        self.folder_btn.pack(side=tk.LEFT, padx=(5, 3))

        self.drives_btn = tk.Button(btn_frame, text=tr('btn_drives'), width=20, bg="#3949ab", fg="white",
                                     font=("Arial", 10, "bold"), command=self.select_drives_dialog)
        self.drives_btn.pack(side=tk.LEFT, padx=3)

        btn_frame2 = tk.Frame(control_frame, bg="#e8eaf6")
        btn_frame2.pack(fill=tk.X, pady=3)

        self.stop_btn = tk.Button(btn_frame2, text=tr('btn_stop'), width=14, bg="#c62828", fg="white",
                                   font=("Arial", 10, "bold"), command=self.stop_scan, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(5, 3))

        self.pause_btn = tk.Button(btn_frame2, text=tr('btn_pause'), width=12, bg="#ef6c00", fg="white",
                                    font=("Arial", 10, "bold"), command=self.toggle_pause, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=3)

        self.export_txt_btn = tk.Button(btn_frame2, text=tr('btn_export_txt'), width=16, bg="#2e7d32", fg="white",
                                         font=("Arial", 10, "bold"), command=lambda: self.export('txt'))
        self.export_txt_btn.pack(side=tk.LEFT, padx=3)

        self.export_word_btn = tk.Button(btn_frame2, text=tr('btn_export_word'), width=18, bg="#1565c0", fg="white",
                                          font=("Arial", 10, "bold"), command=self.export_word)
        self.export_word_btn.pack(side=tk.LEFT, padx=3)

        self.errors_btn = tk.Button(btn_frame2, text=tr('btn_errors'), width=12, bg="#c62828", fg="white",
                                     font=("Arial", 10, "bold"), command=self.show_errors)
        self.errors_btn.pack(side=tk.LEFT, padx=(3, 5))

        self._update_sound_button()
        self._update_names_button()
        self._update_lang_button()

        timer_frame = tk.Frame(parent, bg="#e8eaf6")
        timer_frame.pack(fill=tk.X, padx=10, pady=(6, 2))

        self.timer_found_lbl = tk.Label(
            timer_frame, text="", bg="#e8eaf6", fg="#1a237e",
            font=("Arial", 11, "bold"), anchor='w')
        self.timer_found_lbl.pack(side=tk.LEFT, padx=(0, 15))

        self.timer_scanned_lbl = tk.Label(
            timer_frame, text="", bg="#e8eaf6", fg="#1a237e",
            font=("Arial", 11, "bold"), anchor='w')
        self.timer_scanned_lbl.pack(side=tk.LEFT, padx=(0, 15))

        self.timer_elapsed_lbl = tk.Label(
            timer_frame, text="", bg="#e8eaf6", fg="#0d47a1",
            font=("Consolas", 12, "bold"), anchor='w')
        self.timer_elapsed_lbl.pack(side=tk.LEFT, padx=(0, 15))

        self._update_timer_labels()

        progress_frame = tk.Frame(parent, bg="#e8eaf6")
        progress_frame.pack(fill=tk.X, padx=10, pady=(2, 5))
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))
        self.progress_label = tk.Label(progress_frame, text="0 / 0", bg="#e8eaf6",
                                        fg="#1a237e", width=15)
        self.progress_label.pack(side=tk.RIGHT)

        main_pane = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        left_frame = tk.Frame(main_pane)
        main_pane.add(left_frame, weight=3)

        self.scan_header_lbl = tk.Label(left_frame, text=tr('scan_header'),
                                         font=("Arial", 11, "bold"), bg="#c5cae9")
        self.scan_header_lbl.pack(fill=tk.X)

        tree_container = tk.Frame(left_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ('filename', 'keywords', 'size', 'owner', 'author', 'modified', 'disk_letter')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=20)
        for col, key in zip(columns,
                            ['col_filename', 'col_keywords', 'col_size',
                             'col_owner', 'col_author', 'col_modified', 'col_disk']):
            self.tree.heading(col, text=tr(key))
        widths = {'filename': 250, 'keywords': 180, 'size': 90,
                  'owner': 130, 'author': 130, 'modified': 140, 'disk_letter': 60}
        for col in columns:
            self.tree.column(col, width=widths[col], anchor='w')

        vsb = ttk.Scrollbar(tree_container, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        self.tree.bind('<Double-1>', self.show_file_details)
        add_copy_context_menu(self.tree, self.root)
        _make_sortable(self.tree, numeric_cols={'size'})

        right_frame = tk.Frame(main_pane)
        main_pane.add(right_frame, weight=2)
        self.log_header_lbl = tk.Label(right_frame, text=tr('log_header'),
                                        font=("Arial", 11, "bold"), bg="#c5cae9")
        self.log_header_lbl.pack(fill=tk.X)
        self.log_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD,
                                                   font=("Consolas", 9), bg="#f5f5f5")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_config('info', foreground='#0d47a1')
        self.log_text.tag_config('success', foreground='#2e7d32')
        self.log_text.tag_config('error', foreground='#c62828')
        self.log_text.tag_config('warning', foreground='#ef6c00')
        self.log_text.tag_config('found', foreground='#6a1b9a', font=("Consolas", 9, "bold"))
        self.log_text.tag_config('header', foreground='#1a237e', font=("Consolas", 10, "bold"))
        add_copy_context_menu(self.log_text, self.root)

    # ------------------------------------------------------------------
    # Libraries tab
    # ------------------------------------------------------------------
    def _build_libs_tab(self, parent):
        top = tk.Frame(parent, bg="#e8eaf6")
        top.pack(fill=tk.X)
        self.libs_header_lbl = tk.Label(top, text=tr('libs_header'),
                                         font=("Arial", 12, "bold"), bg="#e8eaf6", fg="#1a237e")
        self.libs_header_lbl.pack(pady=4)

        info_frame = tk.Frame(parent, bg="#fff9c4", relief=tk.RIDGE, bd=1)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        self.libs_current_lbl = tk.Label(info_frame, text=tr('libs_current'),
                                          font=("Arial", 9, "bold"), bg="#fff9c4")
        self.libs_current_lbl.pack(anchor=tk.W, padx=5)
        self.lib_current_label = tk.Label(info_frame, text="—",
                                           font=("Arial", 11, "bold"), bg="#fff9c4",
                                           fg="#c62828", wraplength=1200, justify=tk.LEFT)
        self.lib_current_label.pack(anchor=tk.W, padx=5, pady=(0, 5))

        prog_frame = tk.Frame(parent, bg="#e8eaf6")
        prog_frame.pack(fill=tk.X, padx=10, pady=2)
        self.lib_progress = ttk.Progressbar(prog_frame, mode='determinate')
        self.lib_progress.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))
        self.lib_progress_label = tk.Label(prog_frame, text="0 / 0", bg="#e8eaf6",
                                            fg="#1a237e", width=20)
        self.lib_progress_label.pack(side=tk.RIGHT)

        tree_wrap = tk.Frame(parent)
        tree_wrap.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.lib_tree = ttk.Treeview(tree_wrap,
                                     columns=('name', 'type', 'pip', 'fallbacks', 'status', 'version'),
                                     show='headings', height=14)
        for col, key in zip(('name', 'type', 'pip', 'fallbacks', 'status', 'version'),
                            ['libs_col_name', 'libs_col_type', 'libs_col_pip',
                             'libs_col_fallbacks', 'libs_col_status', 'libs_col_version']):
            self.lib_tree.heading(col, text=tr(key))
        for col, width in [('name', 180), ('type', 100), ('pip', 170),
                            ('fallbacks', 220), ('status', 130), ('version', 100)]:
            self.lib_tree.column(col, width=width, anchor='w')

        lib_vsb = ttk.Scrollbar(tree_wrap, orient='vertical', command=self.lib_tree.yview)
        self.lib_tree.configure(yscrollcommand=lib_vsb.set)

        self.lib_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lib_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        add_copy_context_menu(self.lib_tree, self.root)
        _make_sortable(self.lib_tree)

        self._fill_libs_tree()

        self.libs_log_frame = tk.LabelFrame(parent, text=tr('libs_log'),
                                             font=("Arial", 10, "bold"))
        self.libs_log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.lib_log = scrolledtext.ScrolledText(self.libs_log_frame, wrap=tk.WORD,
                                                   font=("Consolas", 9), height=10)
        self.lib_log.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        self.lib_log.tag_config('info', foreground='#0d47a1')
        self.lib_log.tag_config('success', foreground='#2e7d32')
        self.lib_log.tag_config('error', foreground='#c62828')
        self.lib_log.tag_config('warning', foreground='#ef6c00')
        self.lib_log.tag_config('header', foreground='#1a237e', font=("Consolas", 10, "bold"))
        add_copy_context_menu(self.lib_log, self.root)

    def _fill_libs_tree(self):
        for iid in self.lib_tree.get_children():
            self.lib_tree.delete(iid)
        lang = SETTINGS.get('ui_language', 'ru')
        for lib_id, info in ALL_LIBRARIES.items():
            st = LIBRARY_STATUS.get(lib_id, False)
            ver = LIBRARY_VERSIONS.get(lib_id, "")
            used = LIBRARY_INSTALLED_AS.get(lib_id, "")
            if lang == 'en':
                status = "INSTALLED" if st else "NOT INSTALLED"
                if st and used and used != info['pip']:
                    status = f"FALLBACK: {used}"
            else:
                status = "УСТАНОВЛЕНА" if st else "НЕ УСТАНОВЛЕНА"
                if st and used and used != info['pip']:
                    status = f"АНАЛОГ: {used}"
            fb = ", ".join(f[0] for f in info.get('fallbacks', [])) or "—"
            self.lib_tree.insert('', tk.END, iid=lib_id,
                                 values=(info['name'], info['type'], info['pip'], fb, status, ver))

    def _update_libs_tree(self):
        lang = SETTINGS.get('ui_language', 'ru')
        for lib_id, info in ALL_LIBRARIES.items():
            st = LIBRARY_STATUS.get(lib_id, False)
            ver = LIBRARY_VERSIONS.get(lib_id, "")
            used = LIBRARY_INSTALLED_AS.get(lib_id, "")
            if lang == 'en':
                status = "INSTALLED" if st else "NOT INSTALLED"
                if st and used and used != info['pip']:
                    status = f"FALLBACK: {used}"
            else:
                status = "УСТАНОВЛЕНА" if st else "НЕ УСТАНОВЛЕНА"
                if st and used and used != info['pip']:
                    status = f"АНАЛОГ: {used}"
            fb = ", ".join(f[0] for f in info.get('fallbacks', [])) or "—"
            try:
                self.lib_tree.item(lib_id, values=(info['name'], info['type'], info['pip'],
                                                    fb, status, ver))
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    def log(self, msg, level='info'):
        self.log_queue.put((msg, level))

    def _poll_log_queue(self):
        try:
            while True:
                msg, level = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, msg + "\n", level)
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_log_queue)

    def _poll_lib_queue(self):
        try:
            while True:
                ev = self.lib_queue.get_nowait()
                kind = ev.get('kind')
                if kind == 'status':
                    self.lib_current_label.config(text=ev.get('text', '—'))
                elif kind == 'log':
                    msg = ev.get('msg', '')
                    lvl = ev.get('level', 'info')
                    self.lib_log.insert(tk.END, msg + "\n", lvl)
                    self.lib_log.see(tk.END)
                elif kind == 'boot_log':
                    msg = ev.get('msg', '')
                    lvl = ev.get('level', 'info')
                    self.boot_log.insert(tk.END, msg + "\n", lvl)
                    self.boot_log.see(tk.END)
                elif kind == 'progress':
                    d, t = ev.get('done', 0), ev.get('total', 1)
                    self.lib_progress['maximum'] = max(t, 1)
                    self.lib_progress['value'] = d
                    self.lib_progress_label.config(text=f"{d} / {t}")
                elif kind == 'refresh_tree':
                    self._update_libs_tree()
                elif kind == 'disk_info':
                    self._set_disk_info(ev.get('data', []))
                elif kind == 'ocr_status':
                    self.ocr_label.config(text=ev.get('text', '—'))
                elif kind == 'scan_progress':
                    cur = ev.get('current', 0)
                    tot = ev.get('total', 0)
                    self._apply_scan_progress(cur, tot)
                elif kind == 'scan_found':
                    self._current_found = ev.get('found', self._current_found)
                    self._update_timer_labels()
                elif kind == 'scan_finished':
                    self._scan_finished()
        except queue.Empty:
            pass
        self.root.after(50, self._poll_lib_queue)

    # ------------------------------------------------------------------
    # Timer labels
    # ------------------------------------------------------------------
    def _update_timer_labels(self):
        try:
            lang = SETTINGS.get('ui_language', 'ru')
            found_lbl = tr('timer_found')
            scanned_lbl = tr('timer_scanned')
            elapsed_lbl = tr('timer_elapsed')
            self.timer_found_lbl.config(text=f"{found_lbl}: {self._current_found}")
            self.timer_scanned_lbl.config(
                text=f"{scanned_lbl}: {self._current_scanned}/{self._current_total}")
            if self._scan_start_monotonic > 0 and self._scan_running:
                elapsed_str = format_elapsed(time.monotonic() - self._scan_start_monotonic)
            else:
                elapsed_str = self.scan_duration_str or "00:00:00"
            self.timer_elapsed_lbl.config(text=f"{elapsed_lbl}: {elapsed_str}")
        except Exception:
            pass

    def _apply_scan_progress(self, current, total):
        try:
            if total <= 0:
                self.progress['maximum'] = 1
                self.progress['value'] = 0
                self.progress_label.config(text=tr('progress_preparing'))
                self.status_bar.config(text=tr('status_scanning_prep'))
                self._current_scanned = 0
                self._current_total = 0
            else:
                self.progress['maximum'] = total
                self.progress['value'] = min(current, total)
                self.progress_label.config(text=f"{current} / {total}")
                self._current_scanned = current
                self._current_total = total
                pct = int(100 * current / total) if total > 0 else 0
                lang = SETTINGS.get('ui_language', 'ru')
                if lang == 'en':
                    self.status_bar.config(text=f"Scanning: {current}/{total} ({pct}%)")
                else:
                    self.status_bar.config(text=f"Сканирование: {current}/{total} ({pct}%)")
            self._update_timer_labels()
        except Exception:
            pass

    def _set_disk_info(self, disks):
        self.disk_text.config(state=tk.NORMAL)
        self.disk_text.delete("1.0", tk.END)
        if not disks:
            self.disk_text.insert(tk.END, "  Disk info unavailable / Информация о дисках недоступна.\n")
        else:
            for i, d in enumerate(disks, 1):
                self.disk_text.insert(tk.END, f"  [{i}] PHYSICAL DISK / ФИЗИЧЕСКИЙ ДИСК\n")
                self.disk_text.insert(tk.END, f"      Model / Модель        : {safe_decode(d.get('model', '?'))}\n")
                self.disk_text.insert(tk.END, f"      Manufacturer / Производитель : {safe_decode(d.get('manufacturer', '?'))}\n")
                self.disk_text.insert(tk.END, f"      Serial / Серийный №    : {safe_decode(d.get('serial_number', '?'))}\n")
                self.disk_text.insert(tk.END, f"      Interface / Интерфейс     : {safe_decode(d.get('interface_type', '?'))}\n")
                self.disk_text.insert(tk.END, f"      Size / Размер        : {d.get('size', '?')}\n")
                self.disk_text.insert(tk.END, f"      Partitions / Разделов      : {d.get('partitions', 0)}\n")
                if d.get('drive_letter'):
                    self.disk_text.insert(tk.END, f"      Drive letters / Буквы дисков : {', '.join(d['drive_letter'])}\n")
                self.disk_text.insert(tk.END, "\n")
        self.disk_text.config(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Scan timer
    # ------------------------------------------------------------------
    def _start_scan_timer(self):
        self._scan_start_monotonic = time.monotonic()
        self._last_log_elapsed = 0
        self._scan_running = True
        self._current_found = 0
        self._current_scanned = 0
        self._current_total = 0
        self._update_timer_labels()
        self._tick_timer()

    def _stop_scan_timer(self):
        self._scan_running = False
        if self._elapsed_timer_id is not None:
            try:
                self.root.after_cancel(self._elapsed_timer_id)
            except Exception:
                pass
            self._elapsed_timer_id = None
        try:
            if self._scan_start_monotonic > 0:
                self.scan_duration_str = format_elapsed(
                    time.monotonic() - self._scan_start_monotonic)
            self._update_timer_labels()
        except Exception:
            pass

    def _tick_timer(self):
        try:
            if not self._scan_running:
                self._elapsed_timer_id = None
                return
            elapsed = time.monotonic() - self._scan_start_monotonic
            elapsed_str = format_elapsed(elapsed)
            self.timer_elapsed_lbl.config(
                text=f"{tr('timer_elapsed')}: {elapsed_str}")
            if elapsed - self._last_log_elapsed >= 30:
                self._last_log_elapsed = int(elapsed // 30) * 30
                self.log(f"[TIMER] {elapsed_str}", 'info')
            self._elapsed_timer_id = self.root.after(1000, self._tick_timer)
        except Exception:
            self._elapsed_timer_id = None

    # ------------------------------------------------------------------
    # Background library install
    # ------------------------------------------------------------------
    def _start_background_library_install(self):
        for line in [
            f"{PROGRAM_NAME} v{VERSION}",
            f"Author / Автор: {AUTHOR}",
            f"License / Лицензия: {LICENSE}",
            f"GitHub: {GITHUB}",
            f"Libs dir / Папка библиотек: {LIBS_DIR}",
            f"Keywords / Ключевые слова: {KEYWORDS_FILE}",
            f"Local modules added / Локальных модулей добавлено в sys.path: {len(_LOCAL_MODULES_ADDED)}",
            "",
            "=== BACKGROUND LIBRARY CHECK AND INSTALL ===",
            "=== ФОНОВАЯ ПРОВЕРКА И УСТАНОВКА БИБЛИОТЕК ===",
            "GUI is available immediately. Installation proceeds in background. /",
            "GUI доступен сразу. Установка идёт параллельно.",
        ]:
            self.lib_queue.put({'kind': 'boot_log', 'msg': line, 'level': 'header'})

        self.lib_queue.put({'kind': 'status', 'text': 'Background library check... / Фоновая проверка библиотек...'})

        def worker():
            global HAS_OCR
            try:
                def progress_cb(d, t, name):
                    self.lib_queue.put({'kind': 'progress', 'done': d, 'total': t})

                def log_cb(msg, level='info'):
                    self.lib_queue.put({'kind': 'log', 'msg': msg, 'level': level})
                    self.lib_queue.put({'kind': 'boot_log', 'msg': msg, 'level': level})
                    self.lib_queue.put({'kind': 'refresh_tree'})

                def status_cb(msg, level='info'):
                    self.lib_queue.put({'kind': 'status', 'text': msg})

                check_and_install_libraries_parallel(
                    progress_cb=progress_cb,
                    status_cb=status_cb,
                    log_cb=log_cb,
                )
                _ensure_libs_importable()
                scan_local_modules(BASE_DIR)
                refresh_library_flags()
                self.lib_queue.put({'kind': 'refresh_tree'})

                self.lib_queue.put({'kind': 'status', 'text': 'OCR initialization... / Инициализация OCR...'})
                try:
                    if not SETTINGS.get('ocr_enabled', True):
                        txt = ("OCR: DISABLED in settings / ОТКЛЮЧЁН в настройках")
                        HAS_OCR = False
                    else:
                        ok = init_ocr()
                        if ok:
                            if reader is not None:
                                txt = (f"EasyOCR: YES/ДА\n"
                                       f"Tesseract: {'YES/ДА (' + str(TESSERACT_EXE) + ')' if HAS_TESSERACT else 'NO/НЕТ'}")
                            else:
                                txt = (f"EasyOCR: NO/НЕТ\n"
                                       f"Tesseract: {'YES/ДА (' + str(TESSERACT_EXE) + ')' if HAS_TESSERACT else 'NO/НЕТ'}")
                        else:
                            txt = "OCR unavailable / недоступен"
                except Exception as e:
                    register_error('ocr-init', 'init_ocr error', str(e))
                    txt = f"OCR error / Ошибка OCR: {e}"
                self.lib_queue.put({'kind': 'ocr_status', 'text': txt})
                self.lib_queue.put({'kind': 'boot_log',
                                    'msg': f"OCR: {txt}",
                                    'level': 'success' if HAS_OCR else 'warning'})

                self.lib_queue.put({'kind': 'status', 'text': 'Getting disk info... / Получение информации о дисках...'})
                try:
                    disks = get_detailed_disk_info()
                except Exception as e:
                    register_error('disks', 'Disk info error', str(e))
                    disks = []
                self.disk_info_list = disks
                self.lib_queue.put({'kind': 'disk_info', 'data': disks})
                self.lib_queue.put({'kind': 'boot_log',
                                    'msg': f"Disks found / Найдено дисков: {len(disks)}",
                                    'level': 'info'})

                refresh_library_flags()
                self.lib_queue.put({'kind': 'refresh_tree'})

                installed = sum(1 for s in LIBRARY_STATUS.values() if s)
                total = len(ALL_LIBRARIES)
                self.lib_queue.put({'kind': 'boot_log',
                                    'msg': f"Libraries installed / Библиотек установлено: {installed}/{total}",
                                    'level': 'success' if installed == total else 'warning'})
                self.lib_queue.put({'kind': 'status', 'text': 'Ready / Готов к работе'})
                self.libs_ready.set()
            except Exception as e:
                register_error('lib-install-thread', 'Install thread error / Ошибка в потоке установки', str(e))
                self.lib_queue.put({'kind': 'log', 'msg': f"Critical install error / Критическая ошибка установки: {e}",
                                    'level': 'error'})
                self.libs_ready.set()

        self.lib_install_thread = threading.Thread(target=worker, daemon=True)
        self.lib_install_thread.start()

    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------
    def select_drives_dialog(self):
        try:
            drives = get_drives_detailed(include_network=True)
        except Exception as e:
            register_error('drives', 'Drive list error / Ошибка получения списка дисков', str(e))
            drives = []
        if not drives:
            messagebox.showwarning("Drives / Диски", tr('msg_no_disks'))
            return
        dlg = DriveSelectDialog(self.root, drives, preselect_all=True)
        self.root.wait_window(dlg)
        if dlg.result:
            self._start_scan([Path(p) for p in dlg.result])

    def select_folder(self):
        folder = filedialog.askdirectory(title=tr('menu_select_folder'))
        if folder:
            self._start_scan([Path(folder)])

    def _start_scan(self, paths: List[Path]):
        if self.scan_thread and self.scan_thread.is_alive():
            messagebox.showwarning("Scanning / Сканирование", tr('msg_scan_running'))
            return

        _ensure_libs_importable()
        refresh_library_flags()

        global HAS_OCR
        if not SETTINGS.get('ocr_enabled', True):
            HAS_OCR = False

        self.auditor = FileAuditorPro()
        self.auditor.keywords = list(KEYWORDS)
        self.auditor.names_only = bool(SETTINGS.get('names_only_mode', False))
        self.tree.delete(*self.tree.get_children())
        self.progress['value'] = 0
        self.progress['maximum'] = 100
        self.progress_label.config(text=tr('progress_preparing'))
        self.stop_event.clear()
        self.pause_event.clear()
        self.stop_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.NORMAL, text=tr('btn_pause'))
        self.status_bar.config(text=tr('status_scanning_prep'))
        self.audit_started_str = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        self.audit_finished_str = ""
        self.scan_duration_str = ""
        self._scan_targets = [str(p) for p in paths]

        self._start_scan_timer()

        try:
            self.notebook.select(self.tab_scan)
            self.root.update_idletasks()
        except Exception:
            pass

        try:
            self.log_text.delete("1.0", tk.END)
            self.log("=== SCAN START / НАЧАЛО СКАНИРОВАНИЯ ===", 'header')
            if self.auditor.names_only:
                self.log("MODE: NAMES ONLY / РЕЖИМ: ТОЛЬКО ИМЕНА", 'warning')
            for p in paths:
                self.log(f"Target / Цель: {p}", 'info')
                drive_info = get_volume_full_info(str(p))
                block = format_drive_info_block(drive_info)
                if block:
                    self.log(f"--- Media characteristics / Характеристики носителя {p} ---", 'info')
                    for line in block.splitlines():
                        self.log(f"    {line}", 'info')
        except Exception:
            pass

        def on_find(rec):
            try:
                play_find_sound()
            except Exception:
                pass
            try:
                self.lib_queue.put({'kind': 'scan_found',
                                     'found': len(self.auditor.results)})
            except Exception:
                pass

        def worker():
            try:
                for p in paths:
                    if self.stop_event.is_set():
                        break
                    self.log(f"Starting scan / Начало сканирования: {p}", 'header')
                    try:
                        found = self.auditor.scan_folder(
                            p,
                            stop_flag_ref=lambda: self.stop_event.is_set(),
                            pause_flag_ref=lambda: self.pause_event.is_set(),
                            log_callback=self.log,
                            progress_callback=self._update_progress,
                            on_find_callback=on_find,
                        )
                        self.log(f"Scan complete / Завершено сканирование {p}: found / найдено {found}", 'success')
                    except Exception as e:
                        register_error('scan-gui-folder', f'Scan error / Ошибка при сканировании {p}', str(e))
                        self.log(f"Error / Ошибка: {e}", 'error')
            except Exception as e:
                register_error('scan-gui', 'Scan thread error / Ошибка в потоке сканирования', str(e))
                self.log(f"Error / Ошибка: {e}", 'error')
            finally:
                self.lib_queue.put({'kind': 'scan_finished'})

        self.scan_thread = threading.Thread(target=worker, daemon=True)
        self.scan_thread.start()

    def _update_progress(self, current, total):
        try:
            self.lib_queue.put({
                'kind': 'scan_progress',
                'current': int(current),
                'total': int(total),
            })
        except Exception:
            pass

    def _scan_finished(self):
        self._stop_scan_timer()
        self.stop_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED, text=tr('btn_pause'))
        self.pause_event.clear()
        self.status_bar.config(text=tr('status_ready'))
        self.audit_finished_str = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        try:
            if self._scan_start_monotonic > 0:
                self.scan_duration_str = format_elapsed(
                    time.monotonic() - self._scan_start_monotonic)
        except Exception:
            self.scan_duration_str = ""
        try:
            self.progress['value'] = self.progress['maximum'] if self.progress['maximum'] > 0 else 0
        except Exception:
            pass
        if self.auditor:
            self._current_found = len(self.auditor.results)
        self._update_timer_labels()

        stopped = self.stop_event.is_set()
        self.stop_event.clear()

        if self.auditor and self.auditor.results:
            for r in self.auditor.results:
                try:
                    self.tree.insert('', tk.END, values=(
                        safe_decode(r.filename), safe_decode(r.keywords_matched),
                        r.size_human, safe_decode(r.file_owner),
                        safe_decode(r.document_author), r.modified_time, r.disk_letter,
                    ))
                except Exception:
                    pass
            if stopped:
                self.log(f"Scan stopped / Сканирование остановлено. Matches / Найдено: {len(self.auditor.results)}", 'warning')
                if self.scan_duration_str:
                    self.log(f"Elapsed time / Прошло времени: {self.scan_duration_str}", 'warning')
                messagebox.showinfo(
                    tr('msg_stopped_title'),
                    tr('msg_stopped', n=len(self.auditor.results),
                       elapsed=self.scan_duration_str or "00:00:00"))
            else:
                self.log(f"Matches found / Найдено совпадений: {len(self.auditor.results)}", 'success')
                if self.scan_duration_str:
                    self.log(f"Elapsed time / Прошло времени: {self.scan_duration_str}", 'success')
                messagebox.showinfo(
                    tr('msg_done_title'),
                    tr('msg_done_scan', n=len(self.auditor.results),
                       elapsed=self.scan_duration_str or "00:00:00"))
        else:
            if stopped:
                self.log("Scan stopped / Сканирование остановлено", 'warning')
                if self.scan_duration_str:
                    self.log(f"Elapsed time / Прошло времени: {self.scan_duration_str}", 'warning')
                messagebox.showinfo(
                    tr('msg_stopped_title'),
                    tr('msg_stopped', n=0,
                       elapsed=self.scan_duration_str or "00:00:00"))
            else:
                self.log("No matches / Совпадений не найдено", 'warning')
                if self.scan_duration_str:
                    self.log(f"Elapsed time / Прошло времени: {self.scan_duration_str}", 'success')
                messagebox.showinfo(
                    tr('msg_done_title'),
                    tr('msg_done_no_matches',
                       elapsed=self.scan_duration_str or "00:00:00"))

        self.scan_thread = None

    def stop_scan(self):
        if not self.stop_event.is_set():
            self.stop_event.set()
        self.pause_event.clear()
        self.stop_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED, text=tr('btn_pause'))
        self.log("Stop requested / Запрошена остановка сканирования...", 'warning')
        lang = SETTINGS.get('ui_language', 'ru')
        self.status_bar.config(
            text="Stopping... / Остановка сканирования..."
            if lang == 'en' else "Остановка сканирования...")

        def _watchdog():
            try:
                t = self.scan_thread
                if t and t.is_alive():
                    t.join(timeout=15.0)
                    if t.is_alive():
                        self.log("Scan thread did not finish in 15s; forcing UI finish. / "
                                 "Поток сканирования не завершился за 15с; принудительное завершение UI.",
                                 'warning')
                        try:
                            self.lib_queue.put({'kind': 'scan_finished'})
                        except Exception:
                            pass
            except Exception:
                pass

        try:
            threading.Thread(target=_watchdog, daemon=True).start()
        except Exception:
            pass

    def toggle_pause(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.pause_btn.config(text=tr('btn_pause'))
            self.log("Scan resumed / Сканирование продолжено", 'info')
        else:
            self.pause_event.set()
            self.pause_btn.config(text=tr('btn_resume'))
            self.log("Scan paused. Press Resume to continue. / Сканирование приостановлено. Нажмите «Продолжить» для возобновления.", 'warning')
            self.status_bar.config(text="PAUSE / ПАУЗА")

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def export(self, fmt):
        if fmt != 'txt':
            return
        if not self.auditor or not self.auditor.results:
            messagebox.showwarning("Export / Экспорт", tr('msg_no_results'))
            return
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"audit_{ts}.txt"
        filepath = filedialog.asksaveasfilename(
            title=tr('msg_save_title'), initialdir=str(DEFAULT_REPORTS_DIR),
            initialfile=default_name, filetypes=[("TXT", "*.txt")])
        if not filepath:
            return
        if self.auditor.save_report_txt(filepath, scan_targets=self._scan_targets,
                                         scan_duration=self.scan_duration_str):
            messagebox.showinfo("Export / Экспорт", tr('msg_saved', path=filepath))
        else:
            messagebox.showerror("Export / Экспорт", tr('msg_save_error'))

    def export_word(self):
        if not self.auditor or not self.auditor.results:
            messagebox.showwarning("Export WORD / Экспорт WORD", tr('msg_no_results_word'))
            return
        dlg = OfficerInfoDialog(self.root)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"audit_report_{ts}.docx"
        filepath = filedialog.asksaveasfilename(
            title=tr('msg_save_word_title'),
            initialdir=str(DEFAULT_REPORTS_DIR),
            initialfile=default_name,
            filetypes=[("Word Document", "*.docx")])
        if not filepath:
            return
        self.status_bar.config(text="Generating Word report... / Формирование Word-отчёта…")
        self.root.update_idletasks()
        try:
            ok = save_docx_report(
                Path(filepath),
                self.auditor.results,
                self.auditor.disk_info_list,
                officer_info=dlg.result,
                audit_started=self.audit_started_str,
                audit_finished=self.audit_finished_str or datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                scan_targets=self._scan_targets,
                scan_duration=self.scan_duration_str,
            )
            if ok:
                messagebox.showinfo("Export WORD / Экспорт WORD", tr('msg_saved_word', path=filepath))
            else:
                messagebox.showerror("Export WORD / Экспорт WORD", tr('msg_save_word_error'))
        finally:
            self.status_bar.config(text=tr('status_ready'))

    # ------------------------------------------------------------------
    # File details
    # ------------------------------------------------------------------
    def show_file_details(self, event):
        sel = self.tree.selection()
        if not sel or not self.auditor:
            return
        idx = self.tree.index(sel[0])
        if 0 <= idx < len(self.auditor.results):
            r = self.auditor.results[idx]
            lang = SETTINGS.get('ui_language', 'ru')
            if lang == 'en':
                details = (
                    f"Name: {safe_decode(r.filename)}\n"
                    f"Path: {safe_decode(r.path)}\n"
                    f"Extension: {safe_decode(r.extension)}\n"
                    f"Size: {r.size:,} bytes ({r.size_human})\n\n"
                    f"[Dates]\n  Created: {r.created_time}\n  Modified: {r.modified_time}\n"
                    f"  Accessed: {r.accessed_time}\n\n"
                    f"[Creator & Owner]\n"
                    f"  File creator: {safe_decode(getattr(r, 'creator', '') or 'Not specified')}\n"
                    f"  File owner: {safe_decode(r.file_owner)}\n"
                    f"  Document author: {safe_decode(r.document_author)}\n"
                    f"  Last saved by: {safe_decode(r.last_saved_by)}\n"
                    f"  Scanning computer: {safe_decode(r.computer_name)}\n\n"
                    f"[Attributes]\n  Read-only: {'Yes' if r.is_readonly else 'No'}\n"
                    f"  Hidden: {'Yes' if r.is_hidden else 'No'}\n"
                    f"  System: {'Yes' if r.is_system else 'No'}\n"
                    f"  Archive: {'Yes' if r.is_archive else 'No'}\n\n"
                    f"[Media]\n  Disk letter: {r.disk_letter}\n"
                    f"  Model: {safe_decode(r.disk_model)}\n"
                    f"  Serial: {safe_decode(r.disk_serial)}\n"
                )
            else:
                details = (
                    f"Имя: {safe_decode(r.filename)}\n"
                    f"Путь: {safe_decode(r.path)}\n"
                    f"Расширение: {safe_decode(r.extension)}\n"
                    f"Размер: {r.size:,} байт ({r.size_human})\n\n"
                    f"[Даты]\n  Создан: {r.created_time}\n  Изменён: {r.modified_time}\n"
                    f"  Открыт: {r.accessed_time}\n\n"
                    f"[Создатель и владелец]\n"
                    f"  Создатель файла: {safe_decode(getattr(r, 'creator', '') or 'Не указан')}\n"
                    f"  Владелец файла: {safe_decode(r.file_owner)}\n"
                    f"  Автор документа: {safe_decode(r.document_author)}\n"
                    f"  Кем изменён: {safe_decode(r.last_saved_by)}\n"
                    f"  Компьютер сканирующий: {safe_decode(r.computer_name)}\n\n"
                    f"[Атрибуты]\n  Только чтение: {'Да' if r.is_readonly else 'Нет'}\n"
                    f"  Скрытый: {'Да' if r.is_hidden else 'Нет'}\n"
                    f"  Системный: {'Да' if r.is_system else 'Нет'}\n"
                    f"  Архивный: {'Да' if r.is_archive else 'Нет'}\n\n"
                    f"[Носитель]\n  Буква диска: {r.disk_letter}\n"
                    f"  Модель: {safe_decode(r.disk_model)}\n"
                    f"  Серийный номер: {safe_decode(r.disk_serial)}\n"
                )
            if r.drive_full_info:
                details += f"\n[Media characteristics / Характеристики носителя]\n{r.drive_full_info}\n"
            details += (
                f"\n[Keywords / Ключевые слова]\n  {safe_decode(r.keywords_matched)}\n\n"
                f"[Preview / Предпросмотр]\n  {safe_decode(r.content_preview)[:500]}"
            )
            ext_low = (r.extension or '').lower()
            if ext_low in MAIL_EXTS:
                marker = "[Attributes]" if lang == 'en' else "[Атрибуты]"
                details = details.replace(
                    marker,
                    (f"[Mail message]\n"
                     f"  Sent by: {safe_decode(getattr(r, 'email_from', '') or 'Not specified')}\n"
                     f"  Recipient: {safe_decode(getattr(r, 'email_to', '') or 'Not specified')}\n\n"
                     if lang == 'en' else
                     f"[Почтовое сообщение]\n"
                     f"  Кто отправил письмо: {safe_decode(getattr(r, 'email_from', '') or 'Не указано')}\n"
                     f"  Кому отправлено письмо: {safe_decode(getattr(r, 'email_to', '') or 'Не указано')}\n\n")
                    + marker
                )
            win = tk.Toplevel(self.root)
            win.title(f"Details / Детали: {safe_decode(r.filename)}")
            win.geometry("900x650")
            win.minsize(600, 450)
            win.resizable(True, True)
            txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Consolas", 10))
            txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            txt.insert(tk.END, details)
            txt.config(state=tk.NORMAL)
            add_copy_context_menu(txt, self.root)
            btn = tk.Frame(win)
            btn.pack(fill=tk.X, pady=5)
            tk.Button(btn, text=tr('btn_copy_all'), width=18, bg="#3949ab", fg="white",
                      command=lambda: (txt.clipboard_clear(),
                                       txt.clipboard_append(txt.get("1.0", tk.END)))).pack(side=tk.LEFT, padx=5)
            tk.Button(btn, text=tr('btn_close'), width=14, bg="#c62828", fg="white",
                      command=win.destroy).pack(side=tk.RIGHT, padx=5)

    # ------------------------------------------------------------------
    # Keywords
    # ------------------------------------------------------------------
    def show_keywords(self):
        win = tk.Toplevel(self.root)
        win.title(tr('msg_keywords_title'))
        win.geometry("600x600")
        win.minsize(400, 350)
        win.resizable(True, True)
        tk.Label(win, text=f"Keywords / Ключевые слова ({len(KEYWORDS)}) из {KEYWORDS_FILE}",
                 font=("Arial", 11, "bold")).pack(pady=5)
        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Consolas", 10))
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        txt.insert(tk.END, "\n".join(KEYWORDS))
        txt.config(state=tk.DISABLED)
        add_copy_context_menu(txt, self.root)

    def edit_keywords(self):
        try:
            if sys.platform == 'win32':
                os.startfile(str(KEYWORDS_FILE))
            else:
                subprocess.run(['xdg-open', str(KEYWORDS_FILE)])
        except Exception as e:
            register_error('keywords', 'Failed to open keywords.txt / Не удалось открыть keywords.txt', str(e))
            messagebox.showerror("Error / Ошибка", tr('msg_keywords_open_error', e=e))

    def reload_keywords(self):
        global KEYWORDS
        KEYWORDS = load_keywords_from_file(KEYWORDS_FILE)
        self._fill_keywords()
        messagebox.showinfo(tr('msg_keywords_title'), tr('msg_keywords_reloaded', n=len(KEYWORDS)))

    # ------------------------------------------------------------------
    # Errors window
    # ------------------------------------------------------------------
    def show_errors(self):
        win = tk.Toplevel(self.root)
        win.title(tr('msg_errors_title'))
        win.geometry("1000x700")
        win.minsize(700, 450)
        win.resizable(True, True)
        top = tk.Frame(win, bg="#c62828", height=40)
        top.pack(fill=tk.X)
        top.pack_propagate(False)
        tk.Label(top, text=tr('msg_errors_header'), font=("Arial", 12, "bold"),
                 fg="white", bg="#c62828").pack(pady=8)

        with ERROR_BUFFER_LOCK:
            n = len(ERROR_BUFFER)
        tk.Label(win, text=tr('msg_errors_total', n=n), font=("Arial", 10, "bold")).pack(pady=3)

        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Consolas", 9))
        txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        txt.tag_config('ts', foreground='#555555')
        txt.tag_config('stage', foreground='#c62828', font=("Consolas", 9, "bold"))
        txt.tag_config('msg', foreground='#000000')
        txt.tag_config('details', foreground='#0d47a1')
        add_copy_context_menu(txt, self.root)

        def _sanitize(s):
            try:
                s = safe_decode(s)
                return s.replace('\ufffd', '?')
            except Exception:
                return str(s)

        with ERROR_BUFFER_LOCK:
            entries = list(ERROR_BUFFER)
        if not entries:
            txt.insert(tk.END, tr('msg_errors_none'), 'msg')
        else:
            for e in entries:
                txt.insert(tk.END, f"[{_sanitize(e['time'])}] ", 'ts')
                txt.insert(tk.END, f"[{_sanitize(e['stage'])}] ", 'stage')
                txt.insert(tk.END, f"{_sanitize(e['message'])}\n", 'msg')
                if e['details']:
                    txt.insert(tk.END, f"    {_sanitize(e['details'])}\n", 'details')
                txt.insert(tk.END, "-" * 90 + "\n", 'ts')
        txt.config(state=tk.DISABLED)

        btn_frame = tk.Frame(win)
        btn_frame.pack(fill=tk.X, pady=5)

        def save_errors():
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            path = filedialog.asksaveasfilename(
                title=tr('msg_errors_save_title'), initialdir=str(DEFAULT_REPORTS_DIR),
                initialfile=f"errors_{ts}.txt", filetypes=[("Text", "*.txt")])
            if not path:
                return
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    for e in entries:
                        f.write(f"[{e['time']}] [{e['stage']}] {e['message']}\n")
                        if e['details']:
                            f.write(f"    {e['details']}\n")
                        f.write("-" * 90 + "\n")
                messagebox.showinfo(tr('msg_errors_title'), tr('msg_errors_saved', path=path))
            except Exception as ex:
                messagebox.showerror(tr('msg_errors_title'), tr('msg_errors_save_error', ex=ex))

        def clear_errors():
            if messagebox.askyesno(tr('msg_errors_title'), tr('msg_errors_clear_confirm')):
                with ERROR_BUFFER_LOCK:
                    ERROR_BUFFER.clear()
                win.destroy()
                self.show_errors()

        tk.Button(btn_frame, text=tr('btn_save_to_file'), width=20, bg="#3949ab", fg="white",
                  command=save_errors).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=tr('btn_clear'), width=15, bg="#ef6c00", fg="white",
                  command=clear_errors).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=tr('btn_close'), width=15, bg="#c62828", fg="white",
                  command=win.destroy).pack(side=tk.RIGHT, padx=5)

    # ------------------------------------------------------------------
    # Reinstall libraries
    # ------------------------------------------------------------------
    def reinstall_libraries(self):
        if not messagebox.askyesno(tr('msg_reinstall_libs_title'), tr('msg_reinstall_libs_confirm')):
            return
        self.lib_log.delete("1.0", tk.END)
        try:
            _ensure_libs_importable()
        except Exception:
            pass
        self._start_background_library_install()
        self.notebook.select(self.tab_libs)

    # ------------------------------------------------------------------
    # Checkpoint management
    # ------------------------------------------------------------------
    def reset_checkpoint_dialog(self):
        info = get_checkpoint_info()
        if info is None:
            messagebox.showinfo(
                tr('msg_checkpoint_title'),
                tr('msg_checkpoint_not_found')
            )
            return

        lang = SETTINGS.get('ui_language', 'ru')
        if lang == 'en':
            detail_text = (
                f"Checkpoint file: {CHECKPOINT_FILE}\n\n"
                f"Targets: {', '.join(info['targets']) or '—'}\n"
                f"Processed files: {info['processed_count']}\n"
                f"Results saved: {info['results_count']}\n"
                f"Total files: {info['total_files']}\n"
                f"Started at: {info['started_at'] or '—'}\n"
                f"Saved at: {info['saved_at'] or '—'}"
            )
            confirm_msg = f"Reset checkpoint?\n\n{detail_text}"
        else:
            detail_text = (
                f"Файл чекпоинта: {CHECKPOINT_FILE}\n\n"
                f"Цели: {', '.join(info['targets']) or '—'}\n"
                f"Обработано файлов: {info['processed_count']}\n"
                f"Сохранено результатов: {info['results_count']}\n"
                f"Всего файлов: {info['total_files']}\n"
                f"Начат: {info['started_at'] or '—'}\n"
                f"Сохранён: {info['saved_at'] or '—'}"
            )
            confirm_msg = f"Сбросить чекпоинт?\n\n{detail_text}"

        if not messagebox.askyesno(tr('msg_checkpoint_title'), confirm_msg):
            return

        if reset_checkpoint():
            self.log("Checkpoint reset / Чекпоинт сброшен", 'success')
            messagebox.showinfo(tr('msg_checkpoint_title'), tr('msg_checkpoint_reset_ok'))
        else:
            messagebox.showerror(tr('msg_checkpoint_title'), tr('msg_checkpoint_reset_error'))

    def show_checkpoint_info(self):
        info = get_checkpoint_info()
        if info is None:
            messagebox.showinfo(
                tr('msg_checkpoint_title'),
                tr('msg_checkpoint_not_found')
            )
            return

        win = tk.Toplevel(self.root)
        win.title(tr('msg_checkpoint_title'))
        win.geometry("700x500")
        win.minsize(500, 350)
        win.resizable(True, True)

        top = tk.Frame(win, bg="#1a237e", height=40)
        top.pack(fill=tk.X)
        top.pack_propagate(False)
        tk.Label(top, text=tr('msg_checkpoint_title'), font=("Arial", 12, "bold"),
                 fg="white", bg="#1a237e").pack(pady=8)

        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Consolas", 10))
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        lang = SETTINGS.get('ui_language', 'ru')
        if lang == 'en':
            lines = [
                f"Checkpoint file: {CHECKPOINT_FILE}",
                f"File exists: {'Yes' if CHECKPOINT_FILE.exists() else 'No'}",
                f"Version: {info['version'] or '—'}",
                "",
                f"Targets: {', '.join(info['targets']) or '—'}",
                f"Processed files: {info['processed_count']}",
                f"Results saved: {info['results_count']}",
                f"Total files: {info['total_files']}",
                f"Started at: {info['started_at'] or '—'}",
                f"Saved at: {info['saved_at'] or '—'}",
            ]
        else:
            lines = [
                f"Файл чекпоинта: {CHECKPOINT_FILE}",
                f"Файл существует: {'Да' if CHECKPOINT_FILE.exists() else 'Нет'}",
                f"Версия: {info['version'] or '—'}",
                "",
                f"Цели: {', '.join(info['targets']) or '—'}",
                f"Обработано файлов: {info['processed_count']}",
                f"Сохранено результатов: {info['results_count']}",
                f"Всего файлов: {info['total_files']}",
                f"Начат: {info['started_at'] or '—'}",
                f"Сохранён: {info['saved_at'] or '—'}",
            ]
        txt.insert(tk.END, "\n".join(lines))
        txt.config(state=tk.DISABLED)
        add_copy_context_menu(txt, self.root)

        btn_frame = tk.Frame(win)
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text=tr('btn_reset_checkpoint'), width=20,
                  bg="#c62828", fg="white",
                  command=lambda: (win.destroy(), self.reset_checkpoint_dialog())).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text=tr('btn_close'), width=15, bg="#3949ab", fg="white",
                  command=win.destroy).pack(side=tk.RIGHT, padx=5)

    # ------------------------------------------------------------------
    # About dialog
    # ------------------------------------------------------------------
    def show_about(self):
        lang = SETTINGS.get('ui_language', 'ru')
        if lang == 'en':
            text = (
                f"{PROGRAM_NAME} v{VERSION}\n\n"
                f"Author: {AUTHOR}\n"
                f"License: {LICENSE}\n"
                f"GitHub: {GITHUB}\n\n"
                f"Features:\n"
                f"• GUI starts immediately, libraries install in background\n"
                f"• Bilingual UI: Russian / English (button on Scan tab)\n"
                f"• Smart installation: scans all subfolders and libs/\n"
                f"• Multithreaded library installation (up to 8 threads)\n"
                f"• Fallback analogues when install fails\n"
                f"• OCR: EasyOCR + Tesseract (runs automatically)\n"
                f"• Names-only scan mode (fast: checks file names only)\n"
                f"• All images, documents, archives (recursive)\n"
                f"• CAD: AutoCAD (DWG/DXF), KOMPAS, GrandSmeta, MacroMine, Civil 3D\n"
                f"• Mail (.eml, .msg, .mbox): sender, recipients, attachments\n"
                f"• Forensics: pytsk3, pyewf, pyvmdk, dissect, volatility3\n"
                f"• Registry: python-registry, regipy\n"
                f"• USB: pyusb, usbinfo, usb_parser, usbescape\n"
                f"• EXIF: exifread; stegano: Stegano; PE: pefile; MIME: python-magic\n"
                f"• PDF-deep: peepdf, pdfid, pdfminer.six\n"
                f"• Media characteristics (USB/HDD/SSD/flash) in reports\n"
                f"• Copy from any window (Ctrl+C, Ctrl+A, RMB)\n"
                f"• Sound on find — 'pig squeal' (toggle button on Scan tab)\n"
                f"• Fixed encoding issues (UTF-16LE, PowerShell, WMI)\n"
                f"• All windows resizable (vertical and horizontal separately)\n"
                f"• Sort by clicking any column header\n"
                f"• Export TXT and WORD reports\n"
                f"• Clickable paths in Word report (mapped drives → UNC)\n"
                f"• Pause / Resume during scan\n"
                f"• Resume after power failure (checkpoints)\n"
                f"• Checkpoint reset from Tools menu\n"
                f"• Aggregated conclusions in all reports (no duplication)\n"
                f"• Error log window\n"
                f"• Scan timer (elapsed time above progress bar)\n"
            )
            title = "About"
        else:
            text = (
                f"{PROGRAM_NAME} v{VERSION}\n\n"
                f"Автор: {AUTHOR}\n"
                f"Лицензия: {LICENSE}\n"
                f"GitHub: {GITHUB}\n\n"
                f"Возможности:\n"
                f"• GUI стартует сразу, библиотеки ставятся в фоне\n"
                f"• Двуязычный интерфейс: русский / английский (кнопка на вкладке Сканирование)\n"
                f"• Умная установка: проверка всех подпапок и libs/\n"
                f"• Многопоточная установка библиотек (до 8 потоков)\n"
                f"• Fallback-аналоги при неудаче установки\n"
                f"• OCR: EasyOCR + Tesseract (работает автоматически)\n"
                f"• Режим «только имена» (быстро: проверка только имён файлов)\n"
                f"• Все изображения, документы, архивы (рекурсивно)\n"
                f"• CAD: AutoCAD (DWG/DXF), КОМПАС, ГрандСмета, MacroMine, Civil 3D\n"
                f"• Почта (.eml, .msg, .mbox): отправитель, получатели, вложения\n"
                f"• Форезика: pytsk3, pyewf, pyvmdk, dissect, volatility3\n"
                f"• Реестр: python-registry, regipy\n"
                f"• USB: pyusb, usbinfo, usb_parser, usbescape\n"
                f"• EXIF: exifread; стегано: Stegano; PE: pefile; MIME: python-magic\n"
                f"• PDF-deep: peepdf, pdfid, pdfminer.six\n"
                f"• Характеристики носителя (USB/HDD/SSD/флешка) в отчётах\n"
                f"• Копирование из любых окон (Ctrl+C, Ctrl+A, ПКМ)\n"
                f"• Звук при находке — «поросячий визг» (кнопка на вкладке Сканирование)\n"
                f"• Исправлены кракозябры (UTF-16LE, PowerShell, WMI)\n"
                f"• Все окна можно менять в размере (вертикаль и горизонталь отдельно)\n"
                f"• Сортировка по клику на заголовок столбца\n"
                f"• Экспорт TXT и WORD\n"
                f"• Кликабельные пути в Word-отчёте (мапленные диски → UNC)\n"
                f"• Пауза / Продолжить во время сканирования\n"
                f"• Возобновление после сбоя питания (чекпоинты)\n"
                f"• Сброс чекпоинта из меню «Инструменты»\n"
                f"• Обобщённые выводы во всех отчётах (без дублирования)\n"
                f"• Окно ошибок\n"
                f"• Секундомер сканирования (время над прогресс-баром)\n"
            )
            title = "О программе"
        messagebox.showinfo(title, text)

# ======================================================================
# CLI
# ======================================================================
def show_menu_cli():
    print_header("MAIN MENU / ГЛАВНОЕ МЕНЮ")
    print_color(" [1] Scan folder / Сканировать папку", Fore.GREEN)
    print_color(" [2] Scan USB drives / Сканировать USB диски", Fore.GREEN)
    print_color(" [3] Scan local + USB HDD/SSD / Сканировать локальные + USB HDD/SSD", Fore.YELLOW)
    print_color(" [4] Scan all drives / Сканировать все диски", Fore.YELLOW)
    print_color(" [5] Libraries status / Статус библиотек", Fore.MAGENTA)
    print_color(" [6] Show keywords / Показать ключевые слова", Fore.CYAN)
    print_color(" [7] Reload keywords / Перезагрузить ключевые слова", Fore.CYAN)
    print_color(" [8] Edit keywords / Редактировать ключевые слова", Fore.CYAN)
    print_color(" [9] About / О программе", Fore.BLUE)
    print_color(" [10] Show errors / Показать ошибки", Fore.RED)
    print_color(" [11] Reset checkpoint / Сбросить чекпоинт", Fore.MAGENTA)
    print_color(" [0] Exit / Выход", Fore.RED)
    print_line('=', 50)

def save_prompt_cli(auditor, scan_targets=None, scan_duration=""):
    if not auditor.results:
        print_warning("No results to save / Нет результатов для сохранения")
        return
    custom = input(f"  Path / Путь (Enter - {DEFAULT_REPORTS_DIR}): ").strip()
    target = Path(custom).expanduser().resolve() if custom else DEFAULT_REPORTS_DIR
    if not target.exists():
        try:
            target.mkdir(parents=True, exist_ok=True)
        except Exception:
            target = DEFAULT_REPORTS_DIR
    fmt = input("\nReport format / Формат отчёта (txt/word/none/нет): ").strip().lower()
    if fmt == 'txt':
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        full = target / f"audit_{ts}.txt"
        if auditor.save_report_txt(full, scan_targets=scan_targets, scan_duration=scan_duration):
            print_success(f"Report saved / Отчёт сохранён: {full}")
    elif fmt in ('word', 'docx'):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        full = target / f"audit_report_{ts}.docx"
        if save_docx_report(full, auditor.results, auditor.disk_info_list,
                             scan_targets=scan_targets, scan_duration=scan_duration):
            print_success(f"Word report saved / Word-отчёт сохранён: {full}")

def run_cli():
    global KEYWORDS
    print_banner()
    while True:
        show_menu_cli()
        ch = input(f"\n{Fore.YELLOW}Choice / Выбор{Style.RESET_ALL}: ").strip()
        if ch == '0':
            break
        elif ch == '1':
            folder = input(f"\n{Fore.CYAN}Folder path / Путь к папке: {Style.RESET_ALL}").strip().strip('"')
            if not folder:
                continue
            folder = normalize_network_path(folder)
            path = Path(folder)
            if not path.exists():
                print_error("Path does not exist / Путь не существует")
                continue
            a = FileAuditorPro()
            _t0 = time.monotonic()
            a.scan_folder(path, lambda: stop_scan)
            _dur = format_elapsed(time.monotonic() - _t0)
            print_success(f"Elapsed / Прошло: {_dur}")
            save_prompt_cli(a, scan_targets=[str(path)], scan_duration=_dur)
        elif ch == '2':
            for d in get_usb_drives():
                a = FileAuditorPro()
                _t0 = time.monotonic()
                a.scan_folder(Path(d), lambda: stop_scan)
                _dur = format_elapsed(time.monotonic() - _t0)
                print_success(f"Elapsed / Прошло: {_dur}")
                save_prompt_cli(a, scan_targets=[d], scan_duration=_dur)
        elif ch == '3':
            for d in get_local_fixed_drives():
                a = FileAuditorPro()
                _t0 = time.monotonic()
                a.scan_folder(Path(d), lambda: stop_scan)
                _dur = format_elapsed(time.monotonic() - _t0)
                print_success(f"Elapsed / Прошло: {_dur}")
                save_prompt_cli(a, scan_targets=[d], scan_duration=_dur)
        elif ch == '4':
            for d in get_all_data_drives():
                a = FileAuditorPro()
                _t0 = time.monotonic()
                a.scan_folder(Path(d), lambda: stop_scan)
                _dur = format_elapsed(time.monotonic() - _t0)
                print_success(f"Elapsed / Прошло: {_dur}")
                save_prompt_cli(a, scan_targets=[d], scan_duration=_dur)
        elif ch == '5':
            total = len(ALL_LIBRARIES)
            installed = sum(1 for s in LIBRARY_STATUS.values() if s)
            print_success(f"Total / Всего: {total} | Installed / Установлено: {installed} | Missing / Отсутствует: {total - installed}")
            print_info(f"OCR: EasyOCR={'YES/ДА' if LIBRARY_STATUS.get('easyocr') else 'NO/НЕТ'} | "
                       f"Tesseract={'YES/ДА' if HAS_TESSERACT else 'NO/НЕТ'} | "
                       f"Enabled / Включён={'YES/ДА' if SETTINGS.get('ocr_enabled', True) else 'NO/НЕТ'}")
            if TESSERACT_EXE:
                print_info(f"Tesseract.exe: {TESSERACT_EXE}")
            missing = [(lid, info) for lid, info in ALL_LIBRARIES.items()
                       if not LIBRARY_STATUS.get(lid, False)]
            if missing:
                print_warning("Missing (need to download) / Отсутствуют (нужно скачать):")
                for lid, info in missing:
                    print_color(f"    - {info['name']:<24} <- pip install {info['pip']}", Fore.RED)
        elif ch == '6':
            show_keywords_cli()
        elif ch == '7':
            KEYWORDS = load_keywords_from_file(KEYWORDS_FILE)
            print_success(f"Reloaded / Перезагружено: {len(KEYWORDS)} keywords")
        elif ch == '8':
            try:
                if sys.platform == 'win32':
                    os.startfile(str(KEYWORDS_FILE))
                else:
                    subprocess.run(['xdg-open', str(KEYWORDS_FILE)])
            except Exception:
                pass
        elif ch == '9':
            show_about_cli()
        elif ch == '10':
            show_errors_cli()
        elif ch == '11':
            reset_checkpoint_cli()
        input("\nEnter...")

def reset_checkpoint_cli():
    print_header("CHECKPOINT RESET / СБРОС ЧЕКПОИНТА")
    info = get_checkpoint_info()
    if info is None:
        print_warning("Checkpoint not found / Чекпоинт не найден")
        return
    print_info(f"Checkpoint file / Файл чекпоинта: {CHECKPOINT_FILE}")
    print_info(f"Targets / Цели: {', '.join(info['targets']) or '—'}")
    print_info(f"Processed / Обработано: {info['processed_count']}")
    print_info(f"Results / Результатов: {info['results_count']}")
    print_info(f"Total / Всего: {info['total_files']}")
    print_info(f"Started / Начат: {info['started_at'] or '—'}")
    print_info(f"Saved / Сохранён: {info['saved_at'] or '—'}")
    ans = input("\nReset checkpoint? (y/n) / Сбросить чекпоинт? (y/н): ").strip().lower()
    if ans in ('y', 'yes', 'да', 'д'):
        if reset_checkpoint():
            print_success("Checkpoint reset / Чекпоинт сброшен")
        else:
            print_error("Failed to reset checkpoint / Не удалось сбросить чекпоинт")
    else:
        print_info("Cancelled / Отменено")

def show_errors_cli():
    print_header("ERROR LOG / ОКНО ОШИБОК")
    with ERROR_BUFFER_LOCK:
        entries = list(ERROR_BUFFER)
    if not entries:
        print_success("No errors recorded / Ошибок не зафиксировано")
        return
    for e in entries:
        print_color(f"[{e['time']}] [{e['stage']}] {e['message']}", Fore.RED)
        if e['details']:
            print_color(f"    {e['details']}", Fore.CYAN)
        print_line('-', 60)

def show_keywords_cli():
    print_header(f"KEYWORDS / КЛЮЧЕВЫЕ СЛОВА ({len(KEYWORDS)})")
    for i in range(0, len(KEYWORDS), 3):
        print("  " + "  ".join(f"{kw:<25}" for kw in KEYWORDS[i:i + 3]))

def show_about_cli():
    print_header("ABOUT / О ПРОГРАММЕ")
    print_color(f"  {PROGRAM_NAME} v{VERSION}", Fore.YELLOW, Style.BRIGHT)
    print_two_columns("  Author / Автор", AUTHOR, 18)
    print_two_columns("  License / Лицензия", LICENSE, 18)
    print_two_columns("  GitHub", GITHUB[:50], 18)

def run_library_check_console():
    print_header("LIBRARY CHECK (PARALLEL, with fallbacks) / ПРОВЕРКА БИБЛИОТЕК")
    print_info(f"Libs dir / Папка библиотек: {LIBS_DIR}")
    print_info(f"Local modules added / Локальных модулей добавлено в sys.path: {len(_LOCAL_MODULES_ADDED)}")
    print()

    def _log(msg, level='info'):
        if level == 'success':
            print_success(msg)
        elif level == 'error':
            print_error(msg)
        elif level == 'warning':
            print_warning(msg)
        else:
            print_info(msg)

    check_and_install_libraries_parallel(log_cb=_log)
    _ensure_libs_importable()
    refresh_library_flags()

    print_header("SUMMARY / СВОДКА")
    total = len(ALL_LIBRARIES)
    installed = sum(1 for s in LIBRARY_STATUS.values() if s)
    print_success(f"Total / Всего: {total} | Installed / Установлено: {installed} | Missing / Отсутствует: {total - installed}")
    if HAS_TESSERACT:
        print_success(f"Tesseract-OCR found / найден: {TESSERACT_EXE}")
    else:
        print_warning("Tesseract-OCR not found / не найден")

# ======================================================================
# main
# ======================================================================
def main():
    use_cli = '--cli' in sys.argv or '-c' in sys.argv

    if use_cli:
        run_library_check_console()
        print_header("OCR INITIALIZATION / ИНИЦИАЛИЗАЦИЯ OCR")
        if SETTINGS.get('ocr_enabled', True):
            init_ocr()
        else:
            print_info("OCR disabled in settings / OCR отключён в настройках")
        print_header("DISK INFORMATION / ИНФОРМАЦИЯ О ДИСКАХ")
        for i, d in enumerate(get_detailed_disk_info(), 1):
            print_color(f"\n  [{i}] PHYSICAL DISK / ФИЗИЧЕСКИЙ ДИСК", Fore.YELLOW, Style.BRIGHT)
            print_two_columns("    Model / Модель", d.get('model', 'Unknown'), 20)
            print_two_columns("    Size / Размер", d.get('size', 'Unknown'), 20)
        run_cli()
        return

    try:
        if relaunch_as_pythonw():
            return
    except Exception:
        pass

    try:
        def _hide_later():
            try:
                time.sleep(0.3)
                hide_console()
            except Exception:
                pass

        threading.Thread(target=_hide_later, daemon=True).start()

        root = tk.Tk()
        app = FileAuditorGUI(root)
        root.mainloop()
    except Exception as e:
        try:
            show_console()
        except Exception:
            pass
        register_error('gui', 'GUI error, falling back to CLI / Ошибка GUI, переход в CLI', traceback.format_exc())
        print_error(f"GUI error / Ошибка GUI: {e}")
        try:
            run_library_check_console()
            run_cli()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            show_console()
        except Exception:
            pass
        print("\n\nInterrupted / Программа прервана")
    except Exception as e:
        try:
            show_console()
        except Exception:
            pass
        register_error('main', 'Critical error / Критическая ошибка', traceback.format_exc())
        print_error(f"Critical error / Критическая ошибка: {e}")
        traceback.print_exc()