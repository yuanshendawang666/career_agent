<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { selectPath } from '@/api/careerPaths'
import { getStudent } from '@/api/student'
import { updatePlanningProfile } from '@/api/planning'          // 新增：导入更新规划档案接口
import { Edit, Check, Warning, Position } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const studentId = ref<number | null>(userStore.user?.studentId || null)
const loading = ref(false)
const rawPlan = ref('')
const selectedPath = ref('')
const monthlyGoals = ref<string[]>([])

interface PDCAItem {
  title: string
  content: string
}
const pdcaSections = ref<PDCAItem[]>([])

const loadPlan = async () => {
  if (!studentId.value) {
    ElMessage.warning('请先登录并上传简历')
    return
  }
  loading.value = true
  try {
    const studentRes = await getStudent(studentId.value)
    const profile = studentRes.profile_json || {}
    const savedPath = profile.selected_path
    const savedPlan = profile.development_plan
    const pathName = route.query.path as string

    let targetPath = pathName || savedPath
    if (!targetPath) {
      ElMessage.warning('请从推荐路径页面选择一条路径')
      return
    }

    let planText = ''
    const isNewPlan = (targetPath !== savedPath) || !savedPlan

    if (isNewPlan) {
      const res = await selectPath({ student_id: studentId.value, path_name: targetPath })
      planText = (res.plan || res.development_plan || '').replace(/\*\*/g, '')
      selectedPath.value = targetPath

      try {
        await updatePlanningProfile({ learning_plan: '' })
        console.log('已清空学习计划，下次进入学习资源页面将重新生成')
      } catch (clearError) {
        console.error('清空学习计划失败', clearError)
      }

      ElMessage.success('成长计划已更新，学习资源将重新生成')
    } else {
      selectedPath.value = savedPath
      planText = (savedPlan || '').replace(/\*\*/g, '')
    }

    rawPlan.value = planText
    parsePDCA(planText)

    // ========== 改进后的本月目标提取逻辑 ==========
    const extractGoals = (text: string): string[] => {
      // 提取 Plan 和 Do 部分的内容
      const planMatch = text.match(/Plan[：:]\s*([\s\S]*?)(?=Do[：:]|$)/i)
      const doMatch = text.match(/Do[：:]\s*([\s\S]*?)(?=Check[：:]|$)/i)
      const content = (planMatch ? planMatch[1] : '') + '\n' + (doMatch ? doMatch[1] : '')
      if (!content.trim()) return []
      
      // 尝试提取以数字序号、圆点、短横线开头的行
      const lines = content.split('\n')
      const listItems = lines.filter(line => {
        const trimmed = line.trim()
        return trimmed.match(/^(\d+\.|•|\-|\*)\s/) && trimmed.length > 5
      })
      if (listItems.length > 0) {
        return listItems.slice(0, 3).map(item => item.replace(/^[\d\.•\-\*\s]+/, '').trim())
      }
      
      // 如果没有列表项，则提取前3个完整的句子
      const sentences = content.match(/[^。！？\n]+[。！？]/g) || []
      return sentences.slice(0, 3).map(s => s.trim())
    }

    monthlyGoals.value = extractGoals(planText)
    // ==========================================
  } catch (error: any) {
    ElMessage.error(error.message || '加载计划失败')
  } finally {
    loading.value = false
  }
}

const parsePDCA = (text: string) => {
  // 预处理：修复标题换行拆分（如 P\nLAN -> Plan）
  let cleaned = text
  cleaned = cleaned.replace(/P\s*\n\s*LAN/gi, 'Plan')
  cleaned = cleaned.replace(/D\s*\n\s*O/gi, 'Do')
  cleaned = cleaned.replace(/C\s*\n\s*HECK/gi, 'Check')
  cleaned = cleaned.replace(/A\s*\n\s*CT/gi, 'Act')

  // 标准化标题：确保每个标题后跟冒号和换行，便于分割
  const titles = ['Plan', 'Do', 'Check', 'Act']
  for (const title of titles) {
    // 匹配可能存在的 ** 包裹、中文冒号、英文冒号或没有冒号的情况
    const regex = new RegExp(`(\\*\\*)?${title}(\\*\\*)?[：:]?\\s*\\n`, 'gi')
    cleaned = cleaned.replace(regex, `\n${title}：\n`)
  }

  const sections: PDCAItem[] = []
  // 按标题分割（匹配独立成行的标题，后面跟中文冒号）
  const splitRegex = /(?:^|\n)(Plan|Do|Check|Act)[：:]\s*\n/gi
  let lastIndex = 0
  let match
  const matches = []
  while ((match = splitRegex.exec(cleaned)) !== null) {
    matches.push({ index: match.index, title: match[1], fullMatch: match[0] })
  }

  for (let i = 0; i < matches.length; i++) {
    const startIdx = matches[i].index + matches[i].fullMatch.length
    const title = matches[i].title
    const endIdx = i + 1 < matches.length ? matches[i + 1].index : cleaned.length
    let content = cleaned.slice(startIdx, endIdx).trim()
    sections.push({ title, content })
  }

  // 降级处理：如果按标题分割失败，则尝试按关键词分割（不依赖严格换行）
  if (sections.length === 0 && cleaned.trim()) {
    const parts = cleaned.split(/(?=Plan[：:]|Do[：:]|Check[：:]|Act[：:])/i)
    for (const part of parts) {
      const titleMatch = part.match(/^(Plan|Do|Check|Act)[：:]/i)
      if (titleMatch) {
        const title = titleMatch[1]
        const content = part.replace(/^(Plan|Do|Check|Act)[：:]/i, '').trim()
        if (content) sections.push({ title, content })
      } else if (part.trim()) {
        // 无标题部分作为 Plan 兜底
        sections.push({ title: 'Plan', content: part.trim() })
      }
    }
  }

  // 最终兜底：如果仍然没有内容，将整段文本作为 Plan
  if (sections.length === 0 && cleaned.trim()) {
    sections.push({ title: 'Plan', content: cleaned.trim() })
  }

  pdcaSections.value = sections
}
onMounted(() => {
  loadPlan()
})
</script>

