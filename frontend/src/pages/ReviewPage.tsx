import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Loader2, ArrowRight, CheckCircle2 } from 'lucide-react'
import { processApi, manualApi } from '../lib/api'

export default function ReviewPage() {
  const { videoId } = useParams<{ videoId: string }>()
  const navigate = useNavigate()
  const [processing, setProcessing] = useState(true)
  const [status, setStatus] = useState<string>('処理を開始しています...')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!videoId) return

    const processVideo = async () => {
      try {
        setStatus('音声認識を実行中...')
        await processApi.transcribe(videoId)

        setStatus('シーン検出を実行中...')
        await processApi.detectScenes(videoId)

        setStatus('マニュアル計画を作成中...')
        await manualApi.createPlan(videoId)

        setProcessing(false)
      } catch (err: any) {
        setError(err.response?.data?.detail || '処理に失敗しました')
        setProcessing(false)
      }
    }

    processVideo()
  }, [videoId])

  const handleNext = () => {
    navigate(`/template/${videoId}`)
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          動画を解析中
        </h1>

        {processing ? (
          <div className="text-center py-12">
            <Loader2 className="animate-spin h-16 w-16 text-blue-600 mx-auto mb-4" />
            <p className="text-lg text-gray-700">{status}</p>
            <p className="text-sm text-gray-500 mt-2">
              動画の長さに応じて数分かかる場合があります
            </p>
          </div>
        ) : error ? (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        ) : (
          <div className="text-center py-12">
            <CheckCircle2 className="h-16 w-16 text-green-600 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              解析が完了しました!
            </p>
            <p className="text-sm text-gray-600 mb-6">
              次のステップでキャプチャを確認できます
            </p>
            <button
              onClick={handleNext}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
            >
              次へ
              <ArrowRight className="ml-2 h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
