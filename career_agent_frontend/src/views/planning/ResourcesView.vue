<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Timer } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getStudent } from '@/api/student'
import { previewReport } from '@/api/report'
import { getPlanningProfile, updatePlanningProfile } from '@/api/planning'

const route = useRoute()
const userStore = useUserStore()
const studentId = ref<number | null>(userStore.user?.studentId || null)
const loading = ref(false)
const selectedPath = ref('')
const learningPlan = ref('')

interface PlanStage {
  title: string
  duration: string
  content: string
}

/**
 * 从文本中提取用时信息（如“建议用时 1-2 个月”），并返回用时和清理后的文本。
 * 支持行首带 • 或 - 的列表项，也支持普通段落。
 */
const extractDuration = (text: string): { duration: string; cleanedText: string } => {
  const lines = text.split('\n')
  let duration = ''
  const cleanedLines: string[] = []
  
  for (const line of lines) {
    // 匹配“建议用时 X 个月”或“用时 X 个月”，允许行首有 • 或 - 或空白
    const match = line.match(/^\s*[•\-*]?\s*(建议用时|用时)\s*([0-9~\-]+)\s*个月/)
    if (match && !duration) {
      // 提取用时，格式统一为“建议用时 X 个月”
      duration = `${match[1]} ${match[2]} 个月`
      // 跳过这一行，不加入 cleanedLines
      continue
    }
    cleanedLines.push(line)
  }
  
  // 如果没找到任何用时，尝试从标题中匹配（兜底）
  if (!duration) {
    const titleMatch = text.match(/(建议用时|用时)\s*([0-9~\-]+)\s*个月/)
    if (titleMatch) {
      duration = `${titleMatch[1]} ${titleMatch[2]} 个月`
    }
  }
  
  return { duration, cleanedText: cleanedLines.join('\n').trim() }
}

const parsePlanToStages = (text: string): PlanStage[] => {
  if (!text) return []
  
  // 匹配【xxx】作为阶段标题，直到下一个【xxx】或结尾
  const regex = /【([^】]+)】([\s\S]*?)(?=【|$)/g
  const stages: PlanStage[] = []
  let match
  
  while ((match = regex.exec(text)) !== null) {
    let fullTitle = match[1].trim()
    let content = match[2].trim()
    content = content.replace(/^\n+/, '').replace(/\n+$/, '')
    
    // 1. 先从标题中提取用时（如果标题中包含）
    let duration = ''
    const titleDurationMatch = fullTitle.match(/(建议用时|用时)\s*([0-9~\-]+)\s*个月/)
    if (titleDurationMatch) {
      duration = `${titleDurationMatch[1]} ${titleDurationMatch[2]} 个月`
      fullTitle = fullTitle.replace(titleDurationMatch[0], '').trim()
    }
    
    // 2. 再从内容中提取用时（并清理内容）
    const { duration: contentDuration, cleanedText } = extractDuration(content)
    if (contentDuration && !duration) {
      duration = contentDuration
    }
    content = cleanedText
    
    const title = fullTitle
    if (title && content) {
      stages.push({ title, duration, content })
    }
  }
  
  // 如果没有匹配到任何阶段（兜底计划可能没有【】格式），将整段文本作为一个阶段
  if (stages.length === 0 && text.trim()) {
    const { duration, cleanedText } = extractDuration(text.trim())
    stages.push({ title: '学习计划', duration, content: cleanedText })
  }
  
  return stages
}

const stages = computed(() => parsePlanToStages(learningPlan.value))

// 根据岗位生成默认学习计划（前端兜底，已包含建议用时）
const getDefaultPlan = (jobTitle: string) => {
  const title = jobTitle.toLowerCase()
  if (title.includes('前端')) {
    return `【第一阶段：夯实基础，掌握前端核心技能】
建议用时 1-2 个月
• 学习 HTML5 基础语法，包括标签、表单、语义化标签、HTML5 新特性
• 掌握 CSS3 样式设计，包括选择器、盒模型、布局（Flexbox、Grid）、响应式设计
• 熟练使用 JavaScript 基础语法，包括变量、函数、对象、数组、DOM 操作
• 学习 ES6+ 新特性，如 let/const、箭头函数、解构赋值、模块化等
• 掌握基本的网页开发流程，能够独立完成静态页面开发
• 每周投入 15-20 小时，预计完成周期 4-8 周

【第二阶段：框架进阶，掌握现代前端框架】
建议用时 2-3 个月
• 深入学习 Vue.js 或 React 框架（组件化、状态管理、路由）
• 掌握 Webpack/Vite 等工程化工具的基本配置
• 学习 TypeScript 基础，在项目中使用类型约束
• 实战开发一个完整的中型项目（如博客系统、电商后台）

【第三阶段：能力提升，准备求职】
建议用时 1-2 个月
• 学习性能优化、单元测试、代码规范
• 参与开源项目或独立开发完整应用
• 准备面试：刷题、模拟项目经验`
  } else if (title.includes('java')) {
    return `【第一阶段：Java基础】
建议用时 2 个月
• Java 语法、面向对象、集合框架、异常处理
• 多线程编程、JVM 内存模型基础
• 数据库：MySQL 基础 + JDBC

【第二阶段：Web开发】
建议用时 2-3 个月
• Spring Boot 框架、Spring MVC、MyBatis
• RESTful API 设计、前后端分离实践
• 实战：开发一个完整的 Web 项目（如图书管理系统）

【第三阶段：分布式进阶】
建议用时 1-2 个月
• Redis 缓存、RabbitMQ 消息队列基础
• Spring Cloud 微服务入门、Docker 基础
• 项目优化与部署`
  } else {
    return `【第一阶段：基础学习】
建议用时 1-2 个月
• 掌握目标岗位的核心理论知识
• 完成基础练习题

【第二阶段：技能提升】
建议用时 2-3 个月
• 深入学习岗位所需技术栈
• 参与实际项目或模拟项目

【第三阶段：实战准备】
建议用时 1-2 个月
• 完善项目经验，准备面试
• 投递简历，获取反馈`
  }
}

