# Visual Essays API

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running local dev server

```bash
source .venv/bin/activate
uvicorn --reload --timeout-keep-alive 0 --port 8000 main:app
```

## Deploying

### Google Cloud Run

```bash
./gcr-deploy.sh
```