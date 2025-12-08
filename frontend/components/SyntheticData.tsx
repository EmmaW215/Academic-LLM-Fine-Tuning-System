'use client'

import { useState } from 'react'
import { PenTool, Loader2 } from 'lucide-react'
import { apiClient } from '@/lib/api'

export default function SyntheticData() {
  const [numPapers, setNumPapers] = useState(50)
  const [qaPerPaper, setQaPerPaper] = useState(5)
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<string>('')
  const [preview, setPreview] = useState<string>('')

  const handleGenerate = async () => {
    setLoading(true)
    setStatus('Starting synthetic data generation...')
    setPreview('')

    try {
      const response = await apiClient.generateSynthetic({
        num_papers: numPapers,
        qa_per_paper: qaPerPaper,
      })
      setStatus(response.status)
      setPreview(response.preview)
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'An error occurred'
      setStatus(`❌ Error: ${errorMessage}`)
      if (errorMessage.includes('API key')) {
        setPreview('💡 Please set OPENAI_API_KEY environment variable on the backend server.')
      } else {
        setPreview('')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          <strong>Note:</strong> Synthetic data generation runs in the background and may take a while.
          Requires OPENAI_API_KEY to be set on the backend server.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Papers to Process</label>
          <input
            type="number"
            min="10"
            max="100"
            step="10"
            value={numPapers}
            onChange={(e) => setNumPapers(parseInt(e.target.value) || 50)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Q&A per Paper</label>
          <input
            type="number"
            min="1"
            max="10"
            step="1"
            value={qaPerPaper}
            onChange={(e) => setQaPerPaper(parseInt(e.target.value) || 5)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
          />
        </div>
      </div>

      <button
        onClick={handleGenerate}
        disabled={loading}
        className="w-full px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin h-5 w-5" />
            Generating...
          </>
        ) : (
          <>
            <PenTool className="h-5 w-5" />
            Generate Q&A Data
          </>
        )}
      </button>

      {status && (
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <p className="text-sm whitespace-pre-wrap">{status}</p>
        </div>
      )}

      {preview && (
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="prose dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: preview.replace(/\n/g, '<br>') }} />
        </div>
      )}
    </div>
  )
}

