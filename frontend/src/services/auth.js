import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const authService = {
  register: async (username, email, password) => {
    const response = await axios.post(`${API_BASE_URL}/auth/register`, {
      username,
      email,
      password
    }, { withCredentials: true })
    return response.data
  },

  login: async (username, password) => {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, {
      username,
      password
    }, { withCredentials: true })
    return response.data
  },

  logout: async () => {
    const response = await axios.post(`${API_BASE_URL}/auth/logout`, {}, {
      withCredentials: true
    })
    return response.data
  },

  getCurrentUser: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/me`, {
        withCredentials: true
      })
      return response.data
    } catch (error) {
      return null
    }
  }
}

export default authService
