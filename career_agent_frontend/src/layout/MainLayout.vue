<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const mobileMenuOpen = ref(false)

const navList = [
  { label: '首页', path: '/home' },
  { label: '我的信息', path: '/profile' },
  { label: '简历上传', path: '/resume' },
  { label: '岗位匹配', path: '/match' },
  { label: '我的报告', path: '/report' },
  { label: '历史记录', path: '/history' }
]

const currentPageTitle = computed(() => {
  const map: Record<string, string> = {
    '/home': '首页',
    '/profile': '我的信息',
    '/resume': '简历上传',
    '/match': '岗位匹配',
    '/report': '我的报告',
    '/history': '历史记录'
  }
  return map[route.path] || 'Career Agent'
})

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-left">
        <button class="menu-btn" @click="mobileMenuOpen = !mobileMenuOpen">
          ☰
        </button>

        <router-link to="/home" class="brand">
          <div class="logo">CA</div>
          <div class="brand-text">
            <div class="title">Carrer Agent</div>
            <div class="sub">学生职业规划平台</div>
          </div>
        </router-link>
      </div>

      <nav class="nav desktop-nav">
        <router-link
          v-for="item in navList"
          :key="item.path"
          :to="item.path"
          class="nav-item"
        >
          {{ item.label }}
        </router-link>
      </nav>

      <div class="user">
        <div class="user-avatar">S</div>
        <div class="user-text">
          <div class="user-name">同学你好</div>
          <div class="user-role">个人成长空间</div>
        </div>
      </div>
    </header>

    <div v-if="mobileMenuOpen" class="mobile-mask" @click="closeMobileMenu"></div>

    <aside class="mobile-drawer" :class="{ open: mobileMenuOpen }">
      <div class="drawer-title">页面导航</div>
      <router-link
        v-for="item in navList"
        :key="item.path"
        :to="item.path"
        class="drawer-link"
        @click="closeMobileMenu"
      >
        {{ item.label }}
      </router-link>
    </aside>

    <main class="content-wrap">
      <div class="page-topbar">
        <div>
          <h1 class="page-title">{{ currentPageTitle }}</h1>
          <p class="page-subtitle">一步一步完善你的职业规划路径。</p>
        </div>
      </div>

      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped lang="scss">
.layout {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, #eef6ff 0%, transparent 24%),
    radial-gradient(circle at bottom right, #fff8de 0%, transparent 18%),
    var(--bg-page);
}

.header {
  position: sticky;
  top: 0;
  z-index: 20;
  height: 74px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.menu-btn {
  display: none;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 12px;
  background: #f3f7fd;
  color: var(--text-primary);
  font-size: 18px;
  cursor: pointer;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: linear-gradient(135deg, #dceeff, #fff4cc);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #4d6fae;
  box-shadow: 0 6px 14px rgba(143, 183, 255, 0.18);
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
  align-items: center;
  gap: 8px;
}

.nav-item {
  padding: 10px 14px;
  border-radius: 12px;
  color: var(--text-regular);
  transition: all 0.2s ease;
  font-size: 14px;
}

.nav-item:hover {
  background: #eef4ff;
  color: #4f7fdc;
}

.nav-item.router-link-active {
  background: var(--primary-color-light);
  color: #4f7fdc;
  font-weight: 600;
}

.user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #dceeff, #fff4cc);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #5374c9;
  font-weight: 700;
}

.user-text {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.user-role {
  font-size: 12px;
  color: var(--text-secondary);
}

.content-wrap {
  max-width: 1180px;
  margin: 0 auto;
  padding: 26px 20px 40px;
}

.page-topbar {
  margin-bottom: 18px;
}

.mobile-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.24);
  z-index: 29;
}

.mobile-drawer {
  position: fixed;
  top: 0;
  left: -280px;
  width: 260px;
  height: 100vh;
  background: #fff;
  border-right: 1px solid var(--border-color);
  z-index: 30;
  padding: 24px 18px;
  transition: left 0.25s ease;
}

.mobile-drawer.open {
  left: 0;
}

.drawer-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 18px;
}

.drawer-link {
  display: block;
  padding: 12px 14px;
  border-radius: 12px;
  color: var(--text-regular);
  margin-bottom: 8px;
}

.drawer-link.router-link-active {
  background: var(--primary-color-light);
  color: #4f7fdc;
  font-weight: 600;
}

@media (max-width: 1024px) {
  .desktop-nav {
    display: none;
  }

  .menu-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .user-text {
    display: none;
  }
}

@media (max-width: 768px) {
  .header {
    padding: 0 16px;
  }

  .content-wrap {
    padding: 22px 14px 32px;
  }

  .brand-text .sub {
    display: none;
  }
}
</style>