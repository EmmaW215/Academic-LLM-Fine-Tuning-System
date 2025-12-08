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

export interface DataCollectionRequest {
  category?: string
  query?: string
  num_papers?: number
}

export interface DataCollectionResponse {
  status: string
  papers_collected: number
  preview: string
}

export interface IndexBuildResponse {
  status: string
  chunks_indexed: number
  documents_processed: number
}

export interface SyntheticDataRequest {
  num_papers?: number
  qa_per_paper?: number
}

export interface SyntheticDataResponse {
  status: string
  qa_pairs_generated: number
  filepath: string
  preview: string
}

export interface FineTuningRequest {
  epochs?: number
  batch_size?: number
  learning_rate?: number
}

export interface FineTuningResponse {
  status: string
  train_loss?: number
  train_runtime?: number
  output_dir?: string
  message: string
}

export interface PipelineStatus {
  status: string
  papers_collected: number
  chunks_indexed: number
  qa_pairs_generated: number
  model_trained: boolean
  last_updated?: string
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

  // Get pipeline status
  async getStatus(): Promise<PipelineStatus> {
    const response = await api.get<PipelineStatus>('/status')
    return response.data
  },

  // Data collection
  async collectPapers(request: DataCollectionRequest): Promise<DataCollectionResponse> {
    const response = await api.post<DataCollectionResponse>('/collect', {
      category: request.category || 'cs.CL',
      query: request.query || null,
      num_papers: request.num_papers || 50,
    })
    return response.data
  },

  // Build index
  async buildIndex(): Promise<IndexBuildResponse> {
    const response = await api.post<IndexBuildResponse>('/build-index')
    return response.data
  },

  // Generate synthetic data
  async generateSynthetic(request: SyntheticDataRequest): Promise<SyntheticDataResponse> {
    const response = await api.post<SyntheticDataResponse>('/generate-synthetic', {
      num_papers: request.num_papers || 50,
      qa_per_paper: request.qa_per_paper || 5,
    })
    return response.data
  },

  // Fine-tune model
  async finetune(request: FineTuningRequest): Promise<FineTuningResponse> {
    const response = await api.post<FineTuningResponse>('/finetune', {
      epochs: request.epochs || 3,
      batch_size: request.batch_size || 2,
      learning_rate: request.learning_rate || 0.0002,
    })
    return response.data
  },
}

export default apiClient

