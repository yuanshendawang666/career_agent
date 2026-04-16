<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const router = useRouter()

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="mode-page">
    <header class="topbar">
      <!-- 品牌区域不变 -->
      <div class="brand">...</div>

      <div class="top-actions">
        <!-- 未登录：显示登录/注册 -->
        <template v-if="!userStore.user">
          <router-link to="/login" class="top-link">登录</router-link>
          <router-link to="/register" class="top-link register">注册</router-link>
        </template>
        <!-- 已登录：显示用户名 + 退出按钮 -->
        <template v-else>
          <span class="top-link username">{{ userStore.user.username }}</span>
          <button class="top-link logout" @click="handleLogout">退出</button>
        </template>
      </div>
    </header>


    <div class="hero">
      <div class="badge"><img src="@/assets/logo.png" alt="Logo" class="badge-logo"></div>
      <h1>选择适合你的使用模式</h1>
      <p>
        无论你是还在探索未来方向的大一大二学生，
        还是已经开始准备求职的应届生，
        都可以在这里找到对应的成长路径与支持工具。
      </p>
    </div>

    <div class="mode-grid">
      <el-card class="mode-card" shadow="hover">
        <div class="card-top">
          <div class="icon">🌱</div>
          <div class="title">职业规划路径模式</div>
          <div class="sub-title">适合大一 / 大二学生</div>
        </div>

        <div class="desc">
          帮你探索兴趣方向、理解适合的职业路径、制定阶段成长计划，
          更适合处于探索和准备阶段的学生。
        </div>

        <div class="tag-wrap">
          <span class="soft-tag blue">方向探索</span>
          <span class="soft-tag yellow">路径推荐</span>
          <span class="soft-tag green">成长计划</span>
        </div>

        <ul class="feature-list">
          <li>填写个人信息形成规划档案</li>
          <li>探索兴趣与能力优势</li>
          <li>生成个性化成长建议</li>
        </ul>

        <router-link to="/planning" class="block-link">
          <el-button type="primary" style="width: 100%">进入职业规划模式</el-button>
        </router-link>
      </el-card>

      <el-card class="mode-card" shadow="hover">
        <div class="card-top">
          <div class="icon">💼</div>
          <div class="title">岗位匹配模式</div>
          <div class="sub-title">适合求职者 / 应届生</div>
        </div>

        <div class="desc">
          帮你完善个人信息、上传简历、分析岗位匹配度、生成求职报告，
          更适合已经进入求职准备阶段的用户。
        </div>

        <div class="tag-wrap">
          <span class="soft-tag blue">岗位画像</span>
          <span class="soft-tag yellow">简历解析</span>
          <span class="soft-tag purple">匹配报告</span>
        </div>

        <ul class="feature-list">
          <li>查看岗位画像与岗位图谱</li>
          <li>上传简历并生成画像</li>
          <li>获得岗位匹配结果与求职建议</li>
        </ul>

        <router-link to="/job" class="block-link">
          <el-button type="primary" style="width: 100%">进入岗位匹配模式</el-button>
        </router-link>
      </el-card>
    </div>
  </div>
</template>

<style scoped lang="scss">
.mode-page {
  min-height: 100vh;
  background: url('@/assets/bg.png') center / cover no-repeat fixed;
  // 取消原来的渐变背景（或注释掉）
}

.topbar {
  max-width: 1180px;
  margin: 0 auto 36px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  .brand-logo {
    width: 40px;  // 根据实际调整
    height: 40px;
    object-fit: contain;
  }
}

.logo {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #4d6fae;
}

.brand-text .title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.brand-text .sub {
  font-size: 12px;
  color: var(--text-secondary);
}

.top-actions {
  display: flex;
  gap: 10px;
}

.top-link {
  padding: 8px 14px;
  border-radius: 10px;
  background: #fff;
  color: var(--text-regular);
  border: 1px solid var(--border-color);
}

.top-link.register {
  background: var(--warning-light);
  color: #9b7b16;
  border-color: transparent;
}

.hero {
  max-width: 860px;
  margin: 0 auto 36px;
  text-align: center;
}

.badge {
  display: inline-block;
  background: transparent;
  padding: 0;
  border: none;
  
  .badge-logo {
    width: 120px;  // 根据实际需要调整大小
    height: auto;
  }
}

.hero h1 {
  margin: 0 0 14px;
  font-size: 40px;
  line-height: 1.2;
  color: var(--text-primary);
}

.hero p {
  margin: 0 auto;
  max-width: 720px;
  font-size: 15px;
  line-height: 1.9;
  color: var(--text-regular);
}

.mode-grid {
  max-width: 1180px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.mode-card {
  background: rgba(255, 255, 255, 0.4) !important;  // 半透明白色，数值可调（0.7~0.9）
  backdrop-filter: blur(2px);  // 可选：背景模糊，增加玻璃态效果
  border: 1px solid rgba(255, 255, 255, 0.3);  // 可选：淡边框
}

.card-top {
  margin-bottom: 18px;
}

.icon {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  background: linear-gradient(135deg, #dceeff, #fff4cc);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  margin-bottom: 14px;
}

.title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.sub-title {
  font-size: 14px;
  color: var(--text-secondary);
}

.desc {
  font-size: 14px;
  line-height: 1.9;
  color: var(--text-regular);
  margin-bottom: 18px;
}

.tag-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.soft-tag {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 13px;
}

.soft-tag.blue {
  background: #dceeff;
  color: #567fd8;
}

.soft-tag.yellow {
  background: #fff4cc;
  color: #a68118;
}

.soft-tag.green {
  background: #dff7e8;
  color: #3f9160;
}

.soft-tag.purple {
  background: #eee8ff;
  color: #7d67c8;
}

.feature-list {
  margin: 0 0 24px;
  padding-left: 18px;
  color: var(--text-regular);
  line-height: 1.9;
  font-size: 14px;
}

.block-link {
  display: block;
}

@media (max-width: 900px) {
  .mode-grid {
    grid-template-columns: 1fr;
  }

  .hero h1 {
    font-size: 32px;
  }

  .topbar {
    flex-direction: column;
    align-items: stretch;
  }

  .top-actions {
    justify-content: flex-end;
  }
}


.top-link.username {
  background: #eef2ff;
  color: #4d6fae;
  cursor: default;
  border-color: #d0e0ff;
}
.top-link.logout {
  background: #fff0f0;
  color: #c95a5a;
  border-color: #ffe0e0;
  cursor: pointer;
}
.top-link.logout:hover {
  background: #ffe0e0;
}

.full-width-image {
  width: 100%;
  overflow: hidden;
  margin: 0;
  padding: 0;
  line-height: 0; // 消除图片下方多余空白
}

.full-width-image img {
  width: 100%;
  height: auto;      // 保持比例，高度自适应
  display: block;
  object-fit: cover;
}


</style>
