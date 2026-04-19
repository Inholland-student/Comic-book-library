import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

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
  },

  createStaffUser: async ({ username, email, password, role }) => {
    const body = { username, email, password }
    if (role !== undefined && role !== '') body.role = role
    const response = await axios.post(`${API_BASE_URL}/auth/users`, body, {
      withCredentials: true
    })
    return response.data
  }
}

export default authService
