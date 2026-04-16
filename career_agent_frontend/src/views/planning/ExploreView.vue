<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getStudent } from '@/api/student'
import { getPlanningProfile } from '@/api/planning'

const userStore = useUserStore()
const studentId = ref<number | null>(userStore.user?.studentId || null)
const loading = ref(false)
const interests = ref<string[]>([])
const strengths = ref<string[]>([])

const loadProfile = async () => {
  // 规划档案不依赖 studentId，直接调用 getPlanningProfile（后端根据当前用户获取）
  loading.value = true
  try {
    const res = await getPlanningProfile()
    interests.value = res.interests || []
    strengths.value = res.strengths || []
  } catch (error) {
    console.error('加载规划档案失败', error)
    ElMessage.error('加载兴趣与优势失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (studentId.value) {
    loadProfile()
  } else {
    ElMessage.warning('请先登录并完善档案')
  }
})
</script>

<template>
  <div class="explore-page" v-loading="loading">
    <div class="page-header">
      <div>
        <h2 class="page-title">方向探索</h2>
        <p class="page-subtitle">先从兴趣、优势和性格特点出发，看看你更适合哪些方向。</p>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="panel-card">
          <template #header><div class="panel-title">兴趣关键词</div></template>
          <div class="tag-wrap">
            <span v-for="item in interests" :key="item" class="soft-tag blue">{{ item }}</span>
          </div>
          <div class="desc">这些兴趣更偏向内容、传播、用户和表达相关方向。</div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="panel-card">
          <template #header><div class="panel-title">能力优势</div></template>
          <div class="tag-wrap">
            <span v-for="item in strengths" :key="item" class="soft-tag yellow">{{ item }}</span>
          </div>
          <div class="desc">这些优势说明你适合需要持续成长和信息处理的工作环境。</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="panel-card">
      <template #header><div class="panel-title">探索结论</div></template>

      <div class="conclusion-box">
        从当前兴趣与能力表现来看，你更适合优先探索：
        <strong>内容策划、新媒体运营、用户运营</strong>
        这类对表达、信息整理、沟通协作要求较高的方向。
      </div>

      <div class="next-step">
        <router-link to="/planning/path">
          <el-button type="primary">查看推荐职业路径</el-button>
        </router-link>
      </div>
    </el-card>
  </div>
</template>

<style scoped lang="scss">

.explore-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-subtitle {
  margin: -6px 0 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.tag-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
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


.desc {
  margin-top: 14px;
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-regular);
}

.conclusion-box {
  padding: 18px;
  border-radius: 16px;
  background: #fafcff;
  font-size: 14px;
  line-height: 1.9;
  color: var(--text-regular);
}

.next-step {
  margin-top: 18px;
}

:deep(.el-card) {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(2px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.95);
  }
}
</style>