const loadPlan = async () => {
  let path = route.query.path as string
  if (!path && studentId.value) {
    try {
      const studentRes = await getStudent(studentId.value)
      const profile = studentRes.profile_json || {}
      path = profile.selected_path
    } catch (error) {
      console.error('获取学生信息失败', error)
    }
  }
  if (!path) {
    ElMessage.info('请先在“推荐路径”页面选择一条职业路径')
    selectedPath.value = ''
    learningPlan.value = ''
    return
  }
  selectedPath.value = path
  loading.value = true
  try {
    const planning = await getPlanningProfile()
    if (planning.learning_plan && planning.learning_plan.trim()) {
      learningPlan.value = planning.learning_plan
      loading.value = false
      return
    }
    const reportData = await previewReport({ student_id: studentId.value!, job_title: path })
    const plan = reportData.learning_resources || ''
    if (plan && plan.length > 50) {
      learningPlan.value = plan
      await updatePlanningProfile({ learning_plan: plan })
    } else {
      learningPlan.value = getDefaultPlan(path)
    }
  } catch (error) {
    console.error('加载学习计划失败，使用默认计划', error)
    learningPlan.value = getDefaultPlan(path)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPlan()
})
</script>

<template>
  <div class="plan-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">学习计划</h2>
        <p class="page-subtitle">根据你选择的「{{ selectedPath || '未选择' }}」路径，为你定制阶段性学习计划。</p>
      </div>
    </div>

    <div v-loading="loading" class="plan-container">
      <div v-if="stages.length" class="stages-list">
        <div 
          v-for="(stage, index) in stages" 
          :key="index" 
          class="stage-card"
          :style="{ animationDelay: `${index * 0.05}s` }"
        >
          <div class="stage-header">
            <div class="stage-title-wrapper">
              <span class="stage-index">{{ index + 1 }}</span>
              <h3 class="stage-title">{{ stage.title }}</h3>
            </div>
            <div v-if="stage.duration" class="stage-duration">
              <el-icon><Timer /></el-icon>
              <span>{{ stage.duration }}</span>
            </div>
          </div>
          <div class="stage-content">
            <div 
              v-for="(line, lineIdx) in stage.content.split('\n')" 
              :key="lineIdx"
              class="content-line"
              :class="{ 'list-item': line.trim().startsWith('•') || line.trim().startsWith('-') }"
            >
              {{ line }}
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="!loading" class="empty-state">
        <el-empty description="暂无学习计划，请稍后再试" />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.plan-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px 20px;
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #1e293b, #3b82f6);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.plan-container {
  min-height: 400px;
}

.stages-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stage-card {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.3);
  animation: fadeInUp 0.4s ease-out both;

  backdrop-filter: blur(2px);   
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
    border-color: #d9e2ef;
  }
}

.stage-header {
  padding: 20px 24px 12px 24px;
  background: transparent;
  border-bottom: 1px solid #eef2f6;
  border-bottom-color: rgba(255, 255, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.stage-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stage-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #3b82f6;
  color: white;
  font-weight: 700;
  font-size: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(59, 130, 246, 0.3);
}

.stage-title {
  font-size: 20px;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.3px;
}

.stage-duration {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  padding: 6px 14px;
  border-radius: 40px;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  
  .el-icon {
    font-size: 14px;
  }
}

.stage-content {
  padding: 20px 24px 24px 24px;
  background: transparent;
}

.content-line {
  font-size: 15px;
  line-height: 1.7;
  color: #334155;
  margin-bottom: 10px;
  white-space: pre-wrap;
  word-break: break-word;

  &:last-child {
    margin-bottom: 0;
  }

  &.list-item {
    padding-left: 8px;
    position: relative;
    color: #1e293b;
    font-weight: 500;
  }
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 640px) {
  .plan-page {
    padding: 16px;
  }
  .stage-header {
    padding: 16px 20px 10px 20px;
    flex-direction: column;
    align-items: flex-start;
  }
  .stage-content {
    padding: 16px 20px 20px 20px;
  }
  .stage-title {
    font-size: 18px;
  }
  .content-line {
    font-size: 14px;
  }
}

</style>