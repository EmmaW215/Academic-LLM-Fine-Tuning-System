'use client'

import { useState } from 'react'
import { apiClient, SearchResult } from '@/lib/api'
import { Search, Loader2 } from 'lucide-react'

export default function SearchInterface() {
  const [query, setQuery] = useState('')
  const [searchType, setSearchType] = useState<'hybrid' | 'vector' | 'keyword'>('hybrid')
  const [topK, setTopK] = useState(5)
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)

  const handleSearch = async () => {
    if (!query.trim() || loading) return

    setLoading(true)
    try {
      const response = await apiClient.search({
        query: query.trim(),
        top_k: topK,
        search_type: searchType,
      })
      setResults(response.results)
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'An error occurred'
      alert(`Error: ${errorMessage}`)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Search Controls */}
      <div className="space-y-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search for papers, concepts, or topics..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600"
            disabled={loading}
          />
          <button
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin h-5 w-5" /> : <Search className="h-5 w-5" />}
            Search
          </button>
        </div>

        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium">Search Type:</label>
            <select
              value={searchType}
              onChange={(e) => setSearchType(e.target.value as any)}
              className="px-3 py-1 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
            >
              <option value="hybrid">Hybrid</option>
              <option value="vector">Vector</option>
              <option value="keyword">Keyword</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium">Top K:</label>
            <input
              type="number"
              min="1"
              max="20"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value) || 5)}
              className="w-20 px-2 py-1 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
            />
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="space-y-4">
        {loading && (
          <div className="text-center py-8">
            <Loader2 className="animate-spin h-8 w-8 mx-auto text-primary-500" />
            <p className="mt-2 text-gray-600 dark:text-gray-400">Searching...</p>
          </div>
        )}

        {!loading && results.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-4">
              Found {results.length} result{results.length !== 1 ? 's' : ''}
            </h3>
            <div className="space-y-4">
              {results.map((result, idx) => (
                <div
                  key={result.chunk_id}
                  className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="text-sm font-medium text-primary-600 dark:text-primary-400">
                      Result {idx + 1} • {result.doc_id}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      Score: {result.score.toFixed(4)}
                    </div>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300">{result.text}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {!loading && results.length === 0 && query && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            No results found. Try a different query.
          </div>
        )}

        {!loading && !query && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            Enter a search query to find relevant papers and content.
          </div>
        )}
      </div>
    </div>
  )
}

