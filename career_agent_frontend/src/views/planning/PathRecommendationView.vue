<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { recommendPaths, selectPath as selectPathAPI } from '@/api/careerPaths'

const router = useRouter()
const userStore = useUserStore()
const studentId = ref<number | null>(userStore.user?.studentId || null)
const loading = ref(false)
const paths = ref<any[]>([])

// 加载推荐路径
const loadRecommendations = async () => {
  if (!studentId.value) {
    ElMessage.warning('请先上传简历或完善档案')
    return
  }
  loading.value = true
  try {
    const res = await recommendPaths(studentId.value)
    // 后端返回格式可能是 { paths: [...] } 或直接数组，根据实际调整
    paths.value = res.paths || (Array.isArray(res) ? res : [])
    if (paths.value.length === 0) {
      ElMessage.info('暂无推荐路径，请完善个人信息')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载推荐失败')
  } finally {
    loading.value = false
  }
}

// 选择路径并保存，然后跳转到成长计划页面
const selectPath = (pathName: string) => {
  // 直接跳转，不等待保存
  router.push({ path: '/planning/plan', query: { path: pathName } })
}

onMounted(() => {
  if (studentId.value) {
    loadRecommendations()
  } else {
    ElMessage.warning('请先登录并上传简历')
  }
})
</script>

<template>
  <div class="path-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">推荐路径</h2>
        <p class="page-subtitle">系统根据你的特点，推荐了以下几条更适合早期探索的职业路径。</p>
      </div>
    </div>

    <div v-loading="loading" class="path-list">
      <el-card v-for="item in paths" :key="item.name" class="path-card">
        <div class="path-top">
          <div>
            <div class="path-title">{{ item.name }}</div>
            <div class="path-match">匹配度 {{ item.match_score }}%</div>
          </div>
          <el-tag round>推荐</el-tag>
        </div>
        <div class="path-desc">{{ item.description }}</div>
        <div class="tag-wrap">
          <span class="soft-tag blue">{{ item.name.split('方向')[0] || item.name }}</span>
        </div>
        <div class="action-row">
          <el-button type="primary" size="small" @click="selectPath(item.name)">选择此路径</el-button>
        </div>
      </el-card>

      <div v-if="paths.length === 0 && !loading" class="empty-tip">暂无推荐路径，请完善档案或上传简历</div>
    </div>

    <div class="action-row">
      <router-link to="/planning/explore">
        <el-button>重新探索方向</el-button>
      </router-link>
    </div>
  </div>
</template>

<style scoped lang="scss">
/* 保持原有样式，增加 .action-row 和 .empty-tip */
.path-page { display: flex; flex-direction: column; gap: 20px; }
.page-subtitle { margin: -6px 0 0; font-size: 14px; color: var(--text-secondary); }
.path-list { display: flex; flex-direction: column; gap: 16px; }
.path-card { border-radius: 20px; }
.path-top { display: flex; justify-content: space-between; gap: 14px; align-items: flex-start; margin-bottom: 14px; }
.path-title { font-size: 20px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px; }
.path-match { font-size: 13px; color: var(--text-secondary); }
.path-desc { font-size: 14px; line-height: 1.9; color: var(--text-regular); margin-bottom: 16px; }
.tag-wrap { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 16px; }
.soft-tag { display: inline-flex; align-items: center; padding: 8px 14px; border-radius: 999px; font-size: 13px; background: #dceeff; color: #567fd8; }
.action-row { margin-top: 8px; }
.empty-tip { text-align: center; color: var(--text-secondary); padding: 40px; }
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