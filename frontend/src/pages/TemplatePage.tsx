import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Loader2, ArrowRight, Check, X } from 'lucide-react'
import { manualApi, type ManualPlan } from '../lib/api'

export default function TemplatePage() {
  const { videoId } = useParams<{ videoId: string }>()
  const navigate = useNavigate()
  const [plan, setPlan] = useState<ManualPlan | null>(null)
  const [loading, setLoading] = useState(true)
  const [selections, setSelections] = useState<Record<number, boolean>>({})

  useEffect(() => {
    if (!videoId) return

    const loadPlan = async () => {
      try {
        const data = await manualApi.getPlan(videoId)
        setPlan(data)
        // 初期選択状態を設定
        const initial: Record<number, boolean> = {}
        data.steps.forEach((step, idx) => {
          initial[idx] = step.selected
        })
        setSelections(initial)
      } catch (err) {
        console.error('Failed to load plan:', err)
      } finally {
        setLoading(false)
      }
    }

    loadPlan()
  }, [videoId])

  const toggleSelection = (index: number) => {
    setSelections(prev => ({
      ...prev,
      [index]: !prev[index],
    }))
  }

  const handleNext = async () => {
    if (!videoId) return

    try {
      await manualApi.applySelection(videoId, selections)
      navigate(`/export/${videoId}`)
    } catch (err) {
      console.error('Failed to apply selection:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="animate-spin h-12 w-12 text-blue-600" />
      </div>
    )
  }

  if (!plan) {
    return <div>マニュアル計画が見つかりません</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          キャプチャを確認
        </h1>
        <p className="text-gray-600 mb-6">
          マニュアルに含めるキャプチャを選択してください
        </p>

        {/* ステップ一覧 */}
        <div className="space-y-4 mb-8">
          {plan.steps.map((step, index) => (
            <div
              key={index}
              className={`border rounded-lg p-4 cursor-pointer transition-all ${
                selections[index]
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => toggleSelection(index)}
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  {selections[index] ? (
                    <Check className="h-6 w-6 text-blue-600" />
                  ) : (
                    <X className="h-6 w-6 text-gray-400" />
                  )}
                </div>
                <div className="flex-grow">
                  <h3 className="font-medium text-gray-900 mb-1">
                    Step {index + 1}: {step.title}
                  </h3>
                  <p className="text-sm text-gray-600 mb-2">
                    {step.narration}
                  </p>
                  {step.image && (
                    <img
                      src={`http://localhost:8000/${step.image}`}
                      alt={`Step ${index + 1}`}
                      className="mt-2 max-w-md rounded border"
                    />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 次へボタン */}
        <div className="flex justify-end">
          <button
            onClick={handleNext}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
          >
            エクスポートへ
            <ArrowRight className="ml-2 h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  )
}
