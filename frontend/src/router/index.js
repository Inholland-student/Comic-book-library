import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import ComicsView from '../views/ComicsView.vue'
import CreateUserView from '../views/CreateUserView.vue'

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
  },
  {
    path: '/users/create',
    name: 'CreateUser',
    component: CreateUserView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
