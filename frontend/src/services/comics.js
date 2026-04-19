import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const comicsService = {
  getAll: async (page = 1, perPage = 20) => {
    const response = await axios.get(`${API_BASE_URL}/comics`, {
      params: { page, per_page: perPage },
      withCredentials: true
    })
    return response.data
  },

  getById: async (id) => {
    const response = await axios.get(`${API_BASE_URL}/comics/${id}`, {
      withCredentials: true
    })
    return response.data
  },

  create: async (serie, number, title) => {
    const response = await axios.post(`${API_BASE_URL}/comics`, {
      serie,
      number,
      title
    }, { withCredentials: true })
    return response.data
  },

  update: async (id, serie, number, title) => {
    const response = await axios.put(`${API_BASE_URL}/comics/${id}`, {
      serie,
      number,
      title
    }, { withCredentials: true })
    return response.data
  },

  delete: async (id) => {
    const response = await axios.delete(`${API_BASE_URL}/comics/${id}`, {
      withCredentials: true
    })
    return response.data
  }
}

export default comicsService
