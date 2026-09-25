import os
import time
import tkinter as tk
from tkinter import filedialog, simpledialog
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import argparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException

# --- Configuration ---
MAX_WORKERS = 5  # Number of concurrent browsers
WINDOW_SIZE = "1920,1080"
TIMEOUT_SECONDS = 30

class WebShutter:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()
        self.project_dir = ""
        self.images_dir = ""

    def setup_driver(self):
        """Creates a new headless Chrome driver instance."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={WINDOW_SIZE}")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3") # Suppress logs
        
        driver = webdriver.Chrome(service=Service(), options=chrome_options)
        driver.set_page_load_timeout(TIMEOUT_SECONDS)
        driver.set_script_timeout(TIMEOUT_SECONDS)
        return driver

    def scroll_page(self, driver):
        """Scrolls down the page to trigger lazy loading."""
        try:
            total_height = int(driver.execute_script("return document.body.scrollHeight"))
            for i in range(1, total_height, 500):
                driver.execute_script(f"window.scrollTo(0, {i});")
                time.sleep(0.05)
            # Scroll back to top or stay at bottom? Usually top is better for the main shot, 
            # but for "full page" we might want to stitch. 
            # For now, let's just ensure we visited the bottom and go back to top for a clean header shot.
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5) 
        except Exception:
            pass

    def process_url(self, url):
        """Worker function to process a single URL."""
        driver = None
        result = {
            "original_url": url,
            "final_url": "",
            "title": "Error",
            "status": "Failed",
            "image_path": "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Normalize URL
        if not url.startswith("http"):
            target_url = f"http://{url}"
        else:
            target_url = url

        try:
            driver = self.setup_driver()
            
            # Try HTTP first, then HTTPS if failed (or vice versa if provided)
            try:
                driver.get(target_url)
            except WebDriverException:
                if target_url.startswith("http://"):
                    target_url = target_url.replace("http://", "https://")
                elif target_url.startswith("https://"):
                    target_url = target_url.replace("https://", "http://")
                driver.get(target_url)

            # Success if we got here
            self.scroll_page(driver)
            
            page_title = driver.title or "No Title"
            clean_name = target_url.replace("http://", "").replace("https://", "").replace("/", "_").replace(":", "")[:50]
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{clean_name}_{timestamp_str}.png"
            full_path = os.path.join(self.images_dir, filename)
            
            driver.save_screenshot(full_path)
            
            result["status"] = "Success"
            result["final_url"] = driver.current_url
            result["title"] = page_title
            result["image_path"] = f"images/{filename}" # Relative path for HTML
            
            with self.lock:
                print(f"✅ [{page_title[:20]}] {target_url}")

        except TimeoutException:
            print(f"⏱️ Timeout: {target_url}")
            result["status"] = "Timeout"
        except Exception as e:
            print(f"❌ Error {target_url}: {str(e)[:50]}")
            result["status"] = "Error"
            result["error_msg"] = str(e)
        finally:
            if driver:
                driver.quit()
        
        return result

    def generate_html_report(self):
        """Generates a beautiful HTML gallery."""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>WebShutter Report - {datetime.now().strftime("%Y-%m-%d")}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a1a; color: #fff; margin: 0; padding: 20px; }}
                h1 {{ text-align: center; color: #00d2ff; }}
                .stats {{ text-align: center; margin-bottom: 30px; color: #888; }}
                .gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; max-width: 1600px; margin: 0 auto; }}
                .card {{ background: #2d2d2d; border-radius: 10px; overflow: hidden; transition: transform 0.2s; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
                .card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 12px rgba(0,0,0,0.5); }}
                .card img {{ width: 100%; height: 200px; object-fit: cover; object-position: top; border-bottom: 1px solid #444; cursor: pointer; }}
                .card-body {{ padding: 15px; }}
                .card-title {{ font-weight: bold; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #00d2ff; }}
                .card-url {{ font-size: 0.85em; color: #aaa; margin-bottom: 10px; word-break: break-all; }}
                .status-badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.75em; font-weight: bold; }}
                .status-Success {{ background: #28a745; color: white; }}
                .status-Timeout {{ background: #ffc107; color: black; }}
                .status-Error {{ background: #dc3545; color: white; }}
                
                /* Modal */
                .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }}
                .modal-content {{ margin: auto; display: block; max-width: 90%; max-height: 90vh; margin-top: 2vh; }}
                .close {{ position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; cursor: pointer; }}
            </style>
        </head>
        <body>
            <h1>📸 WebShutter Report</h1>
            <div class="stats">
                Scanned: {len(self.results)} | 
                Success: {len([r for r in self.results if r['status'] == 'Success'])} | 
                Failed: {len([r for r in self.results if r['status'] != 'Success'])}
            </div>
            
            <div class="gallery">
                {''.join([f'''
                <div class="card">
                    <img src="{r['image_path']}" onclick="openModal(this.src)" onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">
                    <div class="card-body">
                        <div class="card-title" title="{r['title']}">{r['title']}</div>
                        <div class="card-url"><a href="{r['final_url'] or r['original_url']}" target="_blank" style="color:#aaa;text-decoration:none;">{r['original_url']}</a></div>
                        <span class="status-badge status-{r['status']}">{r['status']}</span>
                    </div>
                </div>
                ''' for r in self.results])}
            </div>

            <div id="myModal" class="modal">
                <span class="close" onclick="document.getElementById('myModal').style.display='none'">&times;</span>
                <img class="modal-content" id="img01">
            </div>

            <script>
                function openModal(src) {{
                    var modal = document.getElementById("myModal");
                    var modalImg = document.getElementById("img01");
                    modal.style.display = "block";
                    modalImg.src = src;
                }}
                // Close on escape key
                document.addEventListener('keydown', function(event) {{
                    if (event.key === "Escape") {{
                        document.getElementById("myModal").style.display = "none";
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        report_path = os.path.join(self.project_dir, "report.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"\n📄 Report generated: {report_path}")

    def run(self):
        # Parse CLI args
        parser = argparse.ArgumentParser(description="WebShutter - Bulk Screenshot Tool")
        parser.add_argument("-f", "--file", help="Path to the file containing URLs")
        parser.add_argument("-n", "--name", help="Project name for the output folder")
        args = parser.parse_args()

        # 1. Select File
        if args.file:
            file_path = args.file
        else:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="Select a file with subdomains or URLs",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
        
        if not file_path:
            print("❌ No file selected.")
            return

        # 2. Project Name
        if args.name:
            project_name = args.name
        else:
            project_name = simpledialog.askstring("Project Name", "Enter project name (creates folder):")
            if not project_name:
                project_name = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 3. Setup Directories
        self.project_dir = os.path.join("screenshots", project_name)
        self.images_dir = os.path.join(self.project_dir, "images")
        os.makedirs(self.images_dir, exist_ok=True)

        # 4. Read Domains
        try:
            with open(file_path, "r") as f:
                domains = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return

        print(f"🚀 Starting WebShutter on {len(domains)} targets with {MAX_WORKERS} threads...")
        
        # 5. Concurrent Processing
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_url = {executor.submit(self.process_url, domain): domain for domain in domains}
            
            for future in as_completed(future_to_url):
                result = future.result()
                self.results.append(result)

        # 6. Generate Report
        self.generate_html_report()
        print("\n✨ All Done! ✨")
        if os.name == 'nt':
            try:
                os.startfile(self.project_dir)
            except Exception:
                pass

if __name__ == "__main__":
    app = WebShutter()
    app.run()
