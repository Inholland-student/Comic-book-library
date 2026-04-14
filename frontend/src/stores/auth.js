import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref(null)
  const isLoggedIn = computed(() => currentUser.value !== null)

  const login = (user) => {
    currentUser.value = user
  }

  const logout = () => {
    currentUser.value = null
  }

  return {
    currentUser,
    isLoggedIn,
    login,
    logout
  }
})
