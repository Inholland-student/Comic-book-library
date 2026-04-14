import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import ComicsView from '../views/ComicsView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/comics',
    name: 'Comics',
    component: ComicsView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
