import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const comicsService = {
  getAll: async () => {
    const response = await axios.get(`${API_BASE_URL}/comics`, {
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
