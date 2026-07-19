# 🏟️ FIFA 2026 Smart Stadium Command

Welcome to the **FIFA 2026 Smart Stadium Command** project! This repository contains a full-stack, real-time tactical dashboard and fan engagement portal designed to handle operations across multiple North American host venues for the upcoming 2026 FIFA World Cup.

## 🌟 Overview

This application acts as a dual-sided platform:
- **Fan Portal:** A localized, multilingual interface offering live match updates, interactive stadium maps, express in-seat food delivery tracking, and an AI-powered conversational assistant to help fans navigate the event seamlessly.
- **Tactical Command Ops Room:** A restricted-access, high-level administrative dashboard for stadium personnel. It features a live telemetry stream, real-time security alerts (heat-mapping), VIP delegation routing, system QA defense tests, and instant resource dispatching.

## 🚀 Features

### Frontend (Fan & Ops Interfaces)
- **Dynamic CSS Grid Layouts:** Responsive 3-column designs and meticulously styled modern components using utility classes.
- **Real-Time Interactive State:** Live incident tracking and dynamic global status badges (e.g., "SYSTEM NOMINAL" vs "SYSTEM ALERT") powered by a unified metrics state.
- **Digital Tournament Passport:** Automatically synchronizes and visualizes your live bracket selections.
- **AI Navigation Assistant:** Ask natural language questions in multiple languages and get concise, location-aware answers about amenities and schedules.
- **Native Audio Playback:** Click "Play Audio" to hear the AI Assistant's responses synthesized in real-time.

### Backend (Python FastAPI)
- **High-Performance API Gateway:** Built on FastAPI with asynchronous request handling.
- **Google Cloud GenAI (Gemini) SDK Integration:** Leverages the `gemini-3.5-flash` model with latency tracking, strict timeout bounds, and graceful offline fallback degradation.
- **Google Cloud Text-to-Speech:** Generates inline audio streams for dynamic frontend audio playback.
- **Regex & Security Layer:** Deep inspection and sanitization of incoming requests to intercept prompt injection attempts.
- **Structured Data endpoints:** Serves mock geolocation coordinates, routing dictionaries, and authentic 2026 knockout bracket data.

## 🛠️ Technology Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic
- **AI & Cloud Services:** Google GenAI SDK, Google Cloud Text-to-Speech
- **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript, Leaflet.js
- **Testing:** Pytest, HTTPX TestClient

## ⚙️ Getting Started

### Prerequisites
- Python 3.10 or higher
- A Google Cloud account with GenAI / Vertex AI access
- Environment variables configured for API keys

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Sitanshudevop/FIFA_Smart_Stadium.git
   cd FIFA_Smart_Stadium
   ```

2. **Create a virtual environment & install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set your environment variables:**
   Create a `.env` file in the root directory (this is correctly ignored by git) and add your keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   # Or alternatively:
   # GOOGLE_CLOUD_CREDENTIALS=/path/to/your/service-account.json
   ```

4. **Start the FastAPI server:**
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

5. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:8000/`.

## 🛡️ Security

This project employs multiple security measures:
- The `.gitignore` is strictly configured to ensure Google Cloud Service Account JSON keys (`*-*.json`) and `.env` files are never uploaded.
- Backend APIs incorporate regex sanitization to block malicious GenAI prompts (e.g. "Ignore previous instructions").

## 🤝 Contributing

Contributions are welcome! Please ensure you test any new API routes and verify frontend layout integrity before submitting a pull request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
