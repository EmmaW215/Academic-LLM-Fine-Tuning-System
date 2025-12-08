'use client'

import { useEffect, useState } from 'react'
import { apiClient, HealthStatus } from '@/lib/api'

export default function StatusCard() {
  const [status, setStatus] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const health = await apiClient.getHealth()
        setStatus(health)
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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <div className="text-sm text-gray-600 dark:text-gray-400">API Status</div>
          <div className={`text-lg font-medium ${status?.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
            {status?.status === 'healthy' ? '✅ Healthy' : '❌ Unhealthy'}
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Initialized</div>
          <div className={`text-lg font-medium ${status?.initialized ? 'text-green-600' : 'text-yellow-600'}`}>
            {status?.initialized ? '✅ Yes' : '⏳ No'}
          </div>
        </div>
        <div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Index Loaded</div>
          <div className={`text-lg font-medium ${status?.index_loaded ? 'text-green-600' : 'text-yellow-600'}`}>
            {status?.index_loaded ? '✅ Yes' : '⏳ No'}
          </div>
        </div>
      </div>
    </div>
  )
}

