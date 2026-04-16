<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const go = (path: string) => {
  if (route.path !== path) {
    router.push(path)
  }
}

const isPlanningHome = () => route.path === '/planning'
const isPlanningProfile = () => route.path === '/planning/profile'
const isPlanningExplore = () => route.path === '/planning/explore'
const isPlanningPath = () => route.path === '/planning/path'
const isPlanningPlan = () => route.path === '/planning/plan'
const isPlanningResources = () => route.path === '/planning/resources'
</script>

<template>
  <div class="planning-layout">
    <header class="header">
      <div class="brand" @click="go('/')">
        <div class="logo">
          <img src="@/assets/character.png" alt="Logo">
        </div>
        <div class="brand-text">
          <div class="title">「智途」— 你的私人职业规划助手</div>
          <div class="sub">职业规划路径模式</div>
        </div>
      </div>

      <nav class="nav">
        <button class="nav-item" :class="{ 'nav-item-active': isPlanningHome() }" @click="go('/planning')">
          首页
        </button>

        <button class="nav-item" :class="{ 'nav-item-active': isPlanningProfile() }" @click="go('/planning/profile')">
          我的档案
        </button>

        <button class="nav-item" :class="{ 'nav-item-active': isPlanningExplore() }" @click="go('/planning/explore')">
          方向探索
        </button>

        <button class="nav-item" :class="{ 'nav-item-active': isPlanningPath() }" @click="go('/planning/path')">
          推荐路径
        </button>

        <button class="nav-item" :class="{ 'nav-item-active': isPlanningPlan() }" @click="go('/planning/plan')">
          成长计划
        </button>

        <button class="nav-item" :class="{ 'nav-item-active': isPlanningResources() }" @click="go('/planning/resources')">
          学习资源
        </button>
      </nav>

      <div class="right-actions">
        <button class="back-link" @click="go('/')">切换模式</button>
      </div>
    </header>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped lang="scss">
.planning-layout {
  min-height: 100vh;
  margin: 0;
  padding: 0;
  background: url('@/assets/bg.png') center/cover no-repeat fixed;
}

.header {
  min-height: 72px;
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 28px;
  gap: 16px;
  flex-wrap: wrap;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.logo {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  overflow: hidden;        // 保证图片圆角裁剪
  background: none;        // 移除原来的渐变背景
  box-shadow: 0 6px 14px rgba(143, 183, 255, 0.18);
  flex-shrink: 0;
}

.logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;       // 使图片覆盖整个容器
}

.brand-text .title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.brand-text .sub {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.nav {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  flex: 1;
  justify-content: center;
}

.nav-item {
  padding: 10px 14px;
  border-radius: 10px;
  color: var(--text-regular);
  transition: all 0.2s ease;
  white-space: nowrap;
  border: none;
  background: transparent;
  cursor: pointer;
  font: inherit;
}

.nav-item:hover {
  background: #eef4ff;
  color: #4f7fdc;
}

.nav-item-active {
  background: var(--primary-color-light);
  color: #4f7fdc;
  font-weight: 600;
}

.back-link {
  padding: 8px 14px;
  border-radius: 10px;
  background: var(--warning-light);
  color: #9b7b16;
  white-space: nowrap;
  border: none;
  cursor: pointer;
  font: inherit;
}

.content {
  max-width: 1180px;
  margin: 0 auto;
  padding: 28px 20px 40px;
}

@media (max-width: 1024px) {
  .header {
    justify-content: flex-start;
  }

  .nav {
    width: 100%;
    justify-content: flex-start;
  }

  .content {
    padding: 20px 16px 32px;
  }
}
</style>