import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, Loader2 } from 'lucide-react'
import { videoApi } from '../lib/api'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('ファイルを選択してください')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const response = await videoApi.uploadVideo(file)
      // アップロード成功後、解析ページへ遷移
      navigate(`/review/${response.video_id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'アップロードに失敗しました')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          動画をアップロード
        </h1>

        <div className="space-y-6">
          {/* ファイル選択 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              動画ファイル (MP4, MOV, AVI, MKV)
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-blue-400 transition-colors">
              <div className="space-y-1 text-center">
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="flex text-sm text-gray-600">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500"
                  >
                    <span>ファイルを選択</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska"
                      onChange={handleFileChange}
                    />
                  </label>
                  <p className="pl-1">またはドラッグ&ドロップ</p>
                </div>
                <p className="text-xs text-gray-500">最大 500MB</p>
              </div>
            </div>
            {file && (
              <p className="mt-2 text-sm text-gray-600">
                選択されたファイル: <span className="font-medium">{file.name}</span>
              </p>
            )}
          </div>

          {/* エラーメッセージ */}
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* アップロードボタン */}
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {uploading ? (
              <>
                <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5" />
                アップロード中...
              </>
            ) : (
              <>
                <Upload className="-ml-1 mr-2 h-5 w-5" />
                アップロード & 解析開始
              </>
            )}
          </button>
        </div>

        {/* 使い方の説明 */}
        <div className="mt-8 bg-blue-50 rounded-md p-4">
          <h3 className="text-sm font-medium text-blue-900 mb-2">使い方</h3>
          <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800">
            <li>動画ファイルをアップロード</li>
            <li>自動で音声認識とシーン検出を実行</li>
            <li>抽出されたキャプチャを確認・選択</li>
            <li>マニュアルをエクスポート (Markdown/PDF)</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
