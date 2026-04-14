import { defineStore } from 'pinia'
import { ref } from 'vue'
import comicsService from '@/services/comics.js'

export const useComicsStore = defineStore('comics', () => {
  const comics = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchComics = async () => {
    loading.value = true
    error.value = null
    try {
      comics.value = await comicsService.getAll()
    } catch (err) {
      error.value = err.message || 'Failed to fetch comics'
      console.error('Error fetching comics:', err)
    } finally {
      loading.value = false
    }
  }

  const createComic = async (serie, number, title) => {
    loading.value = true
    error.value = null
    try {
      const newComic = await comicsService.create(serie, number, title)
      comics.value.push(newComic)
      return newComic
    } catch (err) {
      error.value = err.message || 'Failed to create comic'
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
      error.value = err.message || 'Failed to update comic'
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
    } catch (err) {
      error.value = err.message || 'Failed to delete comic'
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
    fetchComics,
    createComic,
    updateComic,
    deleteComic
  }
})
