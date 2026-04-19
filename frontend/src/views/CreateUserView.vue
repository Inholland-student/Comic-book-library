<template>
  <div class="page-wrap">
    <div class="card">
      <h1>Add user</h1>
      <p v-if="isSuper" class="hint">creates an admin account</p>
      <p v-else-if="isAdmin" class="hint">pick role: admin or friend</p>

      <form v-if="allowed" @submit.prevent="submit">
        <div class="field">
          <label for="u">Username</label>
          <input id="u" v-model="form.username" required />
        </div>
        <div class="field">
          <label for="e">Email</label>
          <input id="e" v-model="form.email" type="email" required />
        </div>
        <div class="field">
          <label for="p">Password</label>
          <input id="p" v-model="form.password" type="password" required minlength="8" />
        </div>
        <div v-if="isAdmin" class="field">
          <label for="r">Role</label>
          <select id="r" v-model="form.role">
            <option value="friend">friend</option>
            <option value="admin">admin</option>
          </select>
        </div>
        <p v-if="error" class="err">{{ error }}</p>
        <button type="submit" class="btn" :disabled="loading">{{ loading ? 'Saving…' : 'Create' }}</button>
      </form>
      <p v-else class="err">you need admin access</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import authService from '@/services/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  role: 'friend'
})
const error = ref('')
const loading = ref(false)

const role = computed(() => authStore.currentUser?.role)
const isSuper = computed(() => role.value === 'super_admin')
const isAdmin = computed(() => role.value === 'admin')
const allowed = computed(() => isSuper.value || isAdmin.value)

onMounted(() => {
  if (!authStore.isLoggedIn) router.replace('/login')
  else if (!allowed.value) router.replace('/')
})

async function submit () {
  loading.value = true
  error.value = ''
  try {
    const payload = {
      username: form.value.username.trim(),
      email: form.value.email.trim(),
      password: form.value.password
    }
    if (isAdmin.value) payload.role = form.value.role
    if (isSuper.value) payload.role = 'admin'
    await authService.createStaffUser(payload)
    router.push('/comics')
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-wrap {
  min-height: 60vh;
  display: flex;
  justify-content: center;
  padding: 2rem;
}
.card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
h1 { margin-top: 0; }
.hint { color: #666; font-size: 0.9rem; }
.field { margin-bottom: 1rem; }
.field label { display: block; margin-bottom: 0.35rem; font-weight: 600; }
.field input, .field select {
  width: 100%;
  padding: 0.5rem;
  box-sizing: border-box;
}
.btn {
  width: 100%;
  padding: 0.6rem;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}
.btn:disabled { opacity: 0.5; }
.err { color: #a00; margin: 0.5rem 0; }
</style>
