<template>
  <div class="page">
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
          <el-button :disabled="!state.sessionId" @click="doLogout">退出并回收</el-button>
        </el-form-item>
      </el-form>

      <el-alert
        v-if="state.ip"
        type="success"
        :closable="false"
        show-icon
        :title="`当前放行 IP：${state.ip}`"
      />
    </el-card>

    <el-card class="list-card">
      <template #header>
        <div class="list-title">
          <span>在线会话</span>
          <el-button text type="primary" @click="loadSessions">刷新</el-button>
        </div>
      </template>

      <el-table :data="sessions" border>
        <el-table-column prop="session_id" label="会话 ID" min-width="240" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="ip" label="IP" width="150" />
        <el-table-column label="端口" width="220">
          <template #default="scope">
            <el-tag v-for="port in scope.row.ports" :key="port" class="port-tag">{{ port }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="expires_at" label="过期时间" min-width="220" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const baseURL = 'http://localhost:8000/api/v1'

// 登录表单状态
const loginForm = reactive({
  username: 'admin',
  password: 'admin123!',
})

// 端口输入框使用文本，提交时再转换为数组
const portsText = ref('22')
const loading = ref(false)
const sessions = ref([])

// 全局会话信息，用于请求鉴权
const state = reactive({
  accessToken: '',
  sessionId: '',
  ip: '',
})

const http = axios.create({ baseURL, timeout: 5000 })

const authHeaders = computed(() => {
  if (!state.accessToken) {
    return {}
  }
  return { Authorization: `Bearer ${state.accessToken}` }
})

const parsePorts = () =>
  portsText.value
    .split(',')
    .map((p) => Number(p.trim()))
    .filter((p) => Number.isInteger(p) && p > 0 && p < 65536)

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

    state.accessToken = data.access_token
    state.sessionId = data.session_id
    state.ip = data.ip
    ElMessage.success('登录成功，已放行当前 IP')
    await loadSessions()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

const doLogout = async () => {
  if (!state.sessionId) {
    return
  }

  try {
    await http.post(`/auth/logout/${state.sessionId}`)
    state.sessionId = ''
    state.accessToken = ''
    state.ip = ''
    ElMessage.success('已退出并回收规则')
    await loadSessions()
  } catch {
    ElMessage.error('退出失败')
  }
}

const loadSessions = async () => {
  if (!state.accessToken) {
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

onMounted(loadSessions)
</script>

<style scoped>
.page {
  max-width: 1100px;
  margin: 24px auto;
  padding: 0 16px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}
.title {
  font-size: 20px;
  font-weight: 700;
}
.list-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.port-tag {
  margin-right: 6px;
}
</style>
