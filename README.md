# CrunchyList-Sync

**CrunchyList Sync** is a modern, GUI-based tool written in Python that automatically synchronizes your Crunchyroll watch history to your AniList profile. 

Built with [Flet](https://flet.dev/), it offers a clean, dark-themed user interface to manage your anime tracking without manual data entry.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production-orange)

## ✨ Features
* **GUI Interface**: No command line required; user-friendly dashboard.
* **One-Click Sync**: Fetches your Crunchyroll history and updates AniList automatically.
* **Smart Matching**: Uses fuzzy search to match Crunchyroll titles (English/Romaji) to AniList IDs.
* **Persistence**: Remembers your login session so you don't have to re-authenticate every time.
* **Safety**: Runs locally on your machine. Your tokens are stored only on your computer.

## 🚀 Installation

### Prerequisites
* Python 3.10 or higher
* A Crunchyroll account
* An AniList account

### Setup
1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/CrunchyList-Sync.git](https://github.com/YOUR_USERNAME/CrunchyList-Sync.git)
    cd CrunchyList-Sync
    ```

2.  **Create a virtual environment (Optional but Recommended)**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the App**
    ```bash
    python main.py
    ```

## 📖 Usage Guide

1.  **Login to AniList**: Click the "Login" button. A browser window will open asking you to authorize the app. Once accepted, the app will confirm your login.
2.  **Get Crunchyroll Token**:
    * Open Crunchyroll in your browser.
    * Open Developer Tools (F12) -> Application -> Cookies.
    * Look for `etp_rt` or look for your Bearer token in network requests. (This can be found by looking for the watch-history request.)
    * Paste this token into the "Crunchyroll Token" field in the app and click Save.
3.  **Sync**: Click **"Sync Crunchyroll -> AniList"**.
    * The app will first fetch your history from Crunchyroll.
    * It will then search AniList for every show and update your progress if the Crunchyroll episode count is higher than your AniList record.

## 🤝 Contributing

Contributions, forks, and pull requests are highly encouraged! This is a community project built by anime fans for anime fans.

### How to Contribute
1.  **Fork the Project** (Top right corner of this page).
2.  **Create your Feature Branch** (`git checkout -b feature/AmazingFeature`).
3.  **Commit your Changes** (`git commit -m 'Add some AmazingFeature'`).
4.  **Push to the Branch** (`git push origin feature/AmazingFeature`).
5.  **Open a Pull Request**.

### Ideas for Contributions
* Improve the anime title matching algorithm (fuzzy matching).
* Add support for "Completed" status updates.
* Add support for other services (HIDIVE, Funimation).
* Improve the UI/UX.

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.

## ⚠️ Disclaimer
This project is not affiliated with, endorsed, or sponsored by Crunchyroll or AniList. It is a fan-made tool utilizing public APIs. Use responsibly.
