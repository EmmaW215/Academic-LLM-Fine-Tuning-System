'use client'

import { useEffect, useState } from 'react'
import { apiClient, HealthStatus, PipelineStatus } from '@/lib/api'

export default function StatusCard() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const [healthData, pipelineData] = await Promise.all([
          apiClient.getHealth(),
          apiClient.getStatus(),
        ])
        setHealth(healthData)
        setPipelineStatus(pipelineData)
      } catch (error) {
        console.error('Failed to fetch status:', error)
      } finally {
        setLoading(false)
      }
    }

    checkStatus()
    const interval = setInterval(checkStatus, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
        <div className="animate-pulse">Loading status...</div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">System Status</h2>
      
      {/* API Health */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <div className="text-sm text-gray-600 dark:text-gray-400">API Status</div>
          <div className={`text-lg font-medium ${health?.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
            {health?.status === 'healthy' ? '✅ Healthy' : '❌ Unhealthy'}
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Initialized</div>
          <div className={`text-lg font-medium ${health?.initialized ? 'text-green-600' : 'text-yellow-600'}`}>
            {health?.initialized ? '✅ Yes' : '⏳ No'}
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Index Loaded</div>
          <div className={`text-lg font-medium ${health?.index_loaded ? 'text-green-600' : 'text-yellow-600'}`}>
            {health?.index_loaded ? '✅ Yes' : '⏳ No'}
          </div>
        </div>
      </div>

      {/* Pipeline Status */}
      {pipelineStatus && (
        <div className="border-t border-gray-200 dark:border-gray-700 pt-4 mt-4">
          <h3 className="text-lg font-semibold mb-3">Pipeline Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Papers Collected</div>
              <div className="text-lg font-medium">{pipelineStatus.papers_collected}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Chunks Indexed</div>
              <div className="text-lg font-medium">{pipelineStatus.chunks_indexed}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400">QA Pairs Generated</div>
              <div className="text-lg font-medium">{pipelineStatus.qa_pairs_generated}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Model Trained</div>
              <div className={`text-lg font-medium ${pipelineStatus.model_trained ? 'text-green-600' : 'text-yellow-600'}`}>
                {pipelineStatus.model_trained ? '✅ Yes' : '⏳ No'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

