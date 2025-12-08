'use client'

import { useState } from 'react'
import { apiClient, ChatResponse } from '@/lib/api'
import { Send, Loader2 } from 'lucide-react'

export default function ChatInterface() {
  const [message, setMessage] = useState('')
  const [history, setHistory] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([])
  const [loading, setLoading] = useState(false)
  const [modelType, setModelType] = useState<'base' | 'finetuned'>('finetuned')
  const [useRAG, setUseRAG] = useState(true)

  const handleSend = async () => {
    if (!message.trim() || loading) return

    const userMessage = message.trim()
    setMessage('')
    setHistory([...history, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response: ChatResponse = await apiClient.chat({
        message: userMessage,
        model_type: modelType,
        use_rag: useRAG,
      })

      // Handle both response formats
      const assistantMessage = response.message || response.response || 'No response received'
      setHistory([
        ...history,
        { role: 'user', content: userMessage },
        { role: 'assistant', content: assistantMessage },
      ])
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'An error occurred'
      setHistory([
        ...history,
        { role: 'user', content: userMessage },
        { role: 'assistant', content: `❌ Error: ${errorMessage}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium">Model:</label>
          <select
            value={modelType}
            onChange={(e) => setModelType(e.target.value as 'base' | 'finetuned')}
            className="px-3 py-1 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
          >
            <option value="base">Base</option>
            <option value="finetuned">Fine-tuned</option>
          </select>
        </div>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={useRAG}
            onChange={(e) => setUseRAG(e.target.checked)}
            className="rounded"
          />
          <span className="text-sm">Use RAG Context</span>
        </label>
      </div>

      {/* Chat History */}
      <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 h-96 overflow-y-auto">
        {history.length === 0 ? (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-20">
            Start a conversation by typing a message below
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    msg.role === 'user'
                      ? 'bg-primary-500 text-white'
                      : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-gray-800 rounded-lg px-4 py-2 border border-gray-200 dark:border-gray-700">
                  <Loader2 className="animate-spin h-5 w-5" />
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder="Ask a question..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600"
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !message.trim()}
          className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? <Loader2 className="animate-spin h-5 w-5" /> : <Send className="h-5 w-5" />}
          Send
        </button>
      </div>
    </div>
  )
}

