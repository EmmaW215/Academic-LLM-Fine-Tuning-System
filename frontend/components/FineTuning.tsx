'use client'

import { useState } from 'react'
import { Wrench, Loader2 } from 'lucide-react'
import { apiClient } from '@/lib/api'

export default function FineTuning() {
  const [epochs, setEpochs] = useState(3)
  const [batchSize, setBatchSize] = useState(2)
  const [learningRate, setLearningRate] = useState(0.0002)
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<string>('')

  const handleTrain = async () => {
    setLoading(true)
    setStatus('Starting fine-tuning...')

    try {
      const response = await apiClient.finetune({
        epochs,
        batch_size: batchSize,
        learning_rate: learningRate,
      })
      setStatus(response.status + '\n\n' + response.message)
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'An error occurred'
      setStatus(`❌ Error: ${errorMessage}`)
      if (errorMessage.includes('dataset') || errorMessage.includes('empty')) {
        setStatus(`❌ Error: ${errorMessage}\n\n💡 Please generate synthetic data first.`)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
        <p className="text-sm text-orange-800 dark:text-orange-200">
          <strong>Warning:</strong> Fine-tuning runs in the background and will take several hours.
          Ensure you have generated synthetic data first. The process requires GPU resources.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Epochs</label>
          <input
            type="number"
            min="1"
            max="10"
            step="1"
            value={epochs}
            onChange={(e) => setEpochs(parseInt(e.target.value) || 3)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Batch Size</label>
          <input
            type="number"
            min="1"
            max="8"
            step="1"
            value={batchSize}
            onChange={(e) => setBatchSize(parseInt(e.target.value) || 2)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Learning Rate</label>
          <input
            type="number"
            min="0.0001"
            max="0.001"
            step="0.0001"
            value={learningRate}
            onChange={(e) => setLearningRate(parseFloat(e.target.value) || 0.0002)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
          />
        </div>
      </div>

      <button
        onClick={handleTrain}
        disabled={loading}
        className="w-full px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin h-5 w-5" />
            Training...
          </>
        ) : (
          <>
            <Wrench className="h-5 w-5" />
            Start Fine-Tuning
          </>
        )}
      </button>

      {status && (
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <p className="text-sm whitespace-pre-wrap">{status}</p>
        </div>
      )}
    </div>
  )
}

