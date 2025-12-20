/**
 * API client for RAG system backend.
 * Handles all HTTP requests to the backend.
 */

import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Generate a unique session ID for conversation memory
const SESSION_ID = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,
})

/**
 * Upload a PDF document to the backend.
 * @param {File} file - PDF file to upload
 * @returns {Promise} Upload response with chunks_created and total_tokens
 */
export const uploadDocument = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Upload failed')
  }
}

/**
 * Send a query to the RAG system with conversation memory.
 * @param {string} query - User question
 * @returns {Promise} Chat response with answer and citations
 */
export const sendQuery = async (query) => {
  try {
    const response = await api.post('/chat', {
      query: query,
      conversation_id: SESSION_ID,
    })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Query failed')
  }
}

/**
 * Check backend health status.
 * @returns {Promise} Health check response
 */
export const checkHealth = async () => {
  try {
    const response = await api.get('/health', { timeout: 5000 })
    return response.data
  } catch (error) {
    console.error('Health check error:', error.message)
    return { status: 'degraded', error: error.message }
  }
}

/**
 * Get the current session ID
 * @returns {string} Session ID
 */
export const getSessionId = () => SESSION_ID

export default api
