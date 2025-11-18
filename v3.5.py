import sys
import asyncio
import aiohttp
import openpyxl
import re
import datetime
import os
import urllib3
import urllib.parse
import pandas as pd
import string
import logging
import subprocess
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from PIL import Image, UnidentifiedImageError
import requests
from aiohttp import BasicAuth
from openpyxl import Workbook

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QRadioButton, QLineEdit, QLabel, QProgressBar, QFileDialog, QCheckBox,
    QMessageBox, QTabWidget, QGroupBox, QComboBox, QSpinBox, QLayout,
    QScrollArea, QFrame
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap

DARK_STYLE = """
/* ---------- ROOT ---------- */
QWidget {
    background-color: transparent;      /* filhos NÃO recebem fundo sólido */
    color: #E5E7EB;
    font-family: Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 11pt;
}

/* fundo só na janela principal */
QWidget#MainApp {
    background-color: #050816;
}

/* ---------- TABS ---------- */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar { qproperty-drawBase: 0; }
QTabBar::tab {
    background-color: #111827;
    color: #9CA3AF;
    padding: 8px 22px;
    margin: 0 6px;
    border-radius: 18px;
    border: 1px solid transparent;
    font-weight: 500;
}
QTabBar::tab:selected {
    background-color: #7F22FE;
    color: #FFFFFF;
    border-color: #7F22FE;
}
QTabBar::tab:hover:!selected {
    background-color: #1F2937;
    color: #E5E7EB;
}

/* ---------- TITLES ---------- */
QLabel#Title {
    font-size: 18pt;
    font-weight: 600;
    color: #F9FAFB;
}

/* ---------- TEXT INPUTS ---------- */
QLineEdit,
QTextEdit,
QPlainTextEdit {
    background-color: #0B1020;
    color: #E5E7EB;
    border-radius: 16px;
    padding: 8px 12px;
    border: 1px solid #111827;
    selection-background-color: #7F22FE;
    selection-color: #FFFFFF;
}
QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus {
    border: 1px solid #7F22FE;
}

/* ---------- BUTTONS ---------- */
QPushButton {
    background-color: #111827;
    color: #E5E7EB;
    border-radius: 18px;
    padding: 8px 18px;
    border: 1px solid #1F2937;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #1F2937;
}
QPushButton:pressed {
    background-color: #020817;
}
QPushButton[accent="true"],
QPushButton#accent {
    background-color: #7F22FE;
    color: #FFFFFF;
    border: none;
}
QPushButton[accent="true"]:hover,
QPushButton#accent:hover {
    background-color: #9F4CFF;
}

/* ---------- GROUPBOX (padrão leve) ---------- */
QGroupBox {
    border: none;
    margin-top: 12px;
    padding-top: 4px;
    color: #9CA3AF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 0;
    padding: 0 6px;
    color: #9CA3AF;
    background-color: transparent;
    font-weight: 500;
}

/* ---------- CARDS EXPLÍCITOS ---------- */
QWidget#card {
    background-color: #0B1020;
    border-radius: 22px;
    border: 1px solid #111827;
    padding: 16px;
    margin-top: 12px;
}

/* ---------- CHAT BUBBLES ---------- */
QLabel#userBubble {
    background-color: #7F22FE;
    color: #FFFFFF;
    border-radius: 18px;
    padding: 8px 14px;
    margin: 4px 0;
}

QLabel#botBubble {
    background-color: #111827;
    color: #E5E7EB;
    border-radius: 18px;
    padding: 8px 14px;
    margin: 4px 0;
}

QLabel#logBubble {
    background-color: #050816;
    color: #9CA3AF;
    border-radius: 12px;
    padding: 4px 10px;
    margin: 2px 0;
    font-size: 9pt;
}

/* pill status no topo direito */
QLabel#chatStatusPill {
    background-color: #7F22FE;
    color: #FFFFFF;
    border-radius: 18px;
    padding: 6px 16px;
    font-weight: 500;
}


/* ---------- CHECKBOX / RADIO (ajuste sem faixas) ---------- */
QCheckBox,
QRadioButton {
    color: #E5E7EB;
    spacing: 8px;
    background: transparent;       /* remove faixa */
}

QCheckBox::indicator,
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #4B5563;
    background-color: #0B1020;     /* fundo neutro */
}

QCheckBox::indicator:checked,
QRadioButton::indicator:checked {
    background-color: #7F22FE;
    border-color: #7F22FE;
}

QCheckBox::indicator:hover,
QRadioButton::indicator:hover {
    border-color: #9F4CFF;
}


/* ---------- COMBOBOX (Dropdown) ---------- */
QComboBox {
    background-color: #0B1020;
    color: #E5E7EB;
    border-radius: 16px;
    padding: 6px 12px;
    border: 1px solid #111827;
}
QComboBox:focus {
    border: 1px solid #7F22FE;
}
QComboBox::drop-down {
    width: 22px;
    border: none;
}
QComboBox::down-arrow {
    image: none;
    border: none;
    width: 0;
    height: 0;
    margin-right: 6px;
    /* triângulo minimalista */
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid #9CA3AF;
}
QComboBox QAbstractItemView {
    background-color: #050816;
    border: 1px solid #111827;
    selection-background-color: #7F22FE;
    selection-color: #FFFFFF;
}

/* ---------- SPINBOX (Quality, etc.) ---------- */
QSpinBox {
    background-color: #0B1020;
    color: #E5E7EB;
    border-radius: 16px;
    border: 1px solid #111827;
    padding-left: 10px;
    padding-right: 26px;  /* espaço pros botões up/down */
}

QSpinBox:focus {
    border: 1px solid #7F22FE;
}

/* botões up/down minimalistas */
QSpinBox::up-button,
QSpinBox::down-button {
    subcontrol-origin: border;
    width: 14px;
    border: none;
    background: transparent;
    margin-right: 6px;
}

QSpinBox::up-button {
    subcontrol-position: right top;
}
QSpinBox::down-button {
    subcontrol-position: right bottom;
}

/* desenha setinhas simples */
QSpinBox::up-arrow,
QSpinBox::down-arrow {
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
}

QSpinBox::up-arrow {
    border-bottom: 6px solid #9CA3AF;
}
QSpinBox::down-arrow {
    border-top: 6px solid #9CA3AF;
}

QSpinBox::up-button:hover,
QSpinBox::down-button:hover {
    background-color: #111827;
}

/* ---------- PROGRESS BAR ---------- */
QProgressBar {
    background-color: #050816;
    border-radius: 12px;
    border: 1px solid #111827;
    text-align: center;
    color: #9CA3AF;
    padding: 2px;
}
QProgressBar::chunk {
    background-color: #7F22FE;
    border-radius: 10px;
}

/* ---------- SCROLLBARS ---------- */
QScrollBar:vertical,
QScrollBar:horizontal {
    background: transparent;
    border: none;
    margin: 4px;
}
QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background: #111827;
    border-radius: 8px;
    min-height: 24px;
    min-width: 24px;
}
QScrollBar::handle:hover {
    background: #1F2937;
}
QScrollBar::add-line,
QScrollBar::sub-line {
    height: 0;
    width: 0;
    background: transparent;
    border: none;
}

/* ---------- TOOLTIP ---------- */
QToolTip {
    background-color: #111827;
    color: #E5E7EB;
    border-radius: 8px;
    padding: 6px 10px;
    border: 1px solid #7F22FE;
}
"""


# Disable insecure request warnings (e.g., for SSL verification)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --------------------- CONSTANTS ---------------------
MAX_EXCEL_CELL_LENGTH = 32767
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# --------------------- Helper Functions ---------------------
def sanitize_filename(filename):
    """Sanitize the filename by removing invalid characters."""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    clean_name = ''.join(c for c in filename if c in valid_chars)
    return clean_name if clean_name else "unnamed_file"

