import { createRouter, createWebHashHistory } from 'vue-router'
import LoginPage from '../views/LoginPage.vue'
import SessionsPage from '../views/SessionsPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
  },
  {
    path: '/sessions',
    name: 'sessions',
    component: SessionsPage,
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
