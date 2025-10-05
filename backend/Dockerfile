FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# システム依存パッケージのインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .[all]

# OpenAI SDKを追加インストール
RUN pip install --no-cache-dir openai

# アプリケーションコードをコピー
COPY app ./app

# Playwright Chromiumのインストール
RUN playwright install --with-deps chromium

# ポート公開
EXPOSE 8000

# サーバー起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
