# CINEIQ

CINEIQ is a hybrid movie recommendation system with:
- A FastAPI backend for recommendations
- A Streamlit dashboard for user interaction and basic analytics

## Tech Stack

- Python
- FastAPI (API server)
- Uvicorn (ASGI server)
- Streamlit (dashboard UI)
- Pandas (data processing)
- scikit-learn (cosine similarity)
- joblib (model loading)
- requests (dashboard to API calls)
- Plotly (charts)

## Project Structure

- `api/main.py`: FastAPI app and recommendation logic
- `dashboard/app.py`: Streamlit dashboard
- `data/`: CSV datasets used by API and dashboard
- `models/`: Trained model artifacts (`.pkl` files)

## Prerequisites

- Python 3.9+ recommended
- `pip`

## Setup

From the project root (`CINEIQ/`):

```bash
python -m venv .venv
```

Activate virtual environment:

- Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install fastapi uvicorn streamlit pandas scikit-learn joblib requests plotly
```

## Run the Application

Use two terminals.

### 1) Start Backend API

Important: start from the `api` folder so relative paths in `main.py` resolve correctly.

```bash
cd api
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API base URL: `http://127.0.0.1:8000`

### 2) Start Streamlit Dashboard

In a second terminal, from the project root:

```bash
cd dashboard
streamlit run app.py
```

Streamlit will open in your browser (usually `http://localhost:8501`).

## API Endpoints

- `GET /` : Health message
- `GET /recommend?user_id=<int>` : Hybrid recommendations for a user
- `GET /similar?movie_title=<string>` : Similar movies by title

Example:

```text
http://127.0.0.1:8000/recommend?user_id=1
```

## Notes

- Keep `data/` and `models/` folders unchanged, as both apps load files from these locations.
- If PowerShell blocks script execution while activating venv, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
