<template>
  <el-card class="list-card">
    <template #header>
      <div class="list-title">
        <span>在线会话</span>
        <el-button text type="primary" @click="loadSessions">刷新</el-button>
      </div>
    </template>

    <el-empty v-if="!authState.accessToken" description="请先前往登录页面完成认证" />

    <el-table v-else :data="sessions" border>
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
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { http } from '../api/client'
import { authState, sessions } from '../stores/sessionStore'

const authHeaders = computed(() => {
  if (!authState.accessToken) {
    return {}
  }
  return { Authorization: `Bearer ${authState.accessToken}` }
})

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

onMounted(loadSessions)
</script>

<style scoped>
.list-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.port-tag {
  margin-right: 6px;
}
</style>
