"""
Basic API tests for Video Manual Generator
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Video Manual Generator"
    assert data["status"] == "running"


def test_health():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "config" in data


# 追加のテストはここに記述
# - 動画アップロード
# - STT実行
# - シーン検出
# - マニュアル生成
# - エクスポート
