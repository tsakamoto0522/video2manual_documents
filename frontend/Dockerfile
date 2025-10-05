FROM node:20-slim

# 作業ディレクトリ
WORKDIR /app

# パッケージファイルをコピー
COPY package*.json ./

# 依存パッケージのインストール
RUN npm install

# ソースコードをコピー
COPY . .

# ポート公開
EXPOSE 5173

# 開発サーバー起動
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
