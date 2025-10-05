/**
 * API client for Video Manual Generator backend
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 型定義
export interface VideoUploadResponse {
  video_id: string
  filename: string
  size_bytes: number
  duration_sec?: number
}

export interface ProcessStatusResponse {
  video_id: string
  status: string
  message: string
  output_path?: string
}

export interface TranscriptionSegment {
  start: number
  end: number
  speaker?: string
  text: string
}

export interface Transcription {
  video_filename: string
  duration_sec: number
  segments: TranscriptionSegment[]
}

export interface SceneInfo {
  time: number
  frame_path: string
}

export interface SceneDetectionResult {
  video_filename: string
  scenes: SceneInfo[]
}

export interface ManualStep {
  title: string
  narration: string
  note?: string
  image?: string
  start: number
  end: number
  selected: boolean
}

export interface ManualPlan {
  title: string
  source_video: string
  created_at: string
  steps: ManualStep[]
}

export interface ExportResponse {
  video_id: string
  format: string
  output_path: string
  download_url: string
}

// API メソッド
export const videoApi = {
  // 動画アップロード
  uploadVideo: async (file: File): Promise<VideoUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // 動画情報取得
  getVideoInfo: async (videoId: string) => {
    const response = await api.get(`/videos/${videoId}`)
    return response.data
  },
}

export const processApi = {
  // 文字起こし実行
  transcribe: async (videoId: string): Promise<ProcessStatusResponse> => {
    const response = await api.post(`/process/transcribe/${videoId}`)
    return response.data
  },

  // シーン検出実行
  detectScenes: async (videoId: string): Promise<ProcessStatusResponse> => {
    const response = await api.post(`/process/scene-detect/${videoId}`)
    return response.data
  },

  // 文字起こし結果取得
  getTranscription: async (videoId: string): Promise<Transcription> => {
    const response = await api.get(`/process/transcribe/${videoId}`)
    return response.data
  },

  // シーン検出結果取得
  getScenes: async (videoId: string): Promise<SceneDetectionResult> => {
    const response = await api.get(`/process/scene-detect/${videoId}`)
    return response.data
  },
}

export const manualApi = {
  // マニュアル計画作成
  createPlan: async (videoId: string, title?: string): Promise<ManualPlan> => {
    const response = await api.post('/manual/plan', {
      video_id: videoId,
      title,
    })
    return response.data
  },

  // キャプチャ選択適用
  applySelection: async (
    videoId: string,
    selections: Record<number, boolean>
  ): Promise<ManualPlan> => {
    const response = await api.post('/manual/apply-selection', {
      video_id: videoId,
      selections,
    })
    return response.data
  },

  // マニュアル計画取得
  getPlan: async (videoId: string): Promise<ManualPlan> => {
    const response = await api.get(`/manual/plan/${videoId}`)
    return response.data
  },

  // マニュアル計画更新
  updatePlan: async (videoId: string, plan: ManualPlan): Promise<ManualPlan> => {
    const response = await api.put(`/manual/plan/${videoId}`, plan)
    return response.data
  },
}

export const exportApi = {
  // Markdown エクスポート
  exportMarkdown: async (videoId: string, template?: string): Promise<ExportResponse> => {
    const response = await api.post('/export/markdown', {
      video_id: videoId,
      format: 'markdown',
      template,
    })
    return response.data
  },

  // PDF エクスポート
  exportPdf: async (videoId: string, template?: string): Promise<ExportResponse> => {
    const response = await api.post('/export/pdf', {
      video_id: videoId,
      format: 'pdf',
      template,
    })
    return response.data
  },

  // ダウンロード URL 取得
  getDownloadUrl: (videoId: string, filename: string): string => {
    return `${API_BASE_URL}/export/download/${videoId}/${filename}`
  },
}

export default api
