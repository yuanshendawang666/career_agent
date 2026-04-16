<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const go = (path: string) => {
  router.push(path)
}

const isJobHome = () => route.path === '/job'
const isPositionProfiles = () => route.path === '/job/position-profiles'
const isCareerGraph = () => route.path === '/job/career-graph'
const isJobProfile = () => route.path === '/job/profile'
const isJobResume = () => route.path === '/job/resume'
const isJobMatch = () => route.path === '/job/match'
const isJobReport = () => route.path === '/job/report'
const isJobHistory = () => route.path === '/job/history'
</script>

<template>
  <!-- 这里改成和样式对应的类名 -->
  <div class="job-layout">
    <header class="header">
      <div class="brand" @click="go('/')">
        <div class="logo">
          <img src="@/assets/character.png" alt="Logo">
        </div>
        <div class="brand-text">
          <div class="title">「智途」— 你的私人职业规划助手</div>
          <div class="sub">岗位匹配模式</div>
        </div>
      </div>

      <nav class="nav">
        <button class="nav-item" :class="{ 'nav-item-active': isJobHome() }" @click="go('/job')">
          首页
        </button>

        <button class="nav-item" :class="{ 'nav-item-active': isPositionProfiles() }" @click="go('/job/position-profiles')">
          岗位画像
        </button>

        <button class="nav-item" :class="{ 'nav-item-active': isCareerGraph() }" @click="go('/job/career-graph')">
          岗位图谱
        </button>

        <button class="nav-item" :class="{ 'nav-item-active': isJobResume() }" @click="go('/job/resume')">
          简历上传
        </button>

        <button class="nav-item" :class="{ 'nav-item-active': isJobProfile() }" @click="go('/job/profile')">
          我的信息
        </button>

        <button class="nav-item" :class="{ 'nav-item-active': isJobMatch() }" @click="go('/job/match')">
          岗位匹配
        </button>

        <button class="nav-item" :class="{ 'nav-item-active': isJobReport() }" @click="go('/job/report')">
          我的报告
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
/* 全屏布局 + 背景 */
.job-layout {
  min-height: 100vh; /* 铺满屏幕高度 */
  margin: 0;
  padding: 0;
  /* 半透明白色叠加 + 背景图（全屏、固定、不重复、覆盖） */
  background: 
    url('@/assets/bg.png') center/cover no-repeat fixed;
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
  overflow: hidden;
  background: none;
  box-shadow: 0 6px 14px rgba(143, 183, 255, 0.18);
  flex-shrink: 0;
}

.logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
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