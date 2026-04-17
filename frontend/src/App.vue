<template>
  <div class="page">
    <el-card class="layout-card">
      <template #header>
        <div class="header">
          <span class="brand">authwall 前端控制台</span>
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            router
            class="nav"
          >
            <el-menu-item index="/login">登录</el-menu-item>
            <el-menu-item index="/sessions">会话列表</el-menu-item>
          </el-menu>
        </div>
      </template>

      <router-view />
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.page {
  max-width: 1100px;
  margin: 24px auto;
  padding: 0 16px;
}

.layout-card {
  min-height: 560px;
}

.header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.brand {
  font-size: 20px;
  font-weight: 700;
}

.nav {
  border-bottom: none;
}
</style>