# --------------------- Web Crawler Classes (No Changes) ---------------------
class CrawlerThread(QThread):
    """
    A worker thread for crawling websites asynchronously.
    Fetches URLs, extracts specified data, and saves it to Excel files.
    """
    progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, mode, search_input, urls, extract_options, check_errors, output_folder):
        super().__init__()
        self.mode = mode  # 1: Search modules (classes), 2: Search words, 0: No search
        self.search_input = search_input
        self.urls = urls
        self.extract_options = extract_options
        self.check_errors = check_errors
        self.output_folder = output_folder or f"web_crawler_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.output_folder, exist_ok=True)
        self.total_pages_crawled = 0
        self.stopped = False

    def stop(self):
        """Signals the thread to stop processing."""
        self.log_update.emit("Stopping crawler...")
        self.stopped = True

    def run(self):
        """Runs the asynchronous crawling process."""
        try:
            asyncio.run(self.main())
        except Exception as e:
            self.log_update.emit(f"An unexpected error occurred: {e}")

    async def main(self):
        """Main async function to set up and execute crawling tasks."""
        class_patterns = []
        search_patterns = []

        if self.mode == 1 and self.search_input:
            class_patterns = [pattern.strip() for pattern in self.search_input.split(',') if pattern.strip()]
        elif self.mode == 2 and self.search_input:
            search_patterns = self._generate_search_patterns([word.strip() for word in self.search_input.split(',') if word.strip()])

        main_filename = os.path.join(self.output_folder, "results.xlsx")
        error_filename = os.path.join(self.output_folder, "error_results.xlsx") if self.check_errors else None
        content_filename = os.path.join(self.output_folder, "content_results.xlsx") if self.extract_options["content"] else None

        wb_main = openpyxl.Workbook()
        ws_main = wb_main.active
        ws_main.title = "Main Results"
        headers = ["URL"]
        if self.extract_options["title"]: headers.append("Title")
        if self.extract_options["meta_title"]: headers.append("Meta Title")
        if self.extract_options["meta_description"]: headers.append("Meta Description")
        if self.extract_options["content"]: headers.append("Content Snippet")
        if self.extract_options["meta_tags"]: headers.append("Meta Tags")
        if self.mode == 1: headers.append("Module Found")
        elif self.mode == 2: headers.append("Found Words")
        ws_main.append(headers)

        wb_content = openpyxl.Workbook() if content_filename else None
        ws_content = wb_content.active if wb_content else None
        if ws_content:
            ws_content.title = "Content Results"
            ws_content.append(["URL", "Full Content"])

        wb_errors = openpyxl.Workbook() if error_filename else None
        ws_errors = wb_errors.active if wb_errors else None
        if ws_errors:
            ws_errors.title = "Error Results"
            ws_errors.append(["URL", "Status Code", "Redirect"])

        async with aiohttp.ClientSession() as session:
            all_urls_to_check = []
            for url in self.urls:
                if self.stopped: break
                if urlparse(url).path.endswith(".xml"):
                    self.log_update.emit(f"Fetching URLs from sitemap: {url}")
                    sitemap_urls = await self._get_sitemap_urls(url, session)
                    all_urls_to_check.extend(sitemap_urls)
                else:
                    all_urls_to_check.append(url)
            
            total_urls = len(all_urls_to_check)
            self.total_pages_crawled = total_urls
            
            tasks = [self._crawl_url(u, session, class_patterns, search_patterns) for u in all_urls_to_check]
            
            for i, future in enumerate(asyncio.as_completed(tasks)):
                if self.stopped: break
                
                result = await future
                if result:
                    if result['type'] == 'success':
                        ws_main.append(result['main_data'])
                        if ws_content and 'content_data' in result:
                            ws_content.append(result['content_data'])
                    elif result['type'] == 'error' and ws_errors:
                        ws_errors.append(result['error_data'])

                progress = int((i + 1) / total_urls * 100) if total_urls > 0 else 100
                self.progress_update.emit(progress)
                self.log_update.emit(f"Processed {i + 1}/{total_urls} URLs")

        if not self.stopped:
            self.log_update.emit("Saving results to Excel files...")
            wb_main.save(main_filename)
            if wb_content: wb_content.save(content_filename)
            if wb_errors: wb_errors.save(error_filename)
            
            self.log_update.emit(f"Crawling completed. Results saved to {self.output_folder}")
            self.log_update.emit(f"Total pages processed: {self.total_pages_crawled}")
            self.finished.emit(self.output_folder)
        else:
            self.log_update.emit("Crawling stopped by user.")

    def _generate_search_patterns(self, words):
        return [re.compile(re.escape(word), re.IGNORECASE) for word in words]

    async def _get_sitemap_urls(self, sitemap_url, session):
        try:
            async with session.get(sitemap_url, ssl=False) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'lxml-xml')
                    return [loc.text for loc in soup.find_all('loc')]
                else:
                    self.log_update.emit(f"Sitemap fetch failed for {sitemap_url}: Status {response.status}")
                    return []
        except Exception as e:
            self.log_update.emit(f"Error reading sitemap {sitemap_url}: {e}")
            return []

    async def _crawl_url(self, url, session, class_patterns, search_patterns):
        try:
            async with session.get(url, ssl=False, timeout=30) as response:
                if response.status in {403, 404} and self.check_errors:
                    redirect_url = response.headers.get("Location", "N/A")
                    self.log_update.emit(f"Error {response.status} for {url}")
                    return {'type': 'error', 'error_data': [url, response.status, redirect_url]}

                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    result = {'type': 'success'}
                    row_data = [url]
                    
                    if self.extract_options["title"]:
                        row_data.append(soup.title.string.strip() if soup.title and soup.title.string else "No title")
                    if self.extract_options["meta_title"]:
                        meta = soup.find("meta", property="og:title")
                        row_data.append(meta["content"] if meta and meta.get("content") else "No meta title")
                    if self.extract_options["meta_description"]:
                        meta = soup.find("meta", property="og:description")
                        row_data.append(meta["content"] if meta and meta.get("content") else "No meta description")
                    
                    if self.extract_options["content"]:
                        content = soup.get_text(separator=' ', strip=True)
                        snippet = content[:MAX_EXCEL_CELL_LENGTH]
                        row_data.append(snippet)
                        result['content_data'] = [url, content]

                    if self.extract_options["meta_tags"]:
                        tags = [f"{meta.get('name') or meta.get('property')}: {meta.get('content', '')}" 
                                for meta in soup.find_all("meta") if meta.get("name") or meta.get("property")]
                        row_data.append(", ".join(tags))
                        
                    if self.mode == 1:
                        found = any(soup.find("div", class_=cp) for cp in class_patterns)
                        row_data.append("Yes" if found else "No")
                    elif self.mode == 2:
                        text = soup.get_text()
                        found_words = [p.pattern for p in search_patterns if p.search(text)]
                        row_data.append(', '.join(found_words) if found_words else "None")

                    result['main_data'] = row_data
                    return result
                else:
                    self.log_update.emit(f"Non-200 status for {url}: {response.status}")

        except Exception as e:
            self.log_update.emit(f"Failed to process {url}: {e}")
        return None

