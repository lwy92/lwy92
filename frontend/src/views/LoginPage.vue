<template>
  <el-card class="login-card">
    <template #header>
      <div class="title">authwall 管理台</div>
    </template>

    <el-form :model="loginForm" label-width="90px" @submit.prevent>
      <el-form-item label="用户名">
        <el-input v-model="loginForm.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="loginForm.password" type="password" show-password placeholder="请输入密码" />
      </el-form-item>
      <el-form-item label="端口列表">
        <el-input v-model="portsText" placeholder="例如：22,80,443" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="doLogin">登录并放行</el-button>
        <el-button :disabled="!authState.sessionId" @click="doLogout">退出并回收</el-button>
      </el-form-item>
    </el-form>

    <el-alert
      v-if="authState.ip"
      type="success"
      :closable="false"
      show-icon
      :title="`当前放行 IP：${authState.ip}`"
    />
  </el-card>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { http } from '../api/client'
import { authState, loginForm, portsText, sessions } from '../stores/sessionStore'

const router = useRouter()
const loading = ref(false)

const authHeaders = computed(() => {
  if (!authState.accessToken) {
    return {}
  }
  return { Authorization: `Bearer ${authState.accessToken}` }
})

const parsePorts = () =>
  portsText.value
    .split(',')
    .map((p) => Number(p.trim()))
    .filter((p) => Number.isInteger(p) && p > 0 && p < 65536)

const loadSessions = async () => {
  if (!authState.accessToken) {
    sessions.value = []
    return
  }

  try {
    const { data } = await http.get('/sessions', { headers: authHeaders.value })
    sessions.value = Array.isArray(data) ? data : []
  } catch {
    ElMessage.warning('会话拉取失败，请确认是否已登录')
  }
}

const doLogin = async () => {
  const ports = parsePorts()
  if (!ports.length) {
    ElMessage.error('请至少输入一个有效端口')
    return
  }

  loading.value = true
  try {
    const { data } = await http.post('/auth/login', {
      username: loginForm.username,
      password: loginForm.password,
      ports,
    })

    authState.accessToken = data.access_token
    authState.sessionId = data.session_id
    authState.ip = data.ip

    ElMessage.success('登录成功，已放行当前 IP')
    await loadSessions()
    await router.push('/sessions')
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

const doLogout = async () => {
  if (!authState.sessionId) {
    return
  }

  try {
    await http.post(`/auth/logout/${authState.sessionId}`)
    authState.sessionId = ''
    authState.accessToken = ''
    authState.ip = ''
    sessions.value = []
    ElMessage.success('已退出并回收规则')
  } catch {
    ElMessage.error('退出失败')
  }
}
</script>

<style scoped>
.login-card {
  max-width: 640px;
}

.title {
  font-size: 20px;
  font-weight: 700;
}
</style>