<template>
  <div class="plan-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">成长计划</h2>
        <p class="page-subtitle">根据推荐路径「{{ selectedPath || '未选择' }}」，为你生成 PDCA 成长建议。</p>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="panel-card" v-loading="loading">
          <template #header><div class="panel-title">PDCA 计划</div></template>
          <div class="pdca-container">
            <div v-for="section in pdcaSections" :key="section.title" class="pdca-card" :class="`pdca-${section.title.toLowerCase()}`">
              <div class="pdca-header">
                <div class="pdca-icon">
                  <el-icon v-if="section.title === 'Plan'"><Edit /></el-icon>
                  <el-icon v-else-if="section.title === 'Do'"><Check /></el-icon>
                  <el-icon v-else-if="section.title === 'Check'"><Warning /></el-icon>
                  <el-icon v-else><Position /></el-icon>
                </div>
                <div class="pdca-title">
                  <span class="first-letter">{{ section.title.charAt(0).toUpperCase() }}</span>
                  <span class="rest-letters">{{ section.title.slice(1).toUpperCase() }}</span>
                </div>
              </div>
              <div class="pdca-content" v-html="section.content.replace(/---/g, '').replace(/\n/g, '<br/>')"></div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="panel-card">
          <template #header><div class="panel-title">本月目标</div></template>
          <div class="goal-list">
            <div v-for="(goal, idx) in monthlyGoals" :key="idx" class="goal-item">
              <div class="goal-number" :class="`number-${idx + 1}`">{{ idx + 1 }}</div>
              <div class="goal-text">{{ goal }}</div>
            </div>
            <div v-if="monthlyGoals.length === 0" class="goal-item">暂无具体目标，请先选择路径</div>
          </div>
        </el-card>

        <el-card class="panel-card">
          <template #header><div class="panel-title">下一步</div></template>
          <router-link :to="{ path: '/planning/resources', query: { path: selectedPath, t: Date.now() } }">
            <el-button type="primary" style="width: 100%">查看学习资源</el-button>
          </router-link>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
/* 样式保持不变，省略重复代码，与用户原有样式一致 */
.plan-page {
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
.pdca-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.pdca-card {
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s;
}
.pdca-plan {
  background: #e6f0ff;
}
.pdca-do {
  background: #e8f8ee;
}
.pdca-check {
  background: #fff4e0;
}
.pdca-act {
  background: #f0e6ff;
}
.pdca-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.pdca-icon {
  width: 48px;
  height: 48px;
  background: #ffffff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}
.pdca-plan .pdca-icon {
  color: #2c5f9e;
}
.pdca-do .pdca-icon {
  color: #2d6a4f;
}
.pdca-check .pdca-icon {
  color: #b87c00;
}
.pdca-act .pdca-icon {
  color: #6f42c1;
}
.pdca-title {
  display: flex;
  align-items: baseline;
  gap: 2px;
}
.pdca-title .first-letter {
  font-size: 32px;
  font-weight: 800;
}
.pdca-title .rest-letters {
  font-size: 20px;
  font-weight: 600;
}
.pdca-plan .pdca-title .first-letter,
.pdca-plan .pdca-title .rest-letters {
  color: #2c5f9e;
}
.pdca-do .pdca-title .first-letter,
.pdca-do .pdca-title .rest-letters {
  color: #2d6a4f;
}
.pdca-check .pdca-title .first-letter,
.pdca-check .pdca-title .rest-letters {
  color: #b87c00;
}
.pdca-act .pdca-title .first-letter,
.pdca-act .pdca-title .rest-letters {
  color: #6f42c1;
}
.pdca-content {
  line-height: 1.8;
  font-size: 16px;
  color: var(--text-regular);
  white-space: pre-wrap;
}
.goal-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.goal-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 14px;
  background: #fafcff;
}
.goal-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}
.goal-number.number-1 {
  background: #dceeff;
  color: #567fd8;
}
.goal-number.number-2 {
  background: #fff4cc;
  color: #a68118;
}
.goal-number.number-3 {
  background: #dff7e8;
  color: #3f9160;
}
.goal-text {
  flex: 1;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-regular);
}
</style>