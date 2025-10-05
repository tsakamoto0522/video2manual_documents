# API ドキュメント

Video Manual Generator API の詳細仕様

## ベース URL

```
http://localhost:8000
```

## エンドポイント一覧

### ヘルスチェック

#### `GET /`

システムステータスを取得

**レスポンス**:
```json
{
  "service": "Video Manual Generator",
  "version": "0.1.0",
  "status": "running"
}
```

#### `GET /health`

詳細なヘルスチェック

**レスポンス**:
```json
{
  "status": "healthy",
  "config": {
    "stt_engine": "whisper",
    "scene_detection": "histogram",
    "pdf_engine": "playwright"
  }
}
```

---

## 動画管理 (`/videos`)

### `POST /videos/upload`

動画ファイルをアップロード

**リクエスト**: `multipart/form-data`
- `file`: 動画ファイル (mp4, mov, avi, mkv)

**レスポンス**:
```json
{
  "video_id": "uuid",
  "filename": "sample.mp4",
  "size_bytes": 10485760,
  "duration_sec": 120.5
}
```

### `GET /videos/{video_id}`

動画情報を取得

**レスポンス**:
```json
{
  "video_id": "uuid",
  "filename": "source.mp4",
  "size_bytes": 10485760,
  "path": "/path/to/video"
}
```

---

## 処理 (`/process`)

### `POST /process/transcribe/{video_id}`

音声認識を実行

**レスポンス**:
```json
{
  "video_id": "uuid",
  "status": "completed",
  "message": "15 セグメントを認識しました",
  "output_path": "data/intermediate/{video_id}/transcription.json"
}
```

### `GET /process/transcribe/{video_id}`

音声認識結果を取得

**レスポンス**:
```json
{
  "video_filename": "sample.mp4",
  "duration_sec": 120.5,
  "segments": [
    {
      "start": 0.0,
      "end": 5.0,
      "speaker": null,
      "text": "こんにちは"
    }
  ]
}
```

### `POST /process/scene-detect/{video_id}`

シーン検出を実行

**レスポンス**:
```json
{
  "video_id": "uuid",
  "status": "completed",
  "message": "8 シーンを検出しました",
  "output_path": "data/intermediate/{video_id}/scenes.json"
}
```

### `GET /process/scene-detect/{video_id}`

シーン検出結果を取得

**レスポンス**:
```json
{
  "video_filename": "sample.mp4",
  "scenes": [
    {
      "time": 0.0,
      "frame_path": "data/captures/{video_id}/scene_0000_0.00s.jpg"
    }
  ]
}
```

---

## マニュアル計画 (`/manual`)

### `POST /manual/plan`

マニュアル計画を作成

**リクエスト**:
```json
{
  "video_id": "uuid",
  "title": "操作マニュアル (オプション)"
}
```

**レスポンス**:
```json
{
  "title": "操作マニュアル",
  "source_video": "sample.mp4",
  "created_at": "2024-01-01T00:00:00",
  "steps": [
    {
      "title": "メニューを開く",
      "narration": "画面左上のメニューボタンをクリックします",
      "note": null,
      "image": "data/captures/.../scene_0001.jpg",
      "start": 0.0,
      "end": 5.0,
      "selected": true
    }
  ]
}
```

### `GET /manual/plan/{video_id}`

マニュアル計画を取得

### `PUT /manual/plan/{video_id}`

マニュアル計画を更新

**リクエスト**: 完全な `ManualPlan` オブジェクト

### `POST /manual/apply-selection`

キャプチャ選択を適用

**リクエスト**:
```json
{
  "video_id": "uuid",
  "selections": {
    "0": true,
    "1": false,
    "2": true
  }
}
```

---

## エクスポート (`/export`)

### `POST /export/markdown`

Markdown としてエクスポート

**リクエスト**:
```json
{
  "video_id": "uuid",
  "format": "markdown",
  "template": "manual_default.md.j2 (オプション)"
}
```

**レスポンス**:
```json
{
  "video_id": "uuid",
  "format": "markdown",
  "output_path": "data/exports/{video_id}/manual.md",
  "download_url": "/export/download/{video_id}/manual.md"
}
```

### `POST /export/pdf`

PDF としてエクスポート

**リクエスト**: 同上

**レスポンス**:
```json
{
  "video_id": "uuid",
  "format": "pdf",
  "output_path": "data/exports/{video_id}/manual.pdf",
  "download_url": "/export/download/{video_id}/manual.pdf"
}
```

### `GET /export/download/{video_id}/{filename}`

エクスポートファイルをダウンロード

**レスポンス**: ファイル本体

---

## エラーレスポンス

すべてのエラーは以下の形式で返されます:

```json
{
  "detail": "エラーメッセージ",
  "type": "VideoProcessingError"
}
```

### ステータスコード

- `200`: 成功
- `400`: リクエストエラー (不正な入力)
- `404`: リソースが見つからない
- `500`: サーバーエラー
