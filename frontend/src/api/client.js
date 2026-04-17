import axios from 'axios'

export const baseURL = 'http://localhost:8000/api/v1'

export const http = axios.create({
  baseURL,
  timeout: 5000,
})
