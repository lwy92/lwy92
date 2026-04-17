import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

// 初始化前端应用并挂载 UI 组件库
createApp(App).use(router).use(ElementPlus).mount('#app')