class BrokenLinkWorker(QThread):
    """
    Worker para 'Broken Link Inspector':
    - mode: 'single' (single page checkup) ou 'sitemap'
    - root_url: URL base (página ou sitemap.xml)
    - same_domain_only: se True, filtra apenas links do mesmo domínio (single page)
    """
    progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)
    finished = pyqtSignal(list)  # lista de resultados

    def __init__(self, mode: str, root_url: str, same_domain_only: bool = True, max_concurrency: int = 10):
        super().__init__()
        self.mode = mode
        self.root_url = root_url.strip()
        self.same_domain_only = same_domain_only
        self.max_concurrency = max_concurrency
        self._stop_requested = False
        self.results = []

    def stop(self):
        self._stop_requested = True

    def run(self):
        try:
            asyncio.run(self.main())
        except Exception as e:
            self.log_update.emit(f"[ERROR] BrokenLinkWorker crashed: {e}")
        finally:
            self.finished.emit(self.results)

    async def main(self):
        self.log_update.emit(f"[INIT] Broken Link Inspector mode = {self.mode}, URL = {self.root_url}")

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            if self.mode == "single":
                urls = await self._collect_links_from_page(self.root_url, session)
            elif self.mode == "sitemap":
                urls = await self._collect_from_sitemap(self.root_url, session)
            else:
                self.log_update.emit(f"[ERROR] Unknown mode: {self.mode}")
                urls = []

            urls = list(dict.fromkeys(urls))  # dedupe preservando ordem
            total = len(urls)
            if total == 0:
                self.log_update.emit("[INFO] No URLs to check.")
                self.progress_update.emit(100)
                return

            self.log_update.emit(f"[INFO] {total} URL(s) to check.")
            sem = asyncio.Semaphore(self.max_concurrency)

            async def runner():
                done = 0
                tasks = [
                    self._check_one(url, session, sem)
                    for url in urls
                ]
                for coro in asyncio.as_completed(tasks):
                    if self._stop_requested:
                        self.log_update.emit("[WARN] Stop requested. Aborting remaining checks.")
                        break
                    result = await coro
                    if result is not None:
                        self.results.append(result)
                    done += 1
                    progress = int(done * 100 / total)
                    self.progress_update.emit(progress)

            await runner()
            self.progress_update.emit(100)
            self.log_update.emit("[DONE] Broken Link Inspector finished.")

    async def _collect_links_from_page(self, page_url: str, session: aiohttp.ClientSession):
        urls = []
        try:
            self.log_update.emit(f"[FETCH] Loading page: {page_url}")
            async with session.get(page_url, ssl=False, timeout=30) as resp:
                html = await resp.text(errors="ignore")
        except Exception as e:
            self.log_update.emit(f"[ERROR] Could not load page: {page_url} – {e}")
            return urls

        base = urlparse(page_url)
        soup = BeautifulSoup(html, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith("javascript:") or href.startswith("#"):
                continue
            full_url = urljoin(page_url, href)
            parsed = urlparse(full_url)
            if parsed.scheme not in ("http", "https"):
                continue
            if self.same_domain_only and parsed.netloc != base.netloc:
                continue
            urls.append(full_url)

        self.log_update.emit(f"[INFO] Found {len(urls)} links on page (after filtering).")
        return urls

    async def _collect_from_sitemap(self, sitemap_url: str, session: aiohttp.ClientSession):
        import xml.etree.ElementTree as ET
        urls = []
        submaps = []

        self.log_update.emit(f"[FETCH] Loading sitemap root: {sitemap_url}")
        xml_root = await self._fetch_xml(sitemap_url, session)
        if not xml_root:
            return urls

        try:
            root = ET.fromstring(xml_root)
        except Exception as e:
            self.log_update.emit(f"[ERROR] Could not parse root sitemap XML: {e}")
            return urls

        root_tag = root.tag.split('}')[-1].lower()

        if root_tag == "sitemapindex":
            self.log_update.emit("[INFO] Root is <sitemapindex> (has sub-sitemaps).")
            for sm_loc in root.iterfind(".//{*}sitemap/{*}loc"):
                if sm_loc.text:
                    sm_url = sm_loc.text.strip()
                    submaps.append(sm_url)

            self.log_update.emit(f"[INFO] Found {len(submaps)} sub-sitemaps.")
            for i, sm in enumerate(submaps, 1):
                if self._stop_requested:
                    break
                self.log_update.emit(f"[FETCH] ({i}/{len(submaps)}) {sm}")
                xml_sub = await self._fetch_xml(sm, session)
                if not xml_sub:
                    continue
                try:
                    r = ET.fromstring(xml_sub)
                    for loc in r.iterfind(".//{*}url/{*}loc"):
                        if loc.text:
                            urls.append(loc.text.strip())
                except Exception as e:
                    self.log_update.emit(f"[PARSE ERROR] Could not parse sub-sitemap {sm}: {e}")

        elif root_tag == "urlset":
            self.log_update.emit("[INFO] Root is <urlset> (single sitemap).")
            for loc in root.iterfind(".//{*}url/{*}loc"):
                if loc.text:
                    urls.append(loc.text.strip())
        else:
            self.log_update.emit(f"[WARN] Unknown sitemap root tag '{root_tag}', using generic <loc>.")
            for loc in root.iterfind(".//{*}loc"):
                if loc.text:
                    urls.append(loc.text.strip())

        self.log_update.emit(f"[INFO] Collected {len(urls)} URL(s) from sitemap.")
        return urls

    async def _fetch_xml(self, url: str, session: aiohttp.ClientSession):
        try:
            async with session.get(url, ssl=False, timeout=30) as r:
                if r.status != 200:
                    self.log_update.emit(f"[ERROR] {url} – status {r.status}")
                    return None
                return await r.text()
        except Exception as e:
            self.log_update.emit(f"[ERROR] {url} – {e}")
            return None

    async def _check_one(self, url: str, session: aiohttp.ClientSession, sem: asyncio.Semaphore):
        async with sem:
            if self._stop_requested:
                return None

            status = None
            final_url = ""
            error = ""

            try:
                # tenta HEAD primeiro, sem seguir redirects
                try:
                    async with session.head(url, ssl=False, allow_redirects=False, timeout=15) as resp:
                        status = resp.status
                        final_url = str(resp.url)

                        # se for redirect, pega destino do Location
                        if 300 <= status < 400:
                            loc = resp.headers.get("Location")
                            if loc:
                                final_url = urljoin(url, loc)

                except Exception:
                    # fallback para GET, também sem seguir redirect
                    async with session.get(url, ssl=False, allow_redirects=False, timeout=30) as resp:
                        status = resp.status
                        final_url = str(resp.url)

                        if 300 <= status < 400:
                            loc = resp.headers.get("Location")
                            if loc:
                                final_url = urljoin(url, loc)

            except Exception as e:
                error = str(e)

            category = "network_error"
            if status is not None:
                if 200 <= status < 300:
                    category = "ok"
                elif 300 <= status < 400:
                    category = "redirect"
                elif 400 <= status < 500:
                    category = "client_error"
                elif status >= 500:
                    category = "server_error"

            return {
                "url": url,
                "status": status,
                "final_url": final_url,
                "error": error,
                "category": category,
            }


class CrawlerGUI(QWidget):
    """GUI for the Web Crawler tool."""
    def __init__(self):
        super().__init__()
        self.crawler_thread = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # --- UI Widgets ---
        self.output_folder = QLineEdit()
        browse_output_btn = QPushButton("Browse")
        self.mode1 = QRadioButton("Search for modules (by CSS class)")
        self.mode2 = QRadioButton("Search for specific words")
        self.search_input = QLineEdit()
        self.url_input = QTextEdit()
        self.extract_options = {
            "title": QCheckBox("Extract Title"),
            "meta_title": QCheckBox("Extract Meta Title"),
            "meta_description": QCheckBox("Extract Meta Description"),
            "content": QCheckBox("Extract Content (Under Dev as .docx)"),
            "meta_tags": QCheckBox("Extract Meta Tags"),
        }
        self.check_errors = QCheckBox("Log 403 and 404 Errors")
        self.progress = QProgressBar()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.start_button = QPushButton("Start Crawling")
        self.stop_button = QPushButton("Stop Crawling")
        self.stop_button.setEnabled(False)

        # --- Layout ---
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Folder:"))
        output_layout.addWidget(self.output_folder)
        output_layout.addWidget(browse_output_btn)
        
        mode_group = QGroupBox("Search Mode")
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.mode1)
        mode_layout.addWidget(self.mode2)
        mode_group.setLayout(mode_layout)

        extract_group = QGroupBox("Extract Options")
        extract_layout = QVBoxLayout()
        for option in self.extract_options.values():
            extract_layout.addWidget(option)
        extract_group.setLayout(extract_layout)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(output_layout)
        layout.addWidget(mode_group)
        self.search_input.setPlaceholderText("Enter search terms separated by commas")
        layout.addWidget(self.search_input)
        self.url_input.setPlaceholderText("Enter one URL or sitemap.xml per line")
        layout.addWidget(self.url_input)
        layout.addWidget(extract_group)
        layout.addWidget(self.check_errors)
        layout.addWidget(self.progress)
        layout.addWidget(self.log_output)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

        # --- Connections ---
        browse_output_btn.clicked.connect(self.browse_output_folder)
        self.start_button.clicked.connect(self.start_crawling)
        self.stop_button.clicked.connect(self.stop_crawling)

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder.setText(folder)

    def start_crawling(self):
        urls = [url.strip() for url in self.url_input.toPlainText().strip().splitlines() if url.strip()]
        if not urls:
            QMessageBox.warning(self, "Input Error", "Please enter at least one URL.")
            return

        output_folder = self.output_folder.text()
        if not output_folder:
            QMessageBox.warning(self, "Input Error", "Please select an output folder.")
            return

        mode = 1 if self.mode1.isChecked() else 2 if self.mode2.isChecked() else 0
        search_input = self.search_input.text().strip()
        if mode in [1, 2] and not search_input:
            QMessageBox.warning(self, "Input Error", "Search mode is selected, but no search terms were provided.")
            return

        self.log_output.clear()
        self.progress.setValue(0)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        extract_opts = {key: option.isChecked() for key, option in self.extract_options.items()}

        self.crawler_thread = CrawlerThread(
            mode=mode,
            search_input=search_input,
            urls=urls,
            extract_options=extract_opts,
            check_errors=self.check_errors.isChecked(),
            output_folder=output_folder
        )
        self.crawler_thread.progress_update.connect(self.progress.setValue)
        self.crawler_thread.log_update.connect(self.log_output.append)
        self.crawler_thread.finished.connect(self.crawl_finished)
        self.crawler_thread.start()

    def stop_crawling(self):
        if self.crawler_thread and self.crawler_thread.isRunning():
            self.crawler_thread.stop()
            self.stop_button.setEnabled(False)

    def crawl_finished(self, output_folder):
        self.log_output.append(f"Process finished. Results are in: {output_folder}")
        QMessageBox.information(self, "Crawling Completed", f"Crawling finished.\nResults saved in: {output_folder}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)


# --------------------- New "Download All Images" Classes ---------------------
class AllImagesDownloaderThread(QThread):
    """
    Worker thread to scrape all images from URLs, download them, create metadata Excel files,
    and optionally compress the downloaded images.
    """
    progress = pyqtSignal(int, str)  # Percentage, status_text
    finished = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, urls, save_folder, auth, compress_options):
        super().__init__()
        self.urls = urls
        self.save_folder = save_folder
        self.auth = auth
        self.compress_options = compress_options
        self.is_stopped = False

    def stop(self):
        self.log.emit("Stopping process...")
        self.is_stopped = True

    def run(self):
        try:
            asyncio.run(self.main_downloader())
        except Exception as e:
            self.log.emit(f"An unexpected error occurred: {e}")
        self.finished.emit("Completed" if not self.is_stopped else "Stopped")

    async def main_downloader(self):
        async with aiohttp.ClientSession(headers=HEADERS, auth=self.auth) as session:
            total_urls = len(self.urls)
            for i, url in enumerate(self.urls):
                if self.is_stopped: break
                status = f"Processing URL {i+1}/{total_urls}: {url}"
                self.progress.emit(int((i / total_urls) * 100), status)
                await self.process_url(session, url.strip())
        
        if not self.is_stopped:
            self.progress.emit(100, "All URLs processed.")
            self.log.emit("Download and extraction completed.")

    async def process_url(self, session, url):
        try:
            async with session.get(url, ssl=False, timeout=30) as response:
                if response.status != 200:
                    self.log.emit(f"Failed to fetch {url}: Status {response.status}")
                    return

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                page_title = sanitize_filename(soup.title.string if soup.title else "Untitled")
                url_folder = os.path.join(self.save_folder, page_title)
                originals_folder = os.path.join(url_folder, "Originals")
                os.makedirs(originals_folder, exist_ok=True)

                workbook = Workbook()
                ws = workbook.active
                ws.title = "Image Data"
                ws.append(["Image URL", "Alt Text", "Title", "Local Filename"])

                img_sources = self._extract_img_sources(soup, url)
                self.log.emit(f"Found {len(img_sources)} images on {url}")

                download_tasks = []
                for src, img_name, alt, title in img_sources:
                    if self.is_stopped: break
                    local_path = os.path.join(originals_folder, img_name)
                    ws.append([src, alt, title, img_name])
                    download_tasks.append(self._download_image(session, src, local_path))
                
                await asyncio.gather(*download_tasks)

                excel_path = os.path.join(url_folder, f"{page_title}_Image_Data.xlsx")
                workbook.save(excel_path)
                self.log.emit(f"Metadata saved to {excel_path}")
                
                # --- Compression Step ---
                if self.compress_options['enabled'] and not self.is_stopped:
                    self.log.emit(f"Starting compression for images from {url}...")
                    self._compress_images(
                        source_dir=originals_folder,
                        output_dir=os.path.join(url_folder, "Compressed"),
                        fmt=self.compress_options['format'],
                        quality=self.compress_options['quality']
                    )

        except Exception as e:
            self.log.emit(f"Error processing {url}: {e}")

    def _extract_img_sources(self, soup, base_url):
        sources = set()
        for tag in soup.find_all(['img', 'source']):
            alt = tag.get('alt', '').strip()
            title = tag.get('title', '').strip()
            
            src_attrs = [tag.get('src'), tag.get('data-src')]
            if tag.get('srcset'):
                src_attrs.extend([s.strip().split(' ')[0] for s in tag.get('srcset').split(',')])

            for src in src_attrs:
                if src:
                    resolved_url = urljoin(base_url, src.strip())
                    img_name = sanitize_filename(os.path.basename(urlparse(resolved_url).path))
                    if img_name and '.' in img_name:
                         sources.add((resolved_url, img_name, alt, title))
        return list(sources)

    async def _download_image(self, session, url, local_path):
        try:
            async with session.get(url, ssl=False) as response:
                if response.status == 200:
                    with open(local_path, "wb") as f:
                        f.write(await response.read())
                    self.log.emit(f"Downloaded: {os.path.basename(local_path)}")
                else:
                    self.log.emit(f"Failed download for {url}: Status {response.status}")
        except Exception as e:
            self.log.emit(f"Error downloading {url}: {e}")

    def _compress_images(self, source_dir, output_dir, fmt, quality):
        os.makedirs(output_dir, exist_ok=True)
        supported = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.avif')
        format_map = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG', 'webp': 'WEBP', 'gif': 'GIF', 'avif': 'AVIF'}
        save_format = format_map.get(fmt.lower(), 'JPEG')

        for filename in os.listdir(source_dir):
            if self.is_stopped: break
            if not filename.lower().endswith(supported): continue

            img_path = os.path.join(source_dir, filename)
            self.log.emit(f"Compressing {filename}")
            try:
                with Image.open(img_path) as img:
                    base_name = os.path.splitext(filename)[0]
                    output_path = os.path.join(output_dir, f"{base_name}.{fmt.lower()}")
                    
                    if img.mode in ('P', 'RGBA') and save_format not in ['PNG', 'WEBP', 'AVIF']:
                        img = img.convert('RGB')
                    
                    save_options = {'format': save_format, 'optimize': True}
                    if save_format in ['JPEG', 'WEBP']:
                        save_options['quality'] = quality
                    img.save(output_path, **save_options)
            except Exception as e:
                self.log.emit(f"Could not compress {filename}: {e}")

