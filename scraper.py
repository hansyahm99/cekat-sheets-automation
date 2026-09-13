"""
scraper.py
Login ke Cekat CRM, klik tombol Export/Download di tracker,
lalu tunggu file xlsx-nya selesai ke-download.
Generic: menerima kredensial per business unit (ESL/ESC/EHL).
"""

import os
import time
import glob

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

CEKAT_LOGIN_URL = "https://app.cekat.ai/login"  # TODO: sesuaikan URL login yang sebenarnya
CEKAT_TRACKER_URL = "https://app.cekat.ai/tracker"  # TODO: sesuaikan URL halaman tracker
LOGIN_TIMEOUT = 40
DOWNLOAD_TIMEOUT = 60


def _build_driver(download_dir: str):
    os.makedirs(download_dir, exist_ok=True)

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    return driver


def login(driver, username: str, password: str):
    driver.get(CEKAT_LOGIN_URL)
    wait = WebDriverWait(driver, LOGIN_TIMEOUT)

    # TODO: sesuaikan selector dengan struktur halaman login Cekat yang sebenarnya
    email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
    password_input = driver.find_element(By.NAME, "password")
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

    email_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()

    # tunggu sampai dashboard/tracker kebuka setelah login sukses
    wait.until(EC.url_changes(CEKAT_LOGIN_URL))


def click_export(driver):
    wait = WebDriverWait(driver, LOGIN_TIMEOUT)
    driver.get(CEKAT_TRACKER_URL)

    # TODO: sesuaikan selector tombol Export/Download yang sebenarnya
    export_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Export')]"))
    )
    export_button.click()


def wait_for_download(download_dir: str, timeout: int = DOWNLOAD_TIMEOUT) -> str:
    """Tunggu sampai ada file .xlsx baru (bukan .crdownload) muncul di download_dir."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        xlsx_files = [
            f for f in glob.glob(os.path.join(download_dir, "*.xlsx"))
            if not f.endswith(".crdownload")
        ]
        if xlsx_files:
            # ambil file paling baru
            return max(xlsx_files, key=os.path.getctime)
        time.sleep(1)
    raise TimeoutError(f"File xlsx tidak muncul di {download_dir} dalam {timeout}s")


def download_tracker(username: str, password: str, unit_name: str, download_dir: str) -> str:
    """
    Entry point: login -> klik export -> tunggu download -> return path file.
    Dipanggil oleh main.py dalam loop per unit (ESL/ESC/EHL).
    """
    unit_download_dir = os.path.join(download_dir, unit_name)
    driver = _build_driver(unit_download_dir)
    try:
        login(driver, username, password)
        click_export(driver)
        filepath = wait_for_download(unit_download_dir)
        return filepath
    finally:
        driver.quit()