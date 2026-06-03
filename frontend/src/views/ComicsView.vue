<template>
  <div class="comics-container">
    <div class="comics-header">
      <h1>Comic Book Library</h1>
      <button v-if="authStore.currentUser && isAdmin" @click="showCreateForm = true" class="btn btn-primary">
        + Add Comic
      </button>
    </div>

    <div v-if="comicsStore.hasMore" class="load-more">
      <button class="btn btn-primary" @click="comicsStore.loadMoreComics" :disabled="comicsStore.loading">
        {{ comicsStore.loading ? 'Loading more comics...' : 'Load more comics' }}
      </button>
    </div>

    <!-- Create/Edit Form Modal -->
    <div v-if="showCreateForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ editingComic ? 'Edit Comic' : 'Add New Comic' }}</h2>
          <button class="close-btn" @click="closeForm">&times;</button>
        </div>
        <form @submit.prevent="handleSubmit" class="comic-form">
          <div class="form-group">
            <label for="serie">Serie:</label>
            <input id="serie" v-model="formData.serie" type="text" required placeholder="e.g., X-Men" />
          </div>
          <div class="form-group">
            <label for="number">Number:</label>
            <input id="number" v-model="formData.number" type="text" required placeholder="Issue number" />
          </div>
          <div class="form-group">
            <label for="title">Title:</label>
            <input id="title" v-model="formData.title" type="text" required placeholder="Comic title" />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="comicsStore.loading">
              {{ comicsStore.loading ? 'Saving...' : 'Save Comic' }}
            </button>
            <button type="button" @click="closeForm" class="btn btn-secondary">
              Cancel
            </button>
          </div>
          <div v-if="formError" class="error-message">{{ formError }}</div>
        </form>
      </div>
    </div>

    <!-- Comics List -->
    <div v-if="comicsStore.loading && comicsStore.comics.length === 0" class="loading">
      Loading comics...
    </div>

    <div v-else-if="comicsStore.error" class="error-message">
      {{ comicsStore.error }}
      <button @click="comicsStore.fetchComics" class="btn btn-secondary">Retry</button>
    </div>

    <div v-else-if="comicsStore.comics.length === 0" class="empty-state">
      <p>No comics yet. {{ isAdmin ? 'Add the first one!' : 'Check back soon!' }}</p>
    </div>

    <div v-else class="comics-grid">
      <div v-for="comic in comicsStore.comics" :key="comic.id" class="comic-card">
        <div class="comic-header">
          <h3>{{ comic.serie }} #{{ comic.number }}</h3>
          <div v-if="isAdmin" class="comic-actions">
            <button @click="editComic(comic)" class="btn btn-small btn-edit" title="Edit">
              ✏️
            </button>
            <button @click="deleteComicConfirm(comic)" class="btn btn-small btn-delete" title="Delete">
              🗑️
            </button>
          </div>
        </div>
        <p class="comic-title">{{ comic.title }}</p>
        <div class="comic-meta">
          <small>Added by user #{{ comic.created_by }}</small>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="showDeleteConfirm = false">
      <div class="modal-content modal-small">
        <h3>Delete Comic?</h3>
        <p>Are you sure you want to delete "{{ comicToDelete?.serie }} #{{ comicToDelete?.number }}"?</p>
        <div class="form-actions">
          <button @click="confirmDelete" class="btn btn-danger" :disabled="comicsStore.loading">
            Delete
          </button>
          <button @click="showDeleteConfirm = false" class="btn btn-secondary">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
// Import the authentication store to check user roles
import { useAuthStore } from '@/stores/auth.js'
import { useComicsStore } from '@/stores/comics.js'

const authStore = useAuthStore()
const comicsStore = useComicsStore()

const showCreateForm = ref(false)
const showDeleteConfirm = ref(false)
const editingComic = ref(null)
const comicToDelete = ref(null)
const formError = ref('')

const isAdmin = computed(() => {
  return authStore.currentUser && (authStore.currentUser.role === 'admin' || authStore.currentUser.role === 'super_admin')
})

const formData = ref({
  serie: '',
  number: '',
  title: ''
})

const resetForm = () => {
  formData.value = {
    serie: '',
    number: '',
    title: ''
  }
  editingComic.value = null
  formError.value = ''
}

const closeForm = () => {
  showCreateForm.value = false
  resetForm()
}

const editComic = (comic) => {
  editingComic.value = comic
  formData.value = {
    serie: comic.serie,
    number: comic.number,
    title: comic.title
  }
  showCreateForm.value = true
}

const deleteComicConfirm = (comic) => {
  comicToDelete.value = comic
  showDeleteConfirm.value = true
}

const confirmDelete = async () => {
  try {
    await comicsStore.deleteComic(comicToDelete.value.id)
    showDeleteConfirm.value = false
    comicToDelete.value = null
  } catch (err) {
    formError.value = err.message || 'Failed to delete comic'
  }
}

const handleSubmit = async () => {
  formError.value = ''
  try {
    if (editingComic.value) {
      await comicsStore.updateComic(editingComic.value.id, formData.value)
    } else {
      await comicsStore.createComic(formData.value.serie, formData.value.number, formData.value.title)
    }
    closeForm()
  } catch (err) {
    formError.value = err.response?.data?.error || err.message || 'Operation failed'
  }
}

onMounted(() => {
  comicsStore.fetchComics()
})
</script>

<style scoped>
.comics-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.comics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.comics-header h1 {
  margin: 0;
}

.comics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.comic-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  background: white;
  transition: box-shadow 0.2s;
}

.comic-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.comic-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 0.5rem;
}

.comic-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.comic-actions {
  display: flex;
  gap: 0.5rem;
}

.comic-title {
  color: #666;
  margin: 0.5rem 0 1rem;
}

.comic-meta {
  color: #999;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: opacity 0.2s;
}

.btn:hover:not(:disabled) {
  opacity: 0.8;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-edit {
  background: #28a745;
  color: white;
  padding: 0.3rem 0.6rem;
}

.btn-delete {
  background: #dc3545;
  color: white;
  padding: 0.3rem 0.6rem;
}

.btn-small {
  padding: 0.3rem 0.6rem;
  font-size: 0.8rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
}

.modal-small {
  max-width: 350px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h2 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.comic-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.3rem;
  font-weight: 500;
}

.form-group input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.form-actions button {
  flex: 1;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.error-message {
  padding: 1rem;
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  margin-top: 1rem;
}

.load-more {
  display: flex;
  justify-content: center;
  margin: 2rem 0;
}
</style>
