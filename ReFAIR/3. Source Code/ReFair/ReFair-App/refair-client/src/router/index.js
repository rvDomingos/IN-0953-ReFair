import { createRouter, createWebHistory } from 'vue-router'
import 'bootstrap/dist/css/bootstrap.css'
import 'mdb-vue-ui-kit/css/mdb.min.css';

import Refair from '../components/refair.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Refair',
      component: Refair,
    }
  ]
})

export default router
