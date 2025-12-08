'use client'

import { useState } from 'react'
import ChatInterface from '@/components/ChatInterface'
import SearchInterface from '@/components/SearchInterface'
import StatusCard from '@/components/StatusCard'
import InitializeSystem from '@/components/InitializeSystem'
import DataCollection from '@/components/DataCollection'
import SyntheticData from '@/components/SyntheticData'
import FineTuning from '@/components/FineTuning'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'initialize' | 'data' | 'search' | 'synthetic' | 'finetune' | 'chat'>('initialize')

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
            <nav className="flex -mb-px overflow-x-auto">
              <button
                onClick={() => setActiveTab('initialize')}
                className={`py-4 px-4 font-medium text-sm whitespace-nowrap ${
                  activeTab === 'initialize'
                    ? 'border-b-2 border-primary-500 text-primary-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🚀 Initialize
              </button>
              <button
                onClick={() => setActiveTab('data')}
                className={`py-4 px-4 font-medium text-sm whitespace-nowrap ${
                  activeTab === 'data'
                    ? 'border-b-2 border-primary-500 text-primary-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📚 Data Collection
              </button>
              <button
                onClick={() => setActiveTab('search')}
                className={`py-4 px-4 font-medium text-sm whitespace-nowrap ${
                  activeTab === 'search'
                    ? 'border-b-2 border-primary-500 text-primary-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🔍 RAG Search
              </button>
              <button
                onClick={() => setActiveTab('synthetic')}
                className={`py-4 px-4 font-medium text-sm whitespace-nowrap ${
                  activeTab === 'synthetic'
                    ? 'border-b-2 border-primary-500 text-primary-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                ✏️ Synthetic Data
              </button>
              <button
                onClick={() => setActiveTab('finetune')}
                className={`py-4 px-4 font-medium text-sm whitespace-nowrap ${
                  activeTab === 'finetune'
                    ? 'border-b-2 border-primary-500 text-primary-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🔧 Fine-Tuning
              </button>
              <button
                onClick={() => setActiveTab('chat')}
                className={`py-4 px-4 font-medium text-sm whitespace-nowrap ${
                  activeTab === 'chat'
                    ? 'border-b-2 border-primary-500 text-primary-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                💬 Chat & Compare
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'initialize' && <InitializeSystem />}
            {activeTab === 'data' && <DataCollection />}
            {activeTab === 'search' && <SearchInterface />}
            {activeTab === 'synthetic' && <SyntheticData />}
            {activeTab === 'finetune' && <FineTuning />}
            {activeTab === 'chat' && <ChatInterface />}
          </div>
        </div>
      </div>
    </main>
  )
}

