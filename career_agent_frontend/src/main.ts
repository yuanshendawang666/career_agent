import { createApp } from 'vue'
import { createPinia } from 'pinia'          // 1. 导入 createPinia
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'
import './styles/index.scss'

const app = createApp(App)

app.use(createPinia())   // 2. 安装 Pinia（必须在 mount 之前）
app.use(router)
app.use(ElementPlus)

app.mount('#app')