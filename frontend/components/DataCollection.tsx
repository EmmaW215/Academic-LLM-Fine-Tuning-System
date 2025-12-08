'use client'

import { useState } from 'react'
import { Database, Download, Loader2 } from 'lucide-react'

export default function DataCollection() {
  const [category, setCategory] = useState('cs.CL')
  const [query, setQuery] = useState('')
  const [numPapers, setNumPapers] = useState(50)
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<string>('')
  const [preview, setPreview] = useState<string>('')

  const handleCollect = async () => {
    setLoading(true)
    setStatus('This feature requires backend API endpoints for data collection.')
    setPreview('Please use the Gradio UI for data collection, or add API endpoints to the backend.')
    setLoading(false)
  }

  const handleBuildIndex = async () => {
    setLoading(true)
    setStatus('This feature requires backend API endpoints for index building.')
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
        <p className="text-sm text-yellow-800 dark:text-yellow-200">
          <strong>Note:</strong> Data collection and index building are long-running tasks that require backend API endpoints.
          For now, please use the Gradio UI (running on the GPU server) for these features, or we can add API endpoints to support them.
        </p>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Collect Papers from arXiv</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">arXiv Category</label>
            <input
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
              placeholder="cs.CL"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Search Query (optional)</label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
              placeholder="e.g., transformer attention"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Number of Papers</label>
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
        </div>

        <button
          onClick={handleCollect}
          disabled={loading}
          className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin h-5 w-5" />
              Collecting...
            </>
          ) : (
            <>
              <Download className="h-5 w-5" />
              Collect Papers
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

      <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
        <h3 className="text-lg font-semibold mb-4">Build RAG Index</h3>
        <button
          onClick={handleBuildIndex}
          disabled={loading}
          className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin h-5 w-5" />
              Building...
            </>
          ) : (
            <>
              <Database className="h-5 w-5" />
              Process & Build Index
            </>
          )}
        </button>
      </div>
    </div>
  )
}

