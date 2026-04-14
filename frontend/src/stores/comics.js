import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import comicsService from '@/services/comics.js'

export const useComicsStore = defineStore('comics', () => {
  const comics = ref([])
  const loading = ref(false)
  const error = ref(null)
  const page = ref(0)
  const total = ref(0)
  const PER_PAGE = 20

  const hasMore = computed(() => comics.value.length < total.value)

  const fetchComics = async ({ reset = true } = {}) => {
    if (loading.value) return null
    loading.value = true
    error.value = null

    const targetPage = reset ? 1 : page.value + 1
    if (reset) {
      comics.value = []
      total.value = 0
      page.value = 0
    }

    try {
      const result = await comicsService.getAll(targetPage, PER_PAGE)
      if (reset) {
        comics.value = result.comics
      } else {
        comics.value = comics.value.concat(result.comics)
      }
      page.value = result.page || targetPage
      total.value = result.total || total.value
      return result
    } catch (err) {
      error.value = err.response?.data?.error || err.message || 'Failed to fetch comics'
      console.error('Error fetching comics:', err)
    } finally {
      loading.value = false
    }
  }

  const loadMoreComics = async () => {
    if (!hasMore.value || loading.value) return null
    return fetchComics({ reset: false })
  }

  const createComic = async (serie, number, title) => {
    loading.value = true
    error.value = null
    try {
      const newComic = await comicsService.create(serie, number, title)
      comics.value.push(newComic)
      total.value += 1
      return newComic
    } catch (err) {
      error.value = err.response?.data?.error || err.message || 'Failed to create comic'
      console.error('Error creating comic:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateComic = async (id, updates) => {
    loading.value = true
    error.value = null
    try {
      const updated = await comicsService.update(id, updates.serie, updates.number, updates.title)
      const index = comics.value.findIndex(c => c.id === id)
      if (index !== -1) {
        comics.value[index] = updated
      }
      return updated
    } catch (err) {
      error.value = err.response?.data?.error || err.message || 'Failed to update comic'
      console.error('Error updating comic:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteComic = async (id) => {
    loading.value = true
    error.value = null
    try {
      await comicsService.delete(id)
      comics.value = comics.value.filter(c => c.id !== id)
      total.value = Math.max(0, total.value - 1)
    } catch (err) {
      error.value = err.response?.data?.error || err.message || 'Failed to delete comic'
      console.error('Error deleting comic:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    comics,
    loading,
    error,
    hasMore,
    fetchComics,
    loadMoreComics,
    createComic,
    updateComic,
    deleteComic
  }
})
