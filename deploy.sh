#!/bin/bash

set -e

APP_NAME="fastapi"
APP_DIR="$PWD"
VENV_DIR="$APP_DIR/venv"
USER=$(whoami)
PYTHON_VERSION="3.12"
PYTHON_BIN="/usr/bin/python${PYTHON_VERSION}"
DEBIAN_FRONTEND=noninteractive

echo "🔧 [0/6] Updating system and installing required packages..."
sudo apt update
sudo apt install -y software-properties-common curl build-essential libssl-dev libffi-dev \
    libpq-dev python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev

if ! command -v $PYTHON_BIN >/dev/null 2>&1; then
    echo "❌ Python $PYTHON_VERSION not installed correctly."
    exit 1
fi

echo "🐍 [1/6] Creating virtual environment..."
$PYTHON_BIN -m venv $VENV_DIR
source $VENV_DIR/bin/activate

echo "📦 [2/6] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🧠 [3/6] Writing Gunicorn systemd service..."
sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null <<EOF
[Unit]
Description=Gunicorn for FastAPI
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/gunicorn app.main:app \\
    -k uvicorn.workers.UvicornWorker \\
    --bind 0.0.0.0:8000 \\
    --workers $(nproc --all)
Restart=always
Environment=PATH=$VENV_DIR/bin

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 [4/6] Reloading and enabling systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME

echo "🚀 [5/6] Starting FastAPI service..."
sudo systemctl restart $APP_NAME

echo "🎉 [6/6] FastAPI Deployment Complete! Access it at http://<your-server-ip>:8000"
