# Python 3.12を使用
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新とビルドツールのインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 静的ファイルを収集
RUN python manage.py collectstatic --noinput

# ChromaDBディレクトリの作成と権限設定
RUN mkdir -p /app/wdb && chmod 777 /app/wdb

# ポート8000を公開
EXPOSE 8000

# Gunicornでアプリケーションを起動
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "config.wsgi:application"]