<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { recommendPaths, refreshPlan } from '@/api/careerPaths'

const userStore = useUserStore()
const studentId = ref<number | null>(userStore.user?.studentId || null)
const loading = ref(false)
const recommendedPaths = ref<any[]>([])
const growthAdvice = ref('')

// 加载推荐路径
const loadRecommendations = async () => {
  if (!studentId.value) return
  try {
    const res = await recommendPaths(studentId.value)
    // 后端返回格式可能是 { paths: [...] } 或直接数组
    const paths = res.paths || (Array.isArray(res) ? res : [])
    recommendedPaths.value = paths.slice(0, 3) // 取前3条
  } catch (error) {
    console.error('加载推荐路径失败', error)
  }
}

// 加载成长建议（基于当前匹配度最高的岗位）
const loadGrowthAdvice = async () => {
  if (!studentId.value) return
  try {
    const res = await refreshPlan(studentId.value)
    // 假设 refreshPlan 返回 { match_score, advice, alternative_path }
    if (res.advice) {
      growthAdvice.value = res.advice
    } else {
      growthAdvice.value = '暂无具体建议，请先完成兴趣探索和简历上传。'
    }
  } catch (error) {
    console.error('加载成长建议失败', error)
    growthAdvice.value = '建议先完成兴趣探索和简历上传，系统将为你生成个性化建议。'
  }
}

onMounted(() => {
  if (studentId.value) {
    loadRecommendations()
    loadGrowthAdvice()
  } else {
    // 未登录时显示默认静态内容（可选）
  }
})
</script>

<template>
  <div class="planning-home">
    <section class="hero">
      <div class="hero-left">
        <div class="badge">职业规划路径模式</div>
        <h1>先认识自己，再决定未来方向</h1>
        <p>
          这个模式更适合大一、大二学生。你可以先探索兴趣与能力优势，
          再查看推荐职业路径，逐步建立自己的成长计划。
        </p>

        <div class="actions">
          <router-link to="/planning/explore">
            <el-button type="primary">开始探索方向</el-button>
          </router-link>
          <router-link to="/planning/path">
            <el-button>查看推荐路径</el-button>
          </router-link>
        </div>
      </div>

      <el-card class="hero-card">
        <div class="hero-card-title">当前建议</div>
        <div class="tip-item">{{ growthAdvice || '请先完成兴趣探索和简历上传，系统将为你生成个性化建议。' }}</div>
      </el-card>
    </section>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="card-label">推荐路径数</div>
          <div class="card-value">{{ recommendedPaths.length }}</div>
          <div class="card-desc">系统已为你准备多条发展方向</div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="stat-card">
          <div class="card-label">当前成长阶段</div>
          <div class="card-value">探索期</div>
          <div class="card-desc">适合广泛尝试与建立基础能力</div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="stat-card">
          <div class="card-label">本周任务</div>
          <div class="card-value">2</div>
          <div class="card-desc">完成一次方向探索和一次自我复盘</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <el-col :span="14">
        <el-card class="panel-card" v-loading="loading">
          <template #header>
            <div class="panel-header">
              <span>推荐职业路径</span>
              <router-link to="/planning/path" class="panel-link">查看更多</router-link>
            </div>
          </template>

          <div class="path-list">
            <div v-for="item in recommendedPaths" :key="item.name" class="path-item">
              <div class="path-title">{{ item.name }}</div>
              <div class="path-desc">{{ item.description }}</div>
            </div>
            <div v-if="recommendedPaths.length === 0 && !loading" class="empty-tip">暂无推荐路径，请完善档案或上传简历</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card class="panel-card">
          <template #header>
            <div class="panel-header">
              <span>本周成长建议</span>
            </div>
          </template>

          <div class="growth-list">
            <div class="growth-item">
              <div class="index blue">1</div>
              <div>
                <div class="growth-title">做一次兴趣探索</div>
                <div class="growth-desc">梳理你喜欢做的事、擅长做的事和愿意长期投入的方向。</div>
              </div>
            </div>

            <div class="growth-item">
              <div class="index yellow">2</div>
              <div>
                <div class="growth-title">培养通用能力</div>
                <div class="growth-desc">重点提升表达、协作、信息整理、项目执行等能力。</div>
              </div>
            </div>

            <div class="growth-item">
              <div class="index green">3</div>
              <div>
                <div class="growth-title">增加真实经历</div>
                <div class="growth-desc">通过社团、比赛、课程项目积累能够写进简历的经历。</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
.planning-home {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero {
  display: grid;
  grid-template-columns: 1.4fr 0.9fr;
  gap: 20px;
}

.hero-left {
  background: linear-gradient(135deg, #eef6ff, #fffdf4);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 32px;
}

.badge {
  display: inline-block;
  padding: 8px 14px;
  background: #ffffff;
  color: #6e8fd8;
  border-radius: 999px;
  font-size: 13px;
  margin-bottom: 18px;
}

.hero-left h1 {
  margin: 0 0 14px;
  font-size: 34px;
  line-height: 1.25;
  color: var(--text-primary);
}

.hero-left p {
  margin: 0 0 22px;
  font-size: 15px;
  line-height: 1.9;
  color: var(--text-regular);
  max-width: 620px;
}

.actions {
  display: flex;
  gap: 12px;
}

.hero-card-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 14px;
  color: var(--text-primary);
}

.tip-item {
  padding: 12px 14px;
  background: #f8fbff;
  border-radius: 12px;
  color: var(--text-regular);
  margin-bottom: 10px;
}

.stat-card {
  min-height: 140px;
}

.card-label {
  font-size: 14px;
  color: #8a94a6;
  margin-bottom: 10px;
}

.card-value {
  font-size: 30px;
  font-weight: 700;
  color: #2f3a4a;
  margin-bottom: 10px;
}

.card-desc {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.content-row {
  margin: 0;
}

.panel-card {
  min-height: 300px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 700;
  color: var(--text-primary);
}

.panel-link {
  font-size: 13px;
  color: #6c8fe8;
}

.path-list,
.growth-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.path-item,
.growth-item {
  padding: 14px;
  border-radius: 14px;
  background: #fafcff;
}

.path-title,
.growth-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.path-desc,
.growth-desc {
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-regular);
}

.growth-item {
  display: flex;
  gap: 14px;
}

.index {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.index.blue {
  background: #dceeff;
  color: #567fd8;
}

.index.yellow {
  background: #fff4cc;
  color: #a68118;
}

.index.green {
  background: #dff7e8;
  color: #3f9160;
}

.empty-tip {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
}

@media (max-width: 992px) {
  .hero {
    grid-template-columns: 1fr;
  }
}

:deep(.el-card) {
  background: rgba(255, 255, 255, 0.5) !important;
  backdrop-filter: blur(2px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.95);
  }
}
</style>