import { reactive, ref } from 'vue'

export const loginForm = reactive({
  username: 'admin',
  password: 'admin123!',
})

export const portsText = ref('22')

export const authState = reactive({
  accessToken: '',
  sessionId: '',
  ip: '',
})

export const sessions = ref([])
