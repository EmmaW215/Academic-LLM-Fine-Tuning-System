'use client'

import { useState } from 'react'
import { apiClient } from '@/lib/api'
import { Loader2, Rocket } from 'lucide-react'

export default function InitializeSystem() {
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<string>('')

  const handleInitialize = async () => {
    setLoading(true)
    setStatus('Initializing modules...')

    try {
      // Check if already initialized
      const health = await apiClient.getHealth()
      if (health.initialized) {
        setStatus('✅ System already initialized!')
        setLoading(false)
        return
      }

      // For now, initialization is handled by the backend on startup
      // This is just a status check
      setStatus('✅ System initialization is handled automatically by the backend.')
    } catch (error: any) {
      setStatus(`❌ Error: ${error.message || 'Failed to initialize'}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          <strong>Note:</strong> System initialization is handled automatically when the backend starts.
          The modules are loaded on-demand when you use features like Chat or Search.
        </p>
      </div>

      <button
        onClick={handleInitialize}
        disabled={loading}
        className="w-full px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin h-5 w-5" />
            Initializing...
          </>
        ) : (
          <>
            <Rocket className="h-5 w-5" />
            Check System Status
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