class AllImagesDownloaderGUI(QWidget):
    """GUI for the 'Download All Images' feature."""
    def __init__(self):
        super().__init__()
        self.downloader_thread = None
        self.output_folder = ""
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # --- Output Folder ---
        output_layout = QHBoxLayout()
        output_btn = QPushButton("Set Output Folder")
        output_btn.clicked.connect(self.select_output_folder)
        self.output_label = QLabel("Output Folder: Not Set")
        output_layout.addWidget(output_btn)
        output_layout.addWidget(self.output_label)
        layout.addLayout(output_layout)

        # --- URL Input ---
        layout.addWidget(QLabel("Enter URLs (one per line):"))
        self.url_text = QTextEdit()
        layout.addWidget(self.url_text)

        # --- Authentication ---
        auth_group = QGroupBox("Authentication (if needed)")
        auth_layout = QVBoxLayout(auth_group)
        self.use_auth_check = QCheckBox("Use Authentication")
        self.username_entry = QLineEdit(placeholderText="Username")
        self.password_entry = QLineEdit(placeholderText="Password", echoMode=QLineEdit.EchoMode.Password)
        auth_layout.addWidget(self.use_auth_check)
        auth_layout.addWidget(self.username_entry)
        auth_layout.addWidget(self.password_entry)
        layout.addWidget(auth_group)

        # --- Compression Options ---
        compress_group = QGroupBox("Extract Options")
        compress_group.setCheckable(True)
        compress_group.setChecked(False)
        compress_layout = QHBoxLayout(compress_group)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["jpg", "png", "webp"])
        self.quality_spin = QSpinBox(minimum=1, maximum=100, value=85)
        compress_layout.addWidget(QLabel("Format:"))
        compress_layout.addWidget(self.format_combo)
        compress_layout.addWidget(QLabel("Quality:"))
        compress_layout.addWidget(self.quality_spin)
        layout.addWidget(compress_group)
        self.compress_group = compress_group

        # --- Controls and Logs ---
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Status: Ready")
        self.log_output = QTextEdit(readOnly=True)
        self.start_button = QPushButton("Start Download")
        self.stop_button = QPushButton("Stop", enabled=False)
        open_folder_btn = QPushButton("Open Output Folder")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Log Output:"))
        layout.addWidget(self.log_output)
        layout.addLayout(button_layout)
        layout.addWidget(open_folder_btn)

        # --- Connections ---
        self.start_button.clicked.connect(self.start_download)
        self.stop_button.clicked.connect(self.stop_download)
        open_folder_btn.clicked.connect(self.open_output_folder)
        
    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self)
        if folder:
            self.output_folder = folder
            self.output_label.setText(f"Output Folder: {folder}")

    def open_output_folder(self):
        if self.output_folder and os.path.isdir(self.output_folder):
            try:
                subprocess.Popen(f'explorer "{os.path.abspath(self.output_folder)}"' if os.name == 'nt' else ['open', self.output_folder])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open folder: {e}")
        else:
            QMessageBox.warning(self, "Warning", "Output folder is not set or is invalid.")

    def start_download(self):
        urls = [u.strip() for u in self.url_text.toPlainText().strip().splitlines() if u.strip()]
        if not urls or not self.output_folder:
            QMessageBox.warning(self, "Input Error", "Please provide URLs and set an output folder.")
            return

        auth = None
        if self.use_auth_check.isChecked():
            user = self.username_entry.text().strip()
            pwd = self.password_entry.text().strip()
            if not user or not pwd:
                QMessageBox.warning(self, "Input Error", "Authentication is checked, but username or password is missing.")
                return
            auth = BasicAuth(login=user, password=pwd)

        compress_options = {
            'enabled': self.compress_group.isChecked(),
            'format': self.format_combo.currentText(),
            'quality': self.quality_spin.value()
        }

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.log_output.clear()

        self.downloader_thread = AllImagesDownloaderThread(urls, self.output_folder, auth, compress_options)
        self.downloader_thread.progress.connect(self.update_progress)
        self.downloader_thread.log.connect(self.log_output.append)
        self.downloader_thread.finished.connect(self.on_finished)
        self.downloader_thread.start()

    def stop_download(self):
        if self.downloader_thread and self.downloader_thread.isRunning():
            self.downloader_thread.stop()
            self.stop_button.setEnabled(False)
    
    def update_progress(self, value, text):
        self.progress_bar.setValue(value)
        self.status_label.setText(f"Status: {text}")

    def on_finished(self, status):
        QMessageBox.information(self, "Process Finished", f"The process has finished with status: {status}")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(f"Status: {status}")

# --------------------- Image Processor and Downloader Classes ---------------------
class ImageProcessorThread(QThread):
    """
    A worker thread for downloading (from Excel/URL list) and/or compressing images.
    """
    download_progress = pyqtSignal(int)
    compress_progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished_processing = pyqtSignal(str)

    def __init__(self, mode, excel_path, urls, source_folder, output_folder, image_format, quality):
        super().__init__()
        self.mode = mode
        self.excel_path = excel_path
        self.urls = urls
        self.source_folder = source_folder
        self.output_folder = output_folder
        self.image_format = image_format
        self.quality = quality
        self.stop_processing_flag = False

    def stop(self):
        self.status_update.emit("Stopping process...")
        self.stop_processing_flag = True

    def run(self):
        try:
            download_dir = os.path.join(self.output_folder, 'Originals')
            if self.mode == "excel":
                self.status_update.emit("Starting download from Excel file...")
                self._download_from_excel(download_dir)
            elif self.mode == "url":
                self.status_update.emit("Starting download from URLs...")
                self._download_from_urls(download_dir)
            
            if self.stop_processing_flag:
                self.finished_processing.emit("Stopped")
                return

            source_dir = self.source_folder if self.mode == "local" else download_dir
            if os.path.isdir(source_dir):
                 self.status_update.emit("Starting image compression...")
                 self._compress_images(source_dir)
            else:
                self.status_update.emit("Source directory for compression not found. Skipping compression.")

            if not self.stop_processing_flag:
                self.finished_processing.emit("Completed")
            else:
                self.finished_processing.emit("Stopped")

        except Exception as e:
            self.status_update.emit(f"An error occurred: {str(e)}")
            self.finished_processing.emit("Error")

    def _download_from_excel(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        df = pd.read_excel(self.excel_path, sheet_name=0)
        if df.empty: return
        
        url_column = df.columns[0]
        total = len(df)
        for i, row in df.iterrows():
            if self.stop_processing_flag: break
            url = str(row[url_column]).strip()
            if not url: continue
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            self._download_file(url, output_dir)
            self.download_progress.emit(int((i + 1) / total * 100))

    def _download_from_urls(self, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        total = len(self.urls)
        for i, url in enumerate(self.urls):
            if self.stop_processing_flag: break
            self._download_file(url, output_dir)
            self.download_progress.emit(int((i + 1) / total * 100))

    def _download_file(self, url, output_dir):
        try:
            filename = sanitize_filename(os.path.basename(urlparse(url).path))
            if not filename: return
            
            self.status_update.emit(f"Downloading: {filename}")
            response = requests.get(url, stream=True, verify=False, timeout=10)
            if response.status_code == 200:
                with open(os.path.join(output_dir, filename), 'wb') as f:
                    for chunk in response.iter_content(8192):
                        if self.stop_processing_flag: return
                        f.write(chunk)
            else:
                self.status_update.emit(f"Failed to download {filename} (status: {response.status_code})")
        except Exception as e:
            self.status_update.emit(f"Error downloading {url}: {e}")

    def _compress_images(self, source_dir):
        compressed_folder = os.path.join(self.output_folder, 'Compressed')
        os.makedirs(compressed_folder, exist_ok=True)
        
        supported = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.avif')
        format_map = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG', 'webp': 'WEBP', 'gif': 'GIF', 'avif': 'AVIF'}
        save_format = format_map.get(self.image_format.lower(), 'JPEG')

        files_to_process = [os.path.join(r, f) for r, _, files in os.walk(source_dir) for f in files if f.lower().endswith(supported)]
        total = len(files_to_process)
        if total == 0:
            self.status_update.emit("No images found to compress.")
            return

        for i, img_path in enumerate(files_to_process):
            if self.stop_processing_flag: break
            filename = os.path.basename(img_path)
            self.status_update.emit(f"Compressing {filename}")
            
            try:
                with Image.open(img_path) as img:
                    base_name = os.path.splitext(filename)[0]
                    output_path = os.path.join(compressed_folder, f"{base_name}.{self.image_format.lower()}")
                    
                    if img.format == 'GIF' and save_format == 'GIF':
                        img.save(output_path, save_all=True, append_images=img.n_frames > 1, optimize=False, loop=0)
                        continue

                    if img.mode in ('P', 'RGBA') and save_format not in ['PNG', 'WEBP', 'AVIF']:
                        img = img.convert('RGB')
                    
                    save_options = {'format': save_format, 'optimize': True}
                    if save_format in ['JPEG', 'WEBP']:
                        save_options['quality'] = self.quality
                    
                    img.save(output_path, **save_options)
            except Exception as e:
                self.status_update.emit(f"Could not process {filename}: {e}")
            self.compress_progress.emit(int((i + 1) / total * 100))

class BaseDownloaderGUI(QWidget):
    """Base class for downloader GUIs to avoid code duplication."""
    def __init__(self):
        super().__init__()
        self.image_thread = None

    def create_common_widgets(self):
        # --- Output and Settings ---
        self.output_folder = QLineEdit()
        output_btn = QPushButton("Browse")
        output_btn.clicked.connect(lambda: self.browse_folder(self.output_folder))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["jpg", "png", "webp", "gif", "avif"])
        self.quality_spin = QSpinBox(minimum=1, maximum=100, value=85)
        
        format_quality_group = QGroupBox("Format and Compression")
        format_quality_layout = QHBoxLayout(format_quality_group)
        format_quality_layout.addWidget(QLabel("Format:"))
        format_quality_layout.addWidget(self.format_combo)
        format_quality_layout.addSpacing(20)
        format_quality_layout.addWidget(QLabel("Quality:"))
        format_quality_layout.addWidget(self.quality_spin)
        
        self.status_label = QLabel("Status: Ready")
        self.progress_bar_download = QProgressBar()
        self.progress_bar_compress = QProgressBar()
        self.process_button = QPushButton("Start Process")
        self.stop_button = QPushButton("Stop", enabled=False)

        # Layouts
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Folder:"))
        output_layout.addWidget(self.output_folder)
        output_layout.addWidget(output_btn)

        download_layout = QHBoxLayout()
        download_layout.addWidget(QLabel("Downloading:"))
        download_layout.addWidget(self.progress_bar_download)
        
        compress_layout = QHBoxLayout()
        compress_layout.addWidget(QLabel("Compressing:"))
        compress_layout.addWidget(self.progress_bar_compress)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.stop_button)

        return [output_layout, format_quality_group, self.status_label, 
                download_layout, compress_layout, button_layout]
    
    def processing_finished(self, status):
        messages = {
            "Completed": ("Success", "Process completed successfully."),
            "Stopped": ("Stopped", "Process was stopped by the user."),
            "Error": ("Error", "An error occurred during processing.")
        }
        title, msg = messages.get(status, ("Info", status))
        QMessageBox.information(self, title, msg)
        self.status_label.setText("Status: Ready")
        self.process_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def browse_file(self, line_edit, file_filter):
        file, _ = QFileDialog.getOpenFileName(self, "Select File", "", file_filter)
        if file: line_edit.setText(file)

    def browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder: line_edit.setText(folder)
        
    def stop_processing(self):
        if self.image_thread and self.image_thread.isRunning():
            self.image_thread.stop()
            self.stop_button.setEnabled(False)

