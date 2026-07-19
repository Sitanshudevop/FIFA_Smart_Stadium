<div align="center">

# 🏟️ FIFA 2026 Smart Stadium Command & Fan Portal
**The Official AI-Powered Operations and Navigation Hub for the 2026 World Cup**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/AI-Google_Gemini-FF6F00.svg)](https://ai.google.dev/)
[![WCAG AA](https://img.shields.io/badge/Accessibility-WCAG_AA_Compliant-4CAF50.svg)](https://www.w3.org/WAI/standards-guidelines/wcag/)
[![CI/CD](https://github.com/Sitanshudevop/FIFA_Smart_Stadium/actions/workflows/test-suite.yml/badge.svg)](https://github.com/Sitanshudevop/FIFA_Smart_Stadium/actions)

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/1/17/2026_FIFA_World_Cup_emblem.svg" alt="FIFA 2026 Logo" width="200"/>
</p>

</div>

---

## 🌟 Executive Overview

Welcome to the **FIFA 2026 Smart Stadium Command** project! This repository contains a full-stack, real-time tactical dashboard and fan engagement portal designed to handle operations across multiple North American host venues.

Built for **scalability, high accessibility, and extreme performance**, this architecture leverages the power of Google Cloud GenAI (Gemini) to act as a dual-sided platform:

1. 🌍 **The Fan Portal:** A localized, highly responsive interface offering interactive stadium maps, live multimodal AI navigation, express food delivery, and digital tournament passports.
2. 🛡️ **The Tactical Ops Room:** A restricted-access, high-level administrative dashboard featuring live telemetry, asynchronous incident reporting, AI triage, and real-time security routing.

---

## 🚀 Key Enterprise Features

### 🧠 AI & Multimodal Intelligence
* **Google Gemini Integration:** Leverages `gemini-3.5-flash` with aggressive `async_lru` caching for sub-millisecond redundant token retrieval, slashing API costs and latency.
* **Multimodal Vision Routing:** Fans can snap photos of their ticket or stadium landmarks. The backend parses Base64 image payloads and returns dynamic, localized routing instructions via Gemini Vision.
* **Real-time TTS Synthesis:** Native audio playback of AI routing responses powered by Google Cloud Text-to-Speech.
* **Dynamic Prompt Injection Protection:** Enterprise regex sanitization layers actively block adversarial prompts (e.g., "Ignore previous instructions").

### ♿ Accessibility & UI/UX (WCAG AA)
* **Zero-Destruction ARIA Architecture:** Comprehensive `aria-label`, `aria-live`, and `role` attributes seamlessly integrated for flawless screen reader execution without mutating core DOM structures.
* **Strict CSS Responsiveness:** Elegant stacking flex-grids and mobile viewport protections built entirely via non-destructive CSS media queries.
* **44px Touch Target Compliance:** Fluid and expansive touch targets tailored for mobile-first stadium navigation.

### ⚙️ Performance & CI/CD QA
* **Enterprise CI/CD Pipelines:** Automated GitHub Actions workflows orchestrate isolated testing environments.
* **Comprehensive Mocking:** High-coverage `pytest` suite mocking all external Google Cloud boundaries, simulating network timeouts and 500s.
* **Pydantic Validation:** Strict runtime environment validation prevents catastrophic startup failures from missing secrets.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Fan Portal / UI] -->|REST & FormData| B(FastAPI Gateway)
    A -->|Multimodal Image Uploads| B
    B -->|LRU Cache Intercept| C{Async LRU Cache}
    C -->|Cache Hit| B
    C -->|Cache Miss| D[Google Gemini SDK]
    D -->|Vision / Text Generative Models| E[(Google Cloud AI)]
    B --> F[Google TTS Engine]
    B --> G[Pydantic Settings & Security Validation]
```

---

## 🛠️ Technology Stack

| Domain | Technologies Used |
| :--- | :--- |
| **Backend Core** | `Python 3.11`, `FastAPI`, `Uvicorn`, `Pydantic` |
| **AI & Cloud** | `google-genai`, `google-cloud-texttospeech` |
| **Frontend UI** | `HTML5`, `Tailwind CSS`, `Vanilla JavaScript`, `Leaflet.js` |
| **Performance** | `async-lru`, `slowapi` (Rate Limiting) |
| **QA / Testing** | `pytest`, `pytest-cov`, `httpx` (Async TestClient) |

---

## ⚙️ Quickstart & Deployment

### Prerequisites
* Python 3.10+
* A Google Cloud Account (Vertex AI / Gemini API access)
* Standard build tools (`git`, `pip`)

### 1. Clone the Repository
```bash
git clone https://github.com/Sitanshudevop/FIFA_Smart_Stadium.git
cd FIFA_Smart_Stadium
```

### 2. Configure Environment
Install all enterprise dependencies and set up your environment keys. Note that `.env` files and `*-*.json` service accounts are strictly ignored by Git for security.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory:
```env
# Required for Application Startup
GEMINI_API_KEY="your_secure_api_key_here"
ADMIN_TOKEN="your_secure_admin_token"
# GOOGLE_CLOUD_CREDENTIALS=/path/to/service-account.json
```

### 3. Launch the Gateway
Start the asynchronous ASGI server:
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Access the Portals
* **Fan Portal (Tailwind):** `http://127.0.0.1:8000/`
* **Ops Command Room:** Navigate via the integrated frontend router or local files.

---

## 🧪 Testing

The repository maintains an automated `pytest` suite simulating external boundaries. 
Run the tests locally with full coverage reports:

```bash
python -m pytest tests/ --cov=app --cov-report=term-missing
```

---

## 🤝 Contributing

We welcome contributions! Please adhere to our strict accessibility constraints and ensure all Pytest CI/CD hooks pass before opening a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
