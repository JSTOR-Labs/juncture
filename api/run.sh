#/bin/zsh

source .venv/bin/activate
uvicorn --reload --port 8000 main:app