class ExcelDownloaderGUI(BaseDownloaderGUI):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        self.excel_path = QLineEdit()
        excel_btn = QPushButton("Browse")
        excel_btn.clicked.connect(lambda: self.browse_file(self.excel_path, "Excel Files (*.xlsx *.xls)"))
        
        excel_layout = QHBoxLayout()
        excel_layout.addWidget(QLabel("Excel File:"))
        excel_layout.addWidget(self.excel_path)
        excel_layout.addWidget(excel_btn)
        layout.addLayout(excel_layout)

        for widget in self.create_common_widgets():
            if isinstance(widget, QLayout): layout.addLayout(widget)
            else: layout.addWidget(widget)

        self.process_button.clicked.connect(self.start_processing)
        self.stop_button.clicked.connect(self.stop_processing)

    def start_processing(self):
        if not self.excel_path.text() or not self.output_folder.text():
            QMessageBox.warning(self, "Input Error", "Please select an Excel file and an output folder.")
            return
        self.common_start_logic("excel")

    def common_start_logic(self, mode, urls=None):
        self.status_label.setText("Status: Processing...")
        self.process_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar_download.setValue(0)
        self.progress_bar_compress.setValue(0)

        self.image_thread = ImageProcessorThread(
            mode=mode, excel_path=self.excel_path.text(), urls=urls,
            source_folder="", output_folder=self.output_folder.text(),
            image_format=self.format_combo.currentText(), quality=self.quality_spin.value()
        )
        self.image_thread.download_progress.connect(self.progress_bar_download.setValue)
        self.image_thread.compress_progress.connect(self.progress_bar_compress.setValue)
        self.image_thread.status_update.connect(lambda msg: self.status_label.setText(f"Status: {msg}"))
        self.image_thread.finished_processing.connect(self.processing_finished)
        self.image_thread.start()

class UrlDownloaderGUI(BaseDownloaderGUI):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        self.url_text = QTextEdit(placeholderText="Enter one image URL per line")
        layout.addWidget(QLabel("Image URLs:"))
        layout.addWidget(self.url_text)

        for widget in self.create_common_widgets():
            if isinstance(widget, QLayout): layout.addLayout(widget)
            else: layout.addWidget(widget)
            
        self.process_button.clicked.connect(self.start_processing)
        self.stop_button.clicked.connect(self.stop_processing)
    
    def start_processing(self):
        urls = [u.strip() for u in self.url_text.toPlainText().strip().splitlines() if u.strip()]
        if not urls or not self.output_folder.text():
            QMessageBox.warning(self, "Input Error", "Please enter at least one URL and select an output folder.")
            return
        self.common_start_logic("url", urls=urls)
        
    def common_start_logic(self, mode, urls=None):
        self.status_label.setText("Status: Processing...")
        self.process_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar_download.setValue(0)
        self.progress_bar_compress.setValue(0)

        self.image_thread = ImageProcessorThread(
            mode=mode, excel_path="", urls=urls,
            source_folder="", output_folder=self.output_folder.text(),
            image_format=self.format_combo.currentText(), quality=self.quality_spin.value()
        )
        self.image_thread.download_progress.connect(self.progress_bar_download.setValue)
        self.image_thread.compress_progress.connect(self.progress_bar_compress.setValue)
        self.image_thread.status_update.connect(lambda msg: self.status_label.setText(f"Status: {msg}"))
        self.image_thread.finished_processing.connect(self.processing_finished)
        self.image_thread.start()

class ImageDownloaderGUI(QWidget):
    """Main tab for all image downloading functionalities."""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        self.all_images_tab = AllImagesDownloaderGUI()
        self.excel_tab = ExcelDownloaderGUI()
        self.url_tab = UrlDownloaderGUI()

        self.tabs.addTab(self.all_images_tab, "Download All Images from Page")
        self.tabs.addTab(self.excel_tab, "Download from Excel")
        self.tabs.addTab(self.url_tab, "Download from URL List")
        
        layout.addWidget(self.tabs)

class ImageCompressorGUI(BaseDownloaderGUI):
    """Simplified GUI for compressing local images only."""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        self.source_folder = QLineEdit()
        source_btn = QPushButton("Browse")
        source_btn.clicked.connect(lambda: self.browse_folder(self.source_folder))
        
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source Folder:"))
        source_layout.addWidget(self.source_folder)
        source_layout.addWidget(source_btn)
        layout.addLayout(source_layout)
        
        # Reuse common widgets, but hide the download progress bar
        common_widgets = self.create_common_widgets()
        for widget in common_widgets:
            if isinstance(widget, QLayout): layout.addLayout(widget)
            else: layout.addWidget(widget)
        
        self.progress_bar_download.setVisible(False)
        self.progress_bar_download.parent().findChild(QLabel).setVisible(False)
        
        self.process_button.clicked.connect(self.start_processing)
        self.stop_button.clicked.connect(self.stop_processing)

    def start_processing(self):
        if not self.source_folder.text() or not self.output_folder.text():
            QMessageBox.warning(self, "Input Error", "Please select a source and an output folder.")
            return

        self.status_label.setText("Status: Processing...")
        self.process_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar_compress.setValue(0)

        self.image_thread = ImageProcessorThread(
            mode="local", excel_path="", urls=None,
            source_folder=self.source_folder.text(), output_folder=self.output_folder.text(),
            image_format=self.format_combo.currentText(), quality=self.quality_spin.value()
        )
        self.image_thread.compress_progress.connect(self.progress_bar_compress.setValue)
        self.image_thread.status_update.connect(lambda msg: self.status_label.setText(f"Status: {msg}"))
        self.image_thread.finished_processing.connect(self.processing_finished)
        self.image_thread.start()

