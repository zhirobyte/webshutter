import os
import time
import tkinter as tk
from tkinter import filedialog
import httpx
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# GUI to pick the file
def choose_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Select a file with subdomains or URLs",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

# Setup headless Chrome
def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    return webdriver.Chrome(service=Service(), options=chrome_options)

# Overlay watermark onto screenshot
def watermark_image(img_path, status_code):
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)
    font_size = max(20, img.width // 40)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text = f"{status_code} {'OK' if status_code < 400 else 'ERROR'}"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]


    # choose color: green for OK, blue otherwise
    color = (0, 200, 0) if status_code < 400 else (0, 0, 200)

    # position: 10px from top-right
    x = img.width - text_width - 10
    y = 10

    # draw semi-transparent box
    box_padding = 6
    box = [x - box_padding, y - box_padding,
           x + text_width + box_padding, y + text_height + box_padding]
    draw.rectangle(box, fill=(0,0,0,128))
    draw.text((x, y), text, fill=color, font=font)

    img.save(img_path)

# Capture status + screenshot + watermark
def capture(driver, url, output_dir):
    # 1) get status via httpx
    try:
        r = httpx.get(url, timeout=10, follow_redirects=True)
        status = r.status_code
    except Exception:
        status = 0

    # 2) selenium screenshot
    try:
        driver.get(url)
        time.sleep(2)
    except WebDriverException:
        pass  # still save whatever was rendered

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = url.replace("http://", "").replace("https://", "").replace("/", "_")
    path = os.path.join(output_dir, f"{safe}_{timestamp}.png")
    driver.save_screenshot(path)

    # 3) watermark
    watermark_image(path, status)
    print(f"✅ {url} [{status}] → {path}")

def main():
    file_path = choose_file()
    if not file_path:
        print("❌ No file selected. Exiting.")
        return

    project = input("📁 Name this session folder: ").strip()
    if not project:
        print("❌ No name entered. Exiting.")
        return

    out = os.path.join("screenshots", project)
    os.makedirs(out, exist_ok=True)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        domains = [line.strip() for line in f if line.strip()]


    driver = setup_browser()
    for d in domains:
        url = d if d.startswith("http") else f"http://{d}"
        capture(driver, url, out)

    driver.quit()
    print(f"\n🎉 Done! Screenshots with watermarks in `{out}`")

if __name__ == "__main__":
    main()
