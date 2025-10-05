import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { Download, FileText, FileDown, Loader2 } from 'lucide-react'
import { exportApi } from '../lib/api'

export default function ExportPage() {
  const { videoId } = useParams<{ videoId: string }>()
  const [exporting, setExporting] = useState(false)
  const [exportedFiles, setExportedFiles] = useState<{
    markdown?: string
    pdf?: string
  }>({})

  const handleExportMarkdown = async () => {
    if (!videoId) return

    setExporting(true)
    try {
      const response = await exportApi.exportMarkdown(videoId)
      setExportedFiles(prev => ({
        ...prev,
        markdown: response.download_url,
      }))
    } catch (err) {
      console.error('Markdown export failed:', err)
    } finally {
      setExporting(false)
    }
  }

  const handleExportPdf = async () => {
    if (!videoId) return

    setExporting(true)
    try {
      const response = await exportApi.exportPdf(videoId)
      setExportedFiles(prev => ({
        ...prev,
        pdf: response.download_url,
      }))
    } catch (err) {
      console.error('PDF export failed:', err)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          マニュアルをエクスポート
        </h1>
        <p className="text-gray-600 mb-8">
          生成されたマニュアルをダウンロードできます
        </p>

        <div className="space-y-4">
          {/* Markdown エクスポート */}
          <div className="border rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <FileText className="h-8 w-8 text-blue-600" />
                <div>
                  <h3 className="font-medium text-gray-900">Markdown</h3>
                  <p className="text-sm text-gray-500">
                    テキストエディタで編集可能
                  </p>
                </div>
              </div>
              {exportedFiles.markdown ? (
                <a
                  href={`http://localhost:8000${exportedFiles.markdown}`}
                  download
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                >
                  <Download className="mr-2 h-4 w-4" />
                  ダウンロード
                </a>
              ) : (
                <button
                  onClick={handleExportMarkdown}
                  disabled={exporting}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {exporting ? (
                    <Loader2 className="animate-spin mr-2 h-4 w-4" />
                  ) : (
                    <FileDown className="mr-2 h-4 w-4" />
                  )}
                  エクスポート
                </button>
              )}
            </div>
          </div>

          {/* PDF エクスポート */}
          <div className="border rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <FileDown className="h-8 w-8 text-red-600" />
                <div>
                  <h3 className="font-medium text-gray-900">PDF</h3>
                  <p className="text-sm text-gray-500">
                    印刷や共有に最適
                  </p>
                </div>
              </div>
              {exportedFiles.pdf ? (
                <a
                  href={`http://localhost:8000${exportedFiles.pdf}`}
                  download
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                >
                  <Download className="mr-2 h-4 w-4" />
                  ダウンロード
                </a>
              ) : (
                <button
                  onClick={handleExportPdf}
                  disabled={exporting}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {exporting ? (
                    <Loader2 className="animate-spin mr-2 h-4 w-4" />
                  ) : (
                    <FileDown className="mr-2 h-4 w-4" />
                  )}
                  エクスポート
                </button>
              )}
            </div>
          </div>
        </div>

        {/* 完了メッセージ */}
        {(exportedFiles.markdown || exportedFiles.pdf) && (
          <div className="mt-8 bg-green-50 rounded-md p-4">
            <p className="text-sm text-green-800">
              ✅ エクスポートが完了しました!ダウンロードボタンからファイルを取得できます。
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