# --------------------- Image Resizer GUI Class (No Changes) ---------------------
class ImageResizerGUI(QWidget):
    """GUI for the Image Resizer tool."""
    def __init__(self):
        super().__init__()
        self.preset_ratios = {
            "1:1 (Square)": 1.0, "4:3 (Standard)": 3.0 / 4.0,
            "3:2 (Photo)": 2.0 / 3.0, "16:9 (Widescreen)": 9.0 / 16.0,
        }
        self.current_aspect_ratio = None
        self._is_updating_dimensions = False
        self.init_ui()
        self.toggle_mode_widgets()

    def init_ui(self):
        layout = QVBoxLayout()
        # --- Mode Selection ---
        mode_group = QGroupBox("Mode")
        mode_layout = QHBoxLayout()
        self.mode_folder_radio = QRadioButton("Process Folder")
        self.mode_single_radio = QRadioButton("Process Single Image")
        self.mode_folder_radio.setChecked(True)
        mode_layout.addWidget(self.mode_folder_radio)
        mode_layout.addWidget(self.mode_single_radio)
        mode_group.setLayout(mode_layout)

        # --- Folder Mode Widgets ---
        self.folder_widgets = QWidget()
        folder_layout = QVBoxLayout(self.folder_widgets)
        folder_layout.setContentsMargins(0, 0, 0, 0)
        self.input_folder = QLineEdit(placeholderText="Select source image folder")
        browse_input_folder_btn = QPushButton("Browse Input")
        self.output_folder = QLineEdit(placeholderText="Select folder for resized images")
        browse_output_folder_btn = QPushButton("Browse Output")
        folder_layout.addLayout(self._create_h_layout([self.input_folder, browse_input_folder_btn]))
        folder_layout.addLayout(self._create_h_layout([self.output_folder, browse_output_folder_btn]))

        # --- Single File Mode Widgets ---
        self.single_file_widgets = QWidget()
        single_file_layout = QVBoxLayout(self.single_file_widgets)
        single_file_layout.setContentsMargins(0, 0, 0, 0)
        self.input_file = QLineEdit(placeholderText="Select source image file")
        browse_input_file_btn = QPushButton("Browse Input")
        self.output_file = QLineEdit(placeholderText="Define output file path and name")
        browse_output_file_btn = QPushButton("Save Image As...")
        single_file_layout.addLayout(self._create_h_layout([self.input_file, browse_input_file_btn]))
        single_file_layout.addLayout(self._create_h_layout([self.output_file, browse_output_file_btn]))

        # --- Resize Options ---
        resize_group = QGroupBox("Extract Options")
        resize_layout = QHBoxLayout(resize_group)
        self.ratio_mode_combo = QComboBox()
        self.ratio_mode_combo.addItems(["Original Ratio", "Free (no constraint)"] + list(self.preset_ratios.keys()))
        self.width_spinbox = QSpinBox(minimum=1, maximum=10000, value=800)
        self.height_spinbox = QSpinBox(minimum=1, maximum=10000, value=600)
        resize_layout.addWidget(QLabel("Mode:"))
        resize_layout.addWidget(self.ratio_mode_combo)
        resize_layout.addWidget(QLabel("Width (px):"))
        resize_layout.addWidget(self.width_spinbox)
        resize_layout.addWidget(QLabel("Height (px):"))
        resize_layout.addWidget(self.height_spinbox)

        # --- Bottom Widgets ---
        self.progress = QProgressBar()
        process_btn = QPushButton("Resize")
        
        # --- Add all widgets to main layout ---
        layout.addWidget(mode_group)
        layout.addWidget(self.folder_widgets)
        layout.addWidget(self.single_file_widgets)
        layout.addWidget(resize_group)
        layout.addWidget(self.progress)
        layout.addWidget(process_btn)
        self.setLayout(layout)
        self.setWindowTitle("Proportional Image Resizer")
        
        # --- Connections ---
        self.mode_folder_radio.toggled.connect(self.toggle_mode_widgets)
        browse_input_folder_btn.clicked.connect(self.select_input_folder)
        browse_output_folder_btn.clicked.connect(lambda: self.browse_folder(self.output_folder))
        browse_input_file_btn.clicked.connect(self.select_input_file)
        browse_output_file_btn.clicked.connect(self.select_output_file)
        self.ratio_mode_combo.currentTextChanged.connect(self.mode_changed)
        self.width_spinbox.valueChanged.connect(self.width_changed)
        self.height_spinbox.valueChanged.connect(self.height_changed)
        process_btn.clicked.connect(self.process)

    def _create_h_layout(self, widgets):
        h_layout = QHBoxLayout()
        for w in widgets: h_layout.addWidget(w)
        return h_layout

    def toggle_mode_widgets(self):
        is_folder_mode = self.mode_folder_radio.isChecked()
        self.folder_widgets.setVisible(is_folder_mode)
        self.single_file_widgets.setVisible(not is_folder_mode)
        self.mode_changed()

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_folder.setText(folder)
            self._update_ratio_from_folder(folder)

    def select_input_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if file:
            self.input_file.setText(file)
            self._update_ratio_from_file(file)

    def select_output_file(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save Image As...", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if file:
            self.output_file.setText(file)

    def browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            line_edit.setText(folder)

    def _update_ratio_from_folder(self, folder_path):
        supported = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')
        try:
            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith(supported):
                    self._update_ratio_from_file(os.path.join(folder_path, file_name))
                    return
        except Exception:
            self.current_aspect_ratio = None
            
    def _update_ratio_from_file(self, file_path):
        try:
            with Image.open(file_path) as img:
                w, h = img.size
                self.current_aspect_ratio = h / w if w > 0 else None
        except Exception:
            self.current_aspect_ratio = None
        self.mode_changed()

    def _get_active_ratio(self):
        mode = self.ratio_mode_combo.currentText()
        if mode == "Original Ratio":
            return self.current_aspect_ratio
        return self.preset_ratios.get(mode)

    def mode_changed(self):
        self._is_updating_dimensions = True
        is_free_mode = self.ratio_mode_combo.currentText() == "Free (no constraint)"
        self.height_spinbox.setEnabled(is_free_mode)
        if not is_free_mode:
            self.width_changed(self.width_spinbox.value())
        self._is_updating_dimensions = False

    def width_changed(self, new_width):
        ratio = self._get_active_ratio()
        if ratio is not None and not self._is_updating_dimensions:
            self._is_updating_dimensions = True
            self.height_spinbox.setValue(int(new_width * ratio))
            self._is_updating_dimensions = False

    def height_changed(self, new_height):
        pass
    
    def process(self):
        if self.mode_folder_radio.isChecked():
            self.process_folder()
        else:
            self.process_single_file()

    def _resize_image(self, img_path, output_path):
        target_width = self.width_spinbox.value()
        target_height = self.height_spinbox.value()
        
        with Image.open(img_path) as img:
            ratio = self._get_active_ratio()
            if ratio is not None:
                target_height = int(target_width * ratio)

            new_size = (target_width, target_height)
            
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
            resized_img.save(output_path)

    def process_folder(self):
        input_path = self.input_folder.text()
        output_path = self.output_folder.text()
        if not os.path.isdir(input_path) or not os.path.isdir(output_path):
            QMessageBox.warning(self, "Error", "Both input and output folders must be valid.")
            return

        supported = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')
        files = [f for f in os.listdir(input_path) if f.lower().endswith(supported)]
        if not files:
            QMessageBox.information(self, "Info", "No supported images found in the input folder.")
            return

        self.progress.setValue(0)
        total = len(files)
        for i, filename in enumerate(files, 1):
            try:
                self._resize_image(os.path.join(input_path, filename), os.path.join(output_path, filename))
            except Exception as e:
                print(f"Error processing {filename}: {e}") # Log to console for debugging
            self.progress.setValue(int(i / total * 100))
        
        QMessageBox.information(self, "Completed", "All images have been resized successfully.")

    def process_single_file(self):
        input_path = self.input_file.text()
        output_path = self.output_file.text()
        if not os.path.isfile(input_path) or not output_path:
            QMessageBox.warning(self, "Error", "Input and output file paths must be valid.")
            return
            
        try:
            self.progress.setValue(0)
            self._resize_image(input_path, output_path)
            self.progress.setValue(100)
            QMessageBox.information(self, "Completed", "Image resized successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while resizing:\n{e}")

# --------------------- About Tab Class ---------------------
class AboutTab(QWidget):
    """A simple tab to display information about the application."""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label = QLabel("About Multitool - Websites & Search")
        font = title_label.font()
        font.setPointSize(16)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # Use QLabel with rich text for simple formatting
        info_text = """
        <p><b>Version:</b> 3.5</p>
        <p><b>Release Date:</b> August 19, 2025</p>
        <hr>
        <h3>Creators</h3>
        <p>
            <b>Developed by:</b><br>
            Eduardo Vetromille (Carlos.Brito@br.nestle.com)<br><br>
            <b>In collaboration with:</b><br>
            Aislan Pavanello (Aislan.Pavanello@br.nestle.com)<br>
            Felipe Martins (Felipe.Martins2@br.nestle.com)
        </p>
        <hr>
        <h3>Project Description</h3>
        <p>
            This multi-functional tool is designed to automate and simplify routine web and image-related tasks. It combines four powerful utilities into a single, user-friendly interface:
        </p>
        <p>
            - <b>Web Crawler:</b> Automatically extracts information from web pages, such as text, titles, and other data, saving everything into organized spreadsheets.
            <br>
            - <b>Image Downloader:</b> Downloads images in bulk, whether from an entire webpage, a list of links in an Excel file, or direct URLs.
            <br>
            - <b>Image Compressor:</b> Optimizes images by reducing their file size, ideal for speeding up website load times without significant quality loss.
            <br>
            - <b>Image Resizer:</b> Changes the dimensions of images, either individually or in batches, to fit new requirements while maintaining the correct aspect ratio.
        </p>
        <hr>
        <p><i>Multitool - Websites & Search - Automation tool for marketing and content tasks.</i></p>
        """

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(info_label)
        self.setLayout(layout)
class ChatbotTab(QWidget):
    """
    Aba 'Assistant' em estilo dashboard:
    - Card de chat com bubbles
    - Pill de status no topo direito
    - Atalhos como mini-cards
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_app = parent
        self.downloader_thread = None
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)

        # ---------- Topo: título + pill de status à direita ----------
        top_layout = QHBoxLayout()
        title = QLabel("Assistant")
        title.setObjectName("Title")
        top_layout.addWidget(title)

        self.top_status_pill = QLabel("Ready")
        self.top_status_pill.setObjectName("chatStatusPill")
        self.top_status_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addStretch()
        top_layout.addWidget(self.top_status_pill)
        main_layout.addLayout(top_layout)

        # ---------- Card principal do chat ----------
        chat_card = QWidget()
        chat_card.setObjectName("card")
        chat_layout = QVBoxLayout(chat_card)
        chat_layout.setContentsMargins(16, 16, 16, 16)
        chat_layout.setSpacing(8)

        # Scroll de mensagens com layout vertical
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.messages_container)

        chat_layout.addWidget(self.scroll_area)
        main_layout.addWidget(chat_card)

        # ---------- Atalhos em mini-cards ----------
        shortcuts_card = QWidget()
        shortcuts_card.setObjectName("card")
        shortcuts_layout = QHBoxLayout(shortcuts_card)
        shortcuts_layout.setContentsMargins(16, 10, 16, 10)
        shortcuts_layout.setSpacing(10)

        lbl = QLabel("Sugestões:")
        lbl.setStyleSheet("color: #9CA3AF;")
        shortcuts_layout.addWidget(lbl)

        btn_example = QPushButton("Baixar imagens de URLs")
        btn_example.setProperty("accent", True)
        btn_example.clicked.connect(self.fill_example_download)
        shortcuts_layout.addWidget(btn_example)

        shortcuts_layout.addStretch()
        main_layout.addWidget(shortcuts_card)

        # ---------- Input pill inferior ----------
        input_card = QWidget()
        input_card.setObjectName("card")
        input_layout = QHBoxLayout(input_card)
        input_layout.setContentsMargins(16, 10, 16, 10)
        input_layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(
            "Ex: Baixe as imagens de https://site1.com, https://site2.com"
        )
        send_button = QPushButton("Enviar")
        send_button.setProperty("accent", True)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_button)
        main_layout.addWidget(input_card)

        # ---------- Status / progresso discreto ----------
        self.status_label = QLabel("Status: Aguardando comando")
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.progress_bar)

        # Conexões
        send_button.clicked.connect(self.handle_user_message)
        self.input_field.returnPressed.connect(self.handle_user_message)

    # ---------- Helpers de UI ----------

    def fill_example_download(self):
        self.input_field.setText(
            "Baixe as imagens de https://www.exemplo1.com, https://www.exemplo2.com"
        )
        self.input_field.setFocus()

    def _add_bubble(self, text, kind="bot"):
        label = QLabel(text)
        label.setWordWrap(True)
        if kind == "user":
            label.setObjectName("userBubble")
            # alinha à esquerda/direita visualmente via layout wrapper
            wrapper = QHBoxLayout()
            wrapper.setContentsMargins(0, 0, 0, 0)
            wrapper.addStretch()
            wrapper.addWidget(label)
            cont = QWidget()
            cont.setLayout(wrapper)
            self.messages_layout.addWidget(cont)
        elif kind == "log":
            label.setObjectName("logBubble")
            self.messages_layout.addWidget(label)
        else:
            label.setObjectName("botBubble")
            wrapper = QHBoxLayout()
            wrapper.setContentsMargins(0, 0, 0, 0)
            wrapper.addWidget(label)
            wrapper.addStretch()
            cont = QWidget()
            cont.setLayout(wrapper)
            self.messages_layout.addWidget(cont)

        # autoscroll pro final
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def append_message(self, sender, text):
        if sender.lower().startswith("você"):
            self._add_bubble(text, "user")
        elif sender.lower().startswith("log"):
            self._add_bubble(text, "log")
        else:
            self._add_bubble(text, "bot")

    # ---------- Lógica do comando ----------

    def handle_user_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        self.append_message("Você", text)
        self.input_field.clear()
        self.process_command(text)

    def process_command(self, text):
        lower = text.lower()

        if "baixe as imagens" in lower or "baixar as imagens" in lower:
            urls = self._extract_urls(text)
            if not urls:
                self.append_message(
                    "Assistant",
                    "Não encontrei URLs no comando.\n"
                    "Exemplo: Baixe as imagens de https://site1.com, https://site2.com"
                )
                return
            self.start_download_images_from_urls(urls)
            return

        self.append_message(
            "Assistant",
            "Ainda não aprendi esse tipo de comando 😅\n"
            "No momento você pode pedir, por exemplo:\n"
            "Baixe as imagens de https://site1.com, https://site2.com"
        )

    def _extract_urls(self, text):
        pattern = r'https?://[^\s,;"]+'
        return re.findall(pattern, text)

    def start_download_images_from_urls(self, urls):
        self.append_message(
            "Assistant",
            "Beleza, vou baixar as imagens destas URLs:\n- " + "\n- ".join(urls)
        )

        output_folder = QFileDialog.getExistingDirectory(
            self, "Selecione a pasta para salvar as imagens"
        )
        if not output_folder:
            self.append_message("Assistant", "Operação cancelada: nenhuma pasta selecionada.")
            return

        compress_options = {
            'enabled': False,
            'format': 'jpg',
            'quality': 85
        }

        if self.downloader_thread and self.downloader_thread.isRunning():
            self.downloader_thread.stop()
            self.downloader_thread.wait()

        self.downloader_thread = AllImagesDownloaderThread(
            urls=urls,
            save_folder=output_folder,
            auth=None,
            compress_options=compress_options
        )

        self.downloader_thread.progress.connect(self.update_progress)
        self.downloader_thread.log.connect(lambda msg: self.append_message("Log", msg))
        self.downloader_thread.finished.connect(self.download_finished)

        self.status_label.setText("Status: Baixando imagens...")
        self.top_status_pill.setText("Running")
        self.progress_bar.setValue(0)
        self.downloader_thread.start()

    def update_progress(self, percent, status_text):
        self.progress_bar.setValue(percent)
        self.status_label.setText(f"Status: {status_text}")

    def download_finished(self, status):
        self.append_message("Assistant", f"Tarefa concluída com status: {status}")
        self.status_label.setText(f"Status: {status}")
        self.top_status_pill.setText("Ready")
        self.progress_bar.setValue(100)


class SitemapExtractorGUI(QWidget):
    """Sub-aba que extrai URLs de sitemaps e permite comparar com lista externa."""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # ---------- STEP 1: SITEMAP ----------
        layout.addWidget(QLabel("Step 1 – Sitemap Index URL:"))

        top_row = QHBoxLayout()

        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("Ex: https://www.site.com/sitemap.xml")

        # botão principal roxo
        self.load_btn = QPushButton("Load Sitemaps")
        self.load_btn.setProperty("accent", True)

        self.clear_btn = QPushButton("Clear")

        top_row.addWidget(self.input_url)
        top_row.addWidget(self.load_btn)
        top_row.addWidget(self.clear_btn)
        layout.addLayout(top_row)

        # ---------- LOG OUTPUT ----------
        layout.addWidget(QLabel("Log Output:"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        # ---------- STATS + URLS EXTRAÍDAS ----------
        self.stats_label = QLabel("Sub-sitemaps: 0 | URLs: 0 | Unique: 0")
        layout.addWidget(self.stats_label)

        layout.addWidget(QLabel("Step 2 – Extracted URLs (from sitemap):"))
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(False)
        layout.addWidget(self.result_box)

        export_layout = QHBoxLayout()
        self.btn_tsv = QPushButton("Copy TSV")
        self.btn_csv = QPushButton("Copy CSV")
        self.btn_list = QPushButton("Copy List")
        export_layout.addWidget(self.btn_tsv)
        export_layout.addWidget(self.btn_csv)
        export_layout.addWidget(self.btn_list)
        layout.addLayout(export_layout)

        # ---------- COMPARE SECTION ----------
        layout.addWidget(QLabel("Step 3 – Compare with Excel URLs:"))
        self.compare_box = QTextEdit()
        self.compare_box.setPlaceholderText("Cole aqui as URLs vindas do Excel, uma por linha")
        layout.addWidget(self.compare_box)

        self.compare_btn = QPushButton("Compare")
        self.compare_btn.setEnabled(False)              # começa desativado
        self.compare_btn.setProperty("accent", False)   # ainda sem roxo
        layout.addWidget(self.compare_btn)

        # ---------- OUTPUT DETALHADO DO COMPARE ----------
        layout.addWidget(QLabel("Compare output:"))
        self.compare_output_box = QTextEdit()
        self.compare_output_box.setReadOnly(True)
        layout.addWidget(self.compare_output_box)

        # ---------- CONNECTIONS ----------
        self.load_btn.clicked.connect(self.run_extractor)
        self.clear_btn.clicked.connect(self.clear_all)

        self.btn_list.clicked.connect(self.copy_list)
        self.btn_tsv.clicked.connect(self.copy_tsv)
        self.btn_csv.clicked.connect(self.copy_csv)
        self.compare_btn.clicked.connect(self.compare_lists)

    def set_compare_ready(self, ready: bool):
        """Ativa/desativa o botão Compare e aplica o roxo quando estiver pronto."""
        self.compare_btn.setEnabled(ready)
        self.compare_btn.setProperty("accent", ready)
        # força o Qt a reaplicar o estilo quando a property muda
        self.compare_btn.style().unpolish(self.compare_btn)
        self.compare_btn.style().polish(self.compare_btn)

    # ---------- Helpers de log ----------
    def log(self, txt):
        self.log_box.append(txt)

    # ---------- Fluxo principal ----------
    def clear_all(self):
        self.result_box.clear()
        self.log_box.clear()
        self.compare_box.clear()
        self.compare_output_box.clear()
        self.stats_label.setText("Sub-sitemaps: 0 | URLs: 0 | Unique: 0")
        self.set_compare_ready(False)

    async def fetch_xml(self, url, session):
        try:
            async with session.get(url, ssl=False) as r:
                if r.status != 200:
                    self.log(f"[ERROR] {url} – status {r.status}")
                    return None
                return await r.text()
        except Exception as e:
            self.log(f"[ERROR] {url} – {e}")
            return None

    async def run_async(self, url):
        import xml.etree.ElementTree as ET
        urls, submaps = [], []

        async with aiohttp.ClientSession(headers=HEADERS) as session:
            self.log("[INIT] Fetching sitemap root...")
            xml_root = await self.fetch_xml(url, session)
            if not xml_root:
                return [], []

            try:
                root = ET.fromstring(xml_root)
            except Exception as e:
                self.log(f"[ERROR] Could not parse root sitemap XML: {e}")
                return [], []

            # remove namespace do tag, se existir
            root_tag = root.tag.split('}')[-1].lower()

            # ---------- CASO 1: sitemapindex (tem sub-sitemaps) ----------
            if root_tag == "sitemapindex":
                self.log("[INFO] Root is <sitemapindex> (has sub-sitemaps).")

                # pega apenas locs dentro de <sitemap>
                for sm_loc in root.iterfind(".//{*}sitemap/{*}loc"):
                    if sm_loc.text:
                        sm_url = sm_loc.text.strip()
                        submaps.append(sm_url)

                self.log(f"[INFO] Found {len(submaps)} sub-sitemaps.")

                for i, sm in enumerate(submaps, 1):
                    self.log(f"[FETCH] ({i}/{len(submaps)}) {sm}")
                    xml_sub = await self.fetch_xml(sm, session)
                    if not xml_sub:
                        continue

                    try:
                        r = ET.fromstring(xml_sub)
                        # aqui esperamos um <urlset> com <url><loc>...</loc></url>
                        for loc in r.iterfind(".//{*}url/{*}loc"):
                            if loc.text:
                                urls.append(loc.text.strip())
                    except Exception as e:
                        self.log(f"[PARSE ERROR] Could not parse sub-sitemap {sm}: {e}")

            # ---------- CASO 2: urlset (sitemap "plano", sem sub-sitemaps) ----------
            elif root_tag == "urlset":
                self.log("[INFO] Root is <urlset> (no nested sub-sitemaps).")
                for loc in root.iterfind(".//{*}url/{*}loc"):
                    if loc.text:
                        urls.append(loc.text.strip())

            # ---------- CASO 3: outro formato (fallback genérico) ----------
            else:
                self.log(f"[WARN] Unknown root tag '{root_tag}', using generic <loc> parsing.")
                for loc in root.iterfind(".//{*}loc"):
                    if loc.text:
                        urls.append(loc.text.strip())

        return urls, submaps

    def run_extractor(self):
        url = self.input_url.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Enter a sitemap URL.")
            return

        # reset parcial
        self.result_box.clear()
        self.compare_output_box.clear()
        self.stats_label.setText("Sub-sitemaps: 0 | URLs: 0 | Unique: 0")
        self.set_compare_ready(False)

        self.log_box.clear()
        self.log(f"[START] Processing sitemap: {url}")

        # estamos no thread da UI => usamos asyncio.run
        try:
            asyncio.run(self._exec(url))
        except RuntimeError:
            # fallback caso algum loop já exista
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._exec(url))
            loop.close()

    async def _exec(self, url):
        urls, submaps = await self.run_async(url)
        unique = sorted(set(urls))
        self.result_box.setPlainText("\n".join(unique))
        self.stats_label.setText(
            f"Sub-sitemaps: {len(submaps)} | URLs: {len(urls)} | Unique: {len(unique)}"
        )
        self.set_compare_ready(bool(unique))
        self.log("[DONE] Sitemap extraction complete.")

    # ---------- Export helpers ----------
    def copy_list(self):
        QApplication.clipboard().setText(self.result_box.toPlainText())

    def copy_tsv(self):
        lines = [l for l in self.result_box.toPlainText().splitlines() if l.strip()]
        QApplication.clipboard().setText("\n".join(f"{l}\t" for l in lines))

    def copy_csv(self):
        lines = [l for l in self.result_box.toPlainText().splitlines() if l.strip()]
        QApplication.clipboard().setText("\n".join(f"{l}," for l in lines))

    # ---------- Compare fluxo ----------
    def compare_lists(self):
        extracted_raw = self.result_box.toPlainText().strip()
        if not extracted_raw:
            QMessageBox.warning(self, "No data", "Load a sitemap first to have URLs to compare.")
            return

        extracted = set(l.strip() for l in extracted_raw.splitlines() if l.strip())
        pasted = [v.strip() for v in self.compare_box.toPlainText().splitlines() if v.strip()]

        if not pasted:
            QMessageBox.warning(self, "No input", "Paste at least one URL from Excel to compare.")
            return

        found, missing = [], []
        for p in pasted:
            if p in extracted:
                found.append(p)
            else:
                missing.append(p)

        # ---- Relatório detalhado para o usuário (no campo próprio) ----
        report_lines = []
        report_lines.append("===== COMPARE REPORT =====")
        report_lines.append(f"Total pasted (Excel): {len(pasted)}")
        report_lines.append(f"Found in sitemap:     {len(found)}")
        report_lines.append(f"Not found (missing):  {len(missing)}")
        report_lines.append("")

        report_lines.append("--- FOUND (present in sitemap) ---")
        if found:
            report_lines.extend(f"✔ {u}" for u in found)
        else:
            report_lines.append("(none)")
        report_lines.append("")

        report_lines.append("--- NOT FOUND (missing from sitemap) ---")
        if missing:
            report_lines.extend(f"✘ {u}" for u in missing)
        else:
            report_lines.append("(none)")
        report_lines.append("")
        report_lines.append("===== END OF REPORT =====")

        self.compare_output_box.setPlainText("\n".join(report_lines))

        # loga só o resumo
        self.log(f"[COMPARE] Pasted: {len(pasted)} — Found: {len(found)} — Not found: {len(missing)}")

        # salva para arquivo (estilo Web Crawler)
        self.save_compare_report_to_excel(pasted, found, missing)

        QMessageBox.information(
            self,
            "Compare Results",
            (
                f"Pasted (Excel): {len(pasted)}\n"
                f"Found in sitemap: {len(found)}\n"
                f"Not found: {len(missing)}\n\n"
                "Detailed output is shown abaixo do botão Compare e um arquivo Excel foi gerado."
            )
        )

    def save_compare_report_to_excel(self, pasted, found, missing):
        # Pergunta onde salvar
        folder = QFileDialog.getExistingDirectory(self, "Select folder to save compare report")
        if not folder:
            self.log("[COMPARE] User cancelled saving Excel report.")
            return

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sitemap_compare_{ts}.xlsx"
        path = os.path.join(folder, filename)

        wb = Workbook()

        # Summary
        ws_sum = wb.active
        ws_sum.title = "Summary"
        ws_sum.append(["Metric", "Value"])
        ws_sum.append(["Total pasted (Excel)", len(pasted)])
        ws_sum.append(["Found in sitemap", len(found)])
        ws_sum.append(["Not found", len(missing)])

        # Found
        ws_found = wb.create_sheet("Found")
        ws_found.append(["URL"])
        for u in found:
            ws_found.append([u])

        # Not found
        ws_missing = wb.create_sheet("NotFound")
        ws_missing.append(["URL"])
        for u in missing:
            ws_missing.append([u])

        wb.save(path)
        self.log(f"[COMPARE] Excel report saved to: {path}")

class BrokenLinkInspectorGUI(QWidget):
    """Sub-aba 'Broken Link Inspector' dentro do Crawler."""
    def __init__(self):
        super().__init__()
        self.worker = None
        self.results = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        title = QLabel("Broken Link Inspector")
        title.setObjectName("Title")
        layout.addWidget(title)

        # --------- Mode selection ----------
        mode_group = QGroupBox("Mode")
        mode_layout = QHBoxLayout()
        self.mode_single = QRadioButton("Single page checkup")
        self.mode_sitemap = QRadioButton("Sitemap audit (via sitemap.xml)")
        self.mode_single.setChecked(True)
        mode_layout.addWidget(self.mode_single)
        mode_layout.addWidget(self.mode_sitemap)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # --------- URL input ----------
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Ex (single): https://www.site.com/page")
        url_layout.addWidget(QLabel("URL:"))
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # --------- Options ----------
        self.same_domain_cb = QCheckBox("Only same-domain links (single page)")
        self.same_domain_cb.setChecked(True)
        layout.addWidget(self.same_domain_cb)

        # --------- Controls ----------
        controls = QHBoxLayout()
        self.run_btn = QPushButton("Run check")
        self.run_btn.setProperty("accent", True)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)

        self.export_btn = QPushButton("Export Excel")
        self.export_btn.setEnabled(False)
        self.export_btn.setProperty("accent", False)

        self.clear_btn = QPushButton("Clear")

        controls.addWidget(self.run_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(self.export_btn)
        controls.addWidget(self.clear_btn)
        layout.addLayout(controls)

        # --------- Progress + stats ----------
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.stats_label = QLabel("Checked: 0 | OK: 0 | Redirect: 0 | 4xx: 0 | 5xx: 0 | Errors: 0")
        layout.addWidget(self.stats_label)

        # --------- Results ----------
        layout.addWidget(QLabel("Results (broken first):"))
        self.results_box = QTextEdit()
        self.results_box.setReadOnly(True)
        layout.addWidget(self.results_box)

        # --------- Log ----------
        layout.addWidget(QLabel("Log:"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        # Connections
        self.mode_single.toggled.connect(self._on_mode_change)
        self.run_btn.clicked.connect(self.start_check)
        self.stop_btn.clicked.connect(self.stop_check)
        self.export_btn.clicked.connect(self.export_results)
        self.clear_btn.clicked.connect(self.clear_all)

        self._on_mode_change(self.mode_single.isChecked())

    def _on_mode_change(self, is_single: bool):
        if self.mode_single.isChecked():
            self.url_input.setPlaceholderText("Ex (single): https://www.site.com/page")
            self.same_domain_cb.setEnabled(True)
        else:
            self.url_input.setPlaceholderText("Ex (sitemap): https://www.site.com/sitemap.xml")
            self.same_domain_cb.setEnabled(False)

    def log(self, msg: str):
        self.log_box.append(msg)

    def set_export_ready(self, ready: bool):
        self.export_btn.setEnabled(ready)
        self.export_btn.setProperty("accent", ready)
        self.export_btn.style().unpolish(self.export_btn)
        self.export_btn.style().polish(self.export_btn)

    def clear_all(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Busy", "Stop the current run before clearing.")
            return
        self.results = []
        self.results_box.clear()
        self.log_box.clear()
        self.progress.setValue(0)
        self.stats_label.setText("Checked: 0 | OK: 0 | Redirect: 0 | 4xx: 0 | 5xx: 0 | Errors: 0")
        self.set_export_ready(False)

    def start_check(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Busy", "A check is already running.")
            return

        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL.")
            return

        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        mode = "single" if self.mode_single.isChecked() else "sitemap"
        same_domain = self.same_domain_cb.isChecked()

        self.results = []
        self.results_box.clear()
        self.progress.setValue(0)
        self.set_export_ready(False)

        self.log_box.clear()
        self.log(f"[START] Mode={mode}, URL={url}")

        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.worker = BrokenLinkWorker(mode=mode, root_url=url, same_domain_only=same_domain)
        self.worker.progress_update.connect(self.progress.setValue)
        self.worker.log_update.connect(self.log)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def stop_check(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.log("[WARN] Stop requested by user.")
            self.stop_btn.setEnabled(False)

    def on_worker_finished(self, results: list):
        self.results = results or []
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self._render_results()
        self.set_export_ready(bool(self.results))

    def _render_results(self):
        if not self.results:
            self.stats_label.setText("Checked: 0 | OK: 0 | Redirect: 0 | 4xx: 0 | 5xx: 0 | Errors: 0")
            self.results_box.setPlainText("No results.")
            return

        total = len(self.results)
        ok = sum(1 for r in self.results if r["category"] == "ok")
        redirect = sum(1 for r in self.results if r["category"] == "redirect")
        c4 = sum(1 for r in self.results if r["category"] == "client_error")
        c5 = sum(1 for r in self.results if r["category"] == "server_error")
        err = sum(1 for r in self.results if r["category"] == "network_error")

        self.stats_label.setText(
            f"Checked: {total} | OK: {ok} | Redirect: {redirect} | 4xx: {c4} | 5xx: {c5} | Errors: {err}"
        )

        def fmt(r):
            status = r["status"] if r["status"] is not None else "ERR"
            cat = r["category"]
            src = r["url"]
            dst = r.get("final_url") or ""

            # para redirects, mostra origem -> destino
            if cat == "redirect" and dst and dst != src:
                return f"[{status}] ({cat}) {src}  ->  {dst}"

            # demais casos, mantemos só a URL original
            return f"[{status}] ({cat}) {src}"

        broken_first = [
            r for r in self.results
            if r["category"] in ("client_error", "server_error", "network_error")
        ]
        redirects = [r for r in self.results if r["category"] == "redirect"]
        oks = [r for r in self.results if r["category"] == "ok"]

        lines = []

        if broken_first:
            lines.append("=== BROKEN / ERROR ===")
            lines.extend(fmt(r) for r in broken_first)
            lines.append("")

        if redirects:
            lines.append("=== REDIRECTS ===")
            lines.extend(fmt(r) for r in redirects)
            lines.append("")

        if oks:
            lines.append("=== OK ===")
            lines.extend(fmt(r) for r in oks)

        self.results_box.setPlainText("\n".join(lines))

    def export_results(self):
        if not self.results:
            QMessageBox.warning(self, "No data", "No results to export.")
            return

        folder = QFileDialog.getExistingDirectory(self, "Select folder to save broken link report")
        if not folder:
            self.log("[EXPORT] User cancelled export.")
            return

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        mode = "single" if self.mode_single.isChecked() else "sitemap"
        filename = f"broken_links_{mode}_{ts}.xlsx"
        path = os.path.join(folder, filename)

        wb = Workbook()

        # Summary
        ws_sum = wb.active
        ws_sum.title = "Summary"
        ws_sum.append(["Metric", "Value"])

        total = len(self.results)
        ok = sum(1 for r in self.results if r["category"] == "ok")
        redirect = sum(1 for r in self.results if r["category"] == "redirect")
        c4 = sum(1 for r in self.results if r["category"] == "client_error")
        c5 = sum(1 for r in self.results if r["category"] == "server_error")
        err = sum(1 for r in self.results if r["category"] == "network_error")

        ws_sum.append(["Total checked", total])
        ws_sum.append(["OK (2xx)", ok])
        ws_sum.append(["Redirect (3xx)", redirect])
        ws_sum.append(["Client error (4xx)", c4])
        ws_sum.append(["Server error (5xx)", c5])
        ws_sum.append(["Network / other errors", err])

        # All results
        ws_all = wb.create_sheet("All")
        ws_all.append(["URL", "Status", "Category", "Final URL", "Error"])
        for r in self.results:
            ws_all.append([
                r["url"],
                r["status"],
                r["category"],
                r["final_url"],
                r["error"],
            ])

        # Broken only
        ws_broken = wb.create_sheet("Broken")
        ws_broken.append(["URL", "Status", "Category", "Final URL", "Error"])
        for r in self.results:
            if r["category"] in ("client_error", "server_error", "network_error"):
                ws_broken.append([
                    r["url"],
                    r["status"],
                    r["category"],
                    r["final_url"],
                    r["error"],
                ])

        wb.save(path)
        self.log(f"[EXPORT] Excel report saved to: {path}")
        QMessageBox.information(self, "Export", f"Report saved to:\n{path}")


class CrawlerMainGUI(QWidget):
    """Container principal de 'Crawler' contendo as sub-abas:
        - Web Crawler
        - Sitemap Extractor
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        title = QLabel("Crawler")
        title.setObjectName("Title")
        layout.addWidget(title)

        self.subtabs = QTabWidget()
        layout.addWidget(self.subtabs)

        # Aba original
        self.webcrawler_tab = CrawlerGUI()
        self.subtabs.addTab(self.webcrawler_tab, "Web Crawler")

        # Nova aba
        self.sitemap_tab = SitemapExtractorGUI()
        self.subtabs.addTab(self.sitemap_tab, "Sitemap")

        # Aba Broken Links
        self.broken_tab = BrokenLinkInspectorGUI()
        self.subtabs.addTab(self.broken_tab, "Broken Links")

# --------------------- Main Application ---------------------
class MainApp(QWidget):
    """
    Main application window that integrates all tools into a tabbed interface.
    """
    def __init__(self):
        super().__init__()
        self.setObjectName("MainApp")  # importante p/ o estilo
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        logo_label = QLabel()
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(script_dir, 'nestle_logo.png')
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaled(200, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(logo_label)
        except Exception:
            pass

        self.tabs = QTabWidget()
        self.crawler_tab = CrawlerMainGUI()
        self.downloader_tab = ImageDownloaderGUI()
        self.compressor_tab = ImageCompressorGUI()
        self.resizer_tab = ImageResizerGUI()
        self.chatbot_tab = ChatbotTab(parent=self)
        self.about_tab = AboutTab()

        self.tabs.addTab(self.crawler_tab, "Crawler")
        self.tabs.addTab(self.downloader_tab, "Image Downloader")
        self.tabs.addTab(self.compressor_tab, "Image Compressor")
        self.tabs.addTab(self.resizer_tab, "Image Resizer")
        self.tabs.addTab(self.about_tab, "About")
        self.tabs.addTab(self.chatbot_tab, "Assistant")

        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.setWindowTitle("Multitool - Websites & Search") # <-- UPDATE THIS LINE
        self.resize(1000, 800)
        self.show()
        self.setStyleSheet(DARK_STYLE)

def closeEvent(self, event):
    # pega o thread do crawler, considerando o container novo
    crawler_thread = None
    if isinstance(self.crawler_tab, CrawlerMainGUI):
        crawler_thread = self.crawler_tab.webcrawler_tab.crawler_thread
    else:
        crawler_thread = getattr(self.crawler_tab, "crawler_thread", None)

    threads_to_stop = [
        crawler_thread,
        getattr(self.downloader_tab.all_images_tab, "downloader_thread", None),
        getattr(self.downloader_tab.excel_tab, "image_thread", None),
        getattr(self.downloader_tab.url_tab, "image_thread", None),
        getattr(self.compressor_tab, "image_thread", None),
    ]

    for thread in threads_to_stop:
        if thread and thread.isRunning():
            thread.stop()
            thread.wait()

    event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApp()
    sys.exit(app.exec())
