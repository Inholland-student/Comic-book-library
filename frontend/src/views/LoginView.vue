<template>
  <div class="login-container">
    <div class="login-card">
      <h1>Comic Book Library</h1>
      
      <div v-if="showRegister" class="form-section">
        <h2>Create Account</h2>
        <form @submit.prevent="handleRegister">
          <div class="form-group">
            <label for="reg-username">Username</label>
            <input 
              id="reg-username"
              v-model="registerForm.username" 
              type="text" 
              required 
              placeholder="Choose a username"
            />
          </div>
          <div class="form-group">
            <label for="reg-email">Email</label>
            <input 
              id="reg-email"
              v-model="registerForm.email" 
              type="email" 
              required 
              placeholder="your@email.com"
            />
          </div>
          <div class="form-group">
            <label for="reg-password">Password</label>
            <input 
              id="reg-password"
              v-model="registerForm.password" 
              type="password" 
              required 
              placeholder="At least 8 characters"
            />
          </div>
          <div v-if="error" class="error-message">{{ error }}</div>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Creating...' : 'Create Account' }}
          </button>
          <p class="form-footer">
            Already have an account? 
            <button type="button" @click="showRegister = false" class="link-btn">
              Sign In
            </button>
          </p>
        </form>
      </div>

      <div v-else class="form-section">
        <h2>Sign In</h2>
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="username">Username</label>
            <input 
              id="username"
              v-model="loginForm.username" 
              type="text" 
              required 
              placeholder="Your username"
              autocomplete="username"
            />
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input 
              id="password"
              v-model="loginForm.password" 
              type="password" 
              required 
              placeholder="Your password"
              autocomplete="current-password"
            />
          </div>
          <div v-if="error" class="error-message">{{ error }}</div>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Signing In...' : 'Sign In' }}
          </button>
          <p class="form-footer">
            New here? 
            <button type="button" @click="showRegister = true" class="link-btn">
              Create Account
            </button>
          </p>
        </form>
      </div>
    </div>

    <div class="info-section">
      <h3>Demo Credentials</h3>
      <p><strong>Admin User:</strong> admin / changeme</p>
      <p><strong>Super Admin:</strong> super_user / changeme</p>
      <p><strong>Regular User:</strong> Create a new account</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import authService from '@/services/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const showRegister = ref(false)
const loading = ref(false)
const error = ref('')

const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  email: '',
  password: ''
})

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const { username, password } = loginForm.value
    const user = await authService.login(username, password)
    authStore.login(user)
    router.push('/comics')
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'Login failed'
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  try {
    const { username, email, password } = registerForm.value
    const user = await authService.register(username, email, password)
    authStore.login(user)
    router.push('/comics')
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.login-card h1 {
  color: white;
  margin-bottom: 2rem;
  font-size: 2.5rem;
}

.form-section {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

.form-section h2 {
  margin-top: 0;
  color: #333;
  text-align: center;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 600;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn:hover:not(:disabled) {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border: 1px solid #f5c6cb;
}

.form-footer {
  text-align: center;
  margin-top: 1.5rem;
  color: #666;
}

.link-btn {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  text-decoration: underline;
  font-weight: 600;
}

.info-section {
  flex: 1;
  padding: 2rem;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.info-section h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.info-section p {
  margin: 0.5rem 0;
  font-family: monospace;
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }

  .info-section {
    order: -1;
    background: rgba(0, 0, 0, 0.1);
    padding: 1rem;
  }

  .login-card h1 {
    font-size: 2rem;
  }
}
</style>
