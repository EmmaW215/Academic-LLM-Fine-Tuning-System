import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds for model inference
})

export interface HealthStatus {
  status: string
  initialized: boolean
  index_loaded: boolean
}

export interface SearchRequest {
  query: string
  top_k?: number
  search_type?: 'hybrid' | 'vector' | 'keyword'
}

export interface SearchResult {
  chunk_id: string
  doc_id: string
  text: string
  score: number
  metadata?: Record<string, any>
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
  search_type: string
  total_results: number
}

export interface ChatRequest {
  message: string
  model_type?: 'base' | 'finetuned'
  use_rag?: boolean
  max_tokens?: number
  temperature?: number
}

export interface ChatResponse {
  message?: string  // Some APIs return 'message'
  response?: string  // Some APIs return 'response'
  model_used?: string
  model_type?: string
  latency_ms: number
  sources?: SearchResult[]
}

export const apiClient = {
  // Health check
  async getHealth(): Promise<HealthStatus> {
    const response = await api.get<HealthStatus>('/health')
    return response.data
  },

  // Search
  async search(request: SearchRequest): Promise<SearchResponse> {
    const response = await api.post<SearchResponse>('/search', {
      query: request.query,
      top_k: request.top_k || 5,
      search_type: request.search_type || 'hybrid',
    })
    return response.data
  },

  // Chat
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/chat', {
      message: request.message,
      model_type: request.model_type || 'finetuned',
      use_rag: request.use_rag !== false,
      max_tokens: request.max_tokens || 512,
      temperature: request.temperature || 0.7,
    })
    return response.data
  },

  // Compare models
  async compare(question: string): Promise<string> {
    const response = await api.post<{ comparison: string }>('/compare', null, {
      params: { question },
    })
    return response.data.comparison
  },
}

export default apiClient

