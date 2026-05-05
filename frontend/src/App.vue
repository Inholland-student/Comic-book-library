<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="nav-brand">📚 Comic Library</router-link>
        
        <div class="nav-menu">
          <router-link 
            v-if="authStore.isLoggedIn"
            to="/comics" 
            class="nav-link"
          >
            Comics
          </router-link>
          <router-link
            v-if="authStore.isLoggedIn && canAddUsers"
            to="/users/create"
            class="nav-link"
          >
            Add user
          </router-link>
          
          <div v-if="authStore.isLoggedIn" class="nav-user">
            <span class="user-info">
              {{ authStore.currentUser.username }}
              <span class="user-role">{{ formatRole(authStore.currentUser.role) }}</span>
            </span>
            <button @click="handleLogout" class="nav-link logout-btn">
              Logout
            </button>
          </div>
          
          <div v-else class="nav-auth">
            <router-link to="/login" class="nav-link">
              Sign In
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import authService from '@/services/auth.js'

const authStore = useAuthStore()
const router = useRouter()

const canAddUsers = computed(() => {
  const r = authStore.currentUser?.role
  return r === 'admin' || r === 'super_admin'
})

const formatRole = (role) => {
  return role.charAt(0).toUpperCase() + role.slice(1).replace('_', ' ')
}

const handleLogout = async () => {
  try {
    await authService.logout()
    authStore.logout()
    router.push('/')
  } catch (err) {
    console.error('Logout error:', err)
    // Still clear auth even if logout request fails
    authStore.logout()
    router.push('/')
  }
}

// Initialize current user on app load
onMounted(async () => {
  try {
    const user = await authService.getCurrentUser()
    if (user) {
      authStore.login(user)
    }
  } catch (err) {
    console.log('Not authenticated')
  }
})
</script>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 50;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  font-size: 1.3rem;
  font-weight: 700;
  color: #667eea;
  text-decoration: none;
  display: flex;
  align-items: center;
}

.nav-menu {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.nav-link {
  color: #333;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover {
  color: #667eea;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: 0.9rem;
}

.user-role {
  font-size: 0.8rem;
  color: #666;
  display: block;
}

.logout-btn {
  background: #dc3545;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.logout-btn:hover {
  background: #c82333;
  color: white;
}

.nav-auth {
  display: flex;
  gap: 1rem;
}

.main-content {
  flex: 1;
  background: #f5f5f5;
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .nav-menu {
    width: 100%;
    justify-content: space-between;
  }

  .nav-user {
    flex-direction: column;
    gap: 0.5rem;
  }

  .user-info {
    align-items: center;
  }
}
</style>
