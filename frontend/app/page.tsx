'use client'

import { useState } from 'react'
import ChatInterface from '@/components/ChatInterface'
import SearchInterface from '@/components/SearchInterface'
import StatusCard from '@/components/StatusCard'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'search'>('chat')

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            🎓 Academic LLM Fine-Tuning System
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Build a custom academic Q&A assistant using RAG and QLoRA fine-tuning
          </p>
        </div>

        {/* Status Card */}
        <StatusCard />

        {/* Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg mb-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('chat')}
                className={`py-4 px-6 font-medium text-sm ${
                  activeTab === 'chat'
                    ? 'border-b-2 border-primary-500 text-primary-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                💬 Chat & Compare
              </button>
              <button
                onClick={() => setActiveTab('search')}
                className={`py-4 px-6 font-medium text-sm ${
                  activeTab === 'search'
                    ? 'border-b-2 border-primary-500 text-primary-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🔍 RAG Search
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'chat' && <ChatInterface />}
            {activeTab === 'search' && <SearchInterface />}
          </div>
        </div>
      </div>
    </main>
  )
}

