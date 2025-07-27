# 📦 WebShutter — Changelog

All notable changes to this project will be documented in this file.

---

## [v1.0.2] - 2025-07-27
### Added
- Users can now **input a custom name** for each screenshot session.
- Screenshots will be stored inside `screenshots/<user-input-folder>/` for better organization.

### Changed
- Improved structure and readability of output folder.
- Minor internal refactoring for clarity.

---

## [v1.0.1] - 2025-07-27
### Added
- Project initialized with CLI and file dialog interface.
- Screenshots taken from list of URLs.
- Headless Chrome mode support.
- Output stored in `screenshots/` directory automatically.
- Supports `.txt` file with multiple URLs or subdomains.

---

## [v1.0.0] - 2025-07-27
### Initial Release
- Basic CLI tool to take screenshots of web pages using Selenium.
- Easy-to-use file picker GUI.
- Saves each screenshot with timestamp.
