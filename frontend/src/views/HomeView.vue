<template>
  <div class="home">
    <div class="hero">
      <h1>Comic Book Library</h1>
      <p class="subtitle">A secure, role-based comic management system</p>
      
      <div v-if="authStore.isLoggedIn" class="authenticated">
        <p class="welcome">Welcome, {{ authStore.currentUser.username }}!</p>
        <div class="role-badge">
          <span>Role: {{ formatRole(authStore.currentUser.role) }}</span>
        </div>
        <router-link to="/comics" class="btn btn-primary btn-large">
          Browse Comics →
        </router-link>
      </div>
      
      <div v-else class="unauthenticated">
        <p>Sign in to access the comic library and discover amazing stories.</p>
        <router-link to="/login" class="btn btn-primary btn-large">
          Sign In
        </router-link>
      </div>
    </div>

    <div v-if="!authStore.isLoggedIn" class="features">
      <h2>Features</h2>
      <div class="features-grid">
        <div class="feature-card">
          <h3>📚 Browse Comics</h3>
          <p>Explore a curated collection of comic books and graphic novels.</p>
        </div>
        <div class="feature-card">
          <h3>🔐 Secure Access</h3>
          <p>Your data is protected with industry-standard JWT authentication.</p>
        </div>
        <div class="feature-card">
          <h3>👥 Role-Based Control</h3>
          <p>Different access levels for admins, librarians, and readers.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth.js'

const authStore = useAuthStore()

const formatRole = (role) => {
  return role.charAt(0).toUpperCase() + role.slice(1).replace('_', ' ')
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.hero {
  padding: 4rem 2rem;
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.hero h1 {
  font-size: 3rem;
  margin: 0 0 1rem 0;
  font-weight: 700;
}

.subtitle {
  font-size: 1.3rem;
  margin-bottom: 2rem;
  opacity: 0.95;
}

.authenticated,
.unauthenticated {
  margin-top: 2rem;
}

.welcome {
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.role-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background: white;
  color: #667eea;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  margin-top: 1rem;
}

.features {
  max-width: 1000px;
  margin: 4rem auto;
  padding: 2rem;
}

.features h2 {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 2rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-card h3 {
  font-size: 1.3rem;
  margin-bottom: 0.5rem;
}

.feature-card p {
  margin: 0;
  opacity: 0.9;
}
</style>
