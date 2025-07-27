import os
import time
import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from datetime import datetime

# GUI to pick the file
def choose_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a file with subdomains or URLs",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    return file_path

# Setup browser options
def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    return webdriver.Chrome(service=Service(), options=chrome_options)

# Screenshot a single domain
def capture_screenshot(driver, url, output_dir):
    try:
        driver.get(url)
        time.sleep(3)  # wait for page to load
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = url.replace("http://", "").replace("https://", "").replace("/", "_")
        screenshot_path = os.path.join(output_dir, f"{filename}_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        print(f"✅ Screenshot saved: {screenshot_path}")
    except WebDriverException as e:
        print(f"❌ Failed to load {url}: {e.msg}")

# Main flow
def main():
    file_path = choose_file()
    if not file_path:
        print("❌ No file selected.")
        return

    # Ask user to name this session/project
    project_name = input("📁 Enter a name for this screenshot session (e.g., 'google', 'pentest-job1'): ").strip()
    if not project_name:
        print("❌ No name entered. Exiting.")
        return

    output_dir = os.path.join("screenshots", project_name)
    os.makedirs(output_dir, exist_ok=True)

    with open(file_path, "r") as f:
        domains = [line.strip() for line in f if line.strip()]

    driver = setup_browser()

    for domain in domains:
        if not domain.startswith("http"):
            domain = "http://" + domain  # default to http
        capture_screenshot(driver, domain, output_dir)

    driver.quit()
    print(f"✅ All screenshots saved in: {output_dir}")

if __name__ == "__main__":
    main()
