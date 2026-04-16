<script setup lang="ts">
import { reactive, ref, onMounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { previewReport, exportReport, polishText } from '@/api/report'
import {
  Edit, Check, Warning, Position,
  User, School, Medal, Coin, TrendCharts,
  MapLocation, DataLine, Promotion, Connection,
  Document, Reading, Timer, MagicStick, Switch, Location
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const studentId = ref<number | null>(null)
const jobTitle = ref<string>('')
const editMode = ref(false)
const polishPrompt = ref('')
const polishTarget = ref('gap_analysis')
const loading = ref(false)

const dimensionNameMap: Record<string, string> = {
  base_match: '基础要求',
  professional_match: '职业技能',
  quality_match: '职业素养',
  potential_match: '发展潜力',
  skill_match: '技能匹配',
  cert_match: '证书匹配',
  innovation_match: '创新匹配',
  learning_match: '学习匹配',
  stress_match: '抗压匹配',
  communication_match: '沟通匹配',
  education_match: '学历匹配',
  major_match: '专业匹配',
  experience_match: '经验匹配',
  language_match: '语言匹配',
  internship_match: '实习匹配',
  total_score: '全局评分'
}

const reportData = reactive({
  student: {
    id: 0,
    name: '',
    education: '',
    major: '',
    skills: [] as string[],
    certificates: [] as string[],
    overall_score: 0,
    overall_reason: ''
  },
  job_title: '',
  match_details: {} as Record<string, number>,
  paths: {} as { promotions: string[]; transfers: string[] },
  region_stats: [] as Array<{
    region: string;
    demand_count: number;
    salary_min_avg: number;
    salary_max_avg: number;
    top_cities: string[];
  }>,
  gap_analysis: '',
  action_plan: '',
  evaluation_cycle: '',
  transition_advice: '',
  learning_resources: ''
})

const editable = reactive({
  gap_analysis: '',
  action_plan: '',
  transition_advice: '',
  learning_resources: ''
})

// 解析 PDCA 文本为阶段卡片数据
interface PDCASection {
  title: string
  content: string
}
const pdcaSections = computed<PDCASection[]>(() => {
  const text = editMode ? editable.action_plan : reportData.action_plan
  if (!text) return []
  const sections: PDCASection[] = []
  const titles = ['Plan', 'Do', 'Check', 'Act']
  const regex = new RegExp(`(?:\\*\\*)?(${titles.join('|')})(?:\\*\\*)?[\\s:：]*\\n`, 'gi')
  let match
  const matches: { index: number; title: string }[] = []
  while ((match = regex.exec(text)) !== null) {
    matches.push({ index: match.index, title: match[1] })
  }
  for (let i = 0; i < matches.length; i++) {
    const startIdx = matches[i].index + matches[i].title.length + 1
    const endIdx = i + 1 < matches.length ? matches[i + 1].index : text.length
    let content = text.slice(startIdx, endIdx).trim()
    content = content.replace(/^[-]{3,}\s*/, '').trim()
    sections.push({ title: matches[i].title, content })
  }
  if (sections.length === 0 && text.trim()) {
    sections.push({ title: 'Plan', content: text.trim() })
  }
  return sections
})

const transitionAdviceItems = computed(() => {
  const text = editMode ? editable.transition_advice : reportData.transition_advice
  if (!text || text.trim() === '') return []
  
  const parts = text.split(/(?=\d+\.\s+)/)
  const items: { number: string; title: string; content: string }[] = []
  
  for (const part of parts) {
    const match = part.match(/^(\d+\.)\s*(.*?)(?:\n|$)/s)
    if (match) {
      const number = match[1]
      let remaining = part.slice(match[0].length).trim()
      let title = match[2].trim()
      
      if ((!title || title.length < 5) && remaining) {
        const firstSentenceMatch = remaining.match(/^[^。！？\n]+[。！？\n]/)
        if (firstSentenceMatch) {
          title = firstSentenceMatch[0].trim()
          remaining = remaining.slice(firstSentenceMatch[0].length).trim()
        } else {
          title = remaining
          remaining = ''
        }
      }
      
      title = title.replace(/\n/g, ' ').trim()
      
      items.push({
        number,
        title,
        content: remaining
      })
    } else if (part.trim().length > 0) {
      items.push({
        number: '',
        title: '',
        content: part.trim()
      })
    }
  }
  
  if (items.length === 0 && text.trim().length > 0) {
    items.push({
      number: '',
      title: '',
      content: text.trim()
    })
  }
  
  return items
})

// 解析学习资源为阶段卡片
interface ResourceStage {
  title: string
  duration: string
  content: string
}
const resourceStages = computed<ResourceStage[]>(() => {
  const text = editMode ? editable.learning_resources : reportData.learning_resources
  if (!text) return []
  const stages: ResourceStage[] = []
  const regex = /【([^】]+)】([\s\S]*?)(?=【|$)/g
  let match
  while ((match = regex.exec(text)) !== null) {
    let fullTitle = match[1].trim()
    let content = match[2].trim()
    content = content.replace(/^\n+/, '').replace(/\n+$/, '')
    
    let duration = ''
    const durationMatch = fullTitle.match(/(建议用时|用时)\s*([0-9~\-]+)\s*个月/)
    if (durationMatch) {
      duration = `${durationMatch[1]} ${durationMatch[2]} 个月`
      fullTitle = fullTitle.replace(durationMatch[0], '').trim()
    }
    const title = fullTitle
    if (title && content) {
      stages.push({ title, duration, content })
    }
  }
  if (stages.length === 0 && text.trim()) {
    stages.push({ title: '学习计划', duration: '', content: text.trim() })
  }
  return stages
})

const loadReport = async () => {
  const sid = route.query.student_id
  const jt = route.query.job_title
  if (!sid || !jt) {
    ElMessage.warning('缺少学生ID或岗位名称，请从匹配页面进入')
    router.back()
    return
  }
  studentId.value = parseInt(sid as string)
  jobTitle.value = jt as string

  loading.value = true
  try {
    const res = await previewReport({ student_id: studentId.value, job_title: jobTitle.value })
    Object.assign(reportData, res)
    editable.gap_analysis = reportData.gap_analysis
    editable.action_plan = reportData.action_plan
    editable.transition_advice = reportData.transition_advice
    editable.learning_resources = reportData.learning_resources
    await nextTick()
    renderRadarChart()
  } catch (error: any) {
    ElMessage.error(error.message || '加载报告失败')
  } finally {
    loading.value = false
  }
}

const renderRadarChart = () => {
  const chartDom = document.getElementById('radar-chart')
  if (!chartDom) return
  const myChart = echarts.init(chartDom)
  const dimensionMap: Record<string, string> = {
    base_match: '基础要求',
    professional_match: '职业技能',
    quality_match: '职业素养',
    potential_match: '发展潜力',
    skill_match: '技能匹配',
    cert_match: '证书匹配',
    innovation_match: '创新匹配',
    learning_match: '学习匹配',
    stress_match: '抗压匹配',
    communication_match: '沟通匹配',
    education_match: '学历匹配',
    major_match: '专业匹配',
    experience_match: '经验匹配',
    language_match: '语言匹配',
  }
  const indicators: { name: string; max: number }[] = []
  const values: number[] = []
  for (const [key, label] of Object.entries(dimensionMap)) {
    const val = reportData.match_details[key]
    if (val !== undefined && val > 0) {
      indicators.push({ name: label, max: 1 })
      values.push(val)
    }
  }
  if (indicators.length === 0) {
    myChart.clear()
    myChart.setOption({ title: { show: true, text: '暂无匹配数据', left: 'center', top: 'center' } })
    return
  }
  myChart.setOption({
    radar: {
      indicator: indicators,
      shape: 'circle',
      name: { textStyle: { fontSize: 10 } },
      center: ['50%', '50%'],
      radius: '65%'
    },
    series: [{
      type: 'radar',
      data: [{ value: values, name: '匹配度' }],
      areaStyle: { color: 'rgba(59, 130, 246, 0.2)' },
      lineStyle: { color: '#3b82f6', width: 2 },
      symbolSize: 6,
      symbol: 'circle'
    }]
  })
}

const handleEdit = () => { editMode.value = true }
const handleSave = () => {
  reportData.gap_analysis = editable.gap_analysis
  reportData.action_plan = editable.action_plan
  reportData.transition_advice = editable.transition_advice
  reportData.learning_resources = editable.learning_resources
  editMode.value = false
  ElMessage.success('报告内容已更新')
}

const handlePolish = async () => {
  if (!polishPrompt.value.trim()) {
    ElMessage.warning('请输入润色要求')
    return
  }
  let textToPolish = ''
  switch (polishTarget.value) {
    case 'gap_analysis': textToPolish = editable.gap_analysis; break
    case 'action_plan': textToPolish = editable.action_plan; break
    case 'transition_advice': textToPolish = editable.transition_advice; break
    case 'learning_resources': textToPolish = editable.learning_resources; break
    default: return
  }
  if (!textToPolish) {
    ElMessage.warning('无可润色的内容')
    return
  }
  loading.value = true
  try {
    const res = await polishText({ text: textToPolish, instruction: polishPrompt.value })
    switch (polishTarget.value) {
      case 'gap_analysis':
        reportData.gap_analysis = res.polished_text
        editable.gap_analysis = res.polished_text
        break
      case 'action_plan':
        reportData.action_plan = res.polished_text
        editable.action_plan = res.polished_text
        break
      case 'transition_advice':
        reportData.transition_advice = res.polished_text
        editable.transition_advice = res.polished_text
        break
      case 'learning_resources':
        reportData.learning_resources = res.polished_text
        editable.learning_resources = res.polished_text
        break
    }
    polishPrompt.value = ''
    ElMessage.success('润色完成')
  } catch (error: any) {
    ElMessage.error(error.message || '润色失败')
  } finally {
    loading.value = false
  }
}

const handleExport = async () => {
  const exportPayload = {
    ...reportData,
    gap_analysis: editable.gap_analysis,
    action_plan: editable.action_plan,
    transition_advice: editable.transition_advice,
    learning_resources: editable.learning_resources
  }
  loading.value = true
  try {
    const blob = await exportReport({ report_data: exportPayload })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    
    // ========== 自定义文件名（含时间戳，避免重复） ==========
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    const hours = String(now.getHours()).padStart(2, '0')
    const minutes = String(now.getMinutes()).padStart(2, '0')
    const seconds = String(now.getSeconds()).padStart(2, '0')
    const dateStr = `${year}${month}${day}_${hours}${minutes}${seconds}`
    const studentName = reportData.student.name || '学生'
    const job = jobTitle.value || '岗位'
    const filename = `${studentName}_${job}_职业发展报告_${dateStr}.docx`
    a.download = filename
    
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('报告导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadReport() })
</script>

<template>
  <div class="report-page">
    <div class="page-header">
      <div class="header-info">
        <div class="title-icon">
          <el-icon :size="32"><Document /></el-icon>
        </div>
        <div>
          <h2 class="page-title">职业发展报告</h2>
          <p class="page-subtitle">全面分析你的能力与目标岗位的匹配度，提供定制化成长建议</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button v-if="!editMode" @click="handleEdit" :icon="Edit">编辑报告</el-button>
        <el-button v-if="editMode" @click="handleSave" type="success" :icon="Check">保存修改</el-button>
        <el-button type="primary" :loading="loading" @click="handleExport" :icon="Document">导出报告</el-button>
      </div>
    </div>

    <div class="report-grid">
      <div class="report-main">
        <el-card class="section-card" shadow="hover" v-loading="loading">
          <!-- 一、学生基本信息 -->
          <div class="report-section">
            <div class="section-header">
              <el-icon><User /></el-icon>
              <h3>一、学生基本信息</h3>
            </div>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">姓名</span>
                <span class="info-value">{{ reportData.student.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">学历</span>
                <span class="info-value">{{ reportData.student.education }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">专业</span>
                <span class="info-value">{{ reportData.student.major }}</span>
              </div>
              <div class="info-item full-width">
                <span class="info-label">技能</span>
                <div class="tag-group">
                  <el-tag v-for="s in reportData.student.skills" :key="s" size="small" effect="plain">{{ s }}</el-tag>
                </div>
              </div>
              <div class="info-item full-width">
                <span class="info-label">证书</span>
                <div class="tag-group">
                  <el-tag v-for="c in reportData.student.certificates" :key="c" size="small" type="success" effect="plain">{{ c }}</el-tag>
                </div>
              </div>
              <div class="info-item">
                <span class="info-label">综合竞争力</span>
                <div class="score-badge">
                  <el-progress :percentage="reportData.student.overall_score" :stroke-width="8" :show-text="false" />
                  <span class="score-number">{{ reportData.student.overall_score }}分</span>
                </div>
              </div>
              <div class="info-item full-width">
                <span class="info-label">评分理由</span>
                <span class="info-value reason">{{ reportData.student.overall_reason }}</span>
              </div>
            </div>
          </div>

          <!-- 二、人岗匹配分析 -->
          <div class="report-section">
            <div class="section-header">
              <el-icon><TrendCharts /></el-icon>
              <h3>二、人岗匹配分析</h3>
            </div>
            <div class="match-summary">
              <div class="target-job">
                <span class="label">目标岗位：</span>
                <span class="value">{{ reportData.job_title }}</span>
              </div>
              <div class="total-score">
                <span class="label">综合匹配度</span>
                <div class="score-ring">
                  <el-progress type="circle" :percentage="Math.round(reportData.match_details.total_score * 100)" :width="80" :stroke-width="8" color="#3b82f6" />
                </div>
              </div>
            </div>
            <el-table 
              v-if="Object.entries(reportData.match_details).filter(([key, value]) => key !== 'total_score' && value > 0).length > 0"
              :data="Object.entries(reportData.match_details).filter(([key, value]) => key !== 'total_score' && value > 0)" 
              border stripe 
              class="match-table"
            >
              <el-table-column label="维度" width="120">
                <template #default="{ row }">
                  <div class="dimension-cell">
                    <span>{{ dimensionNameMap[row[0]] || row[0] }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="匹配度">
                <template #default="{ row }">
                  <el-progress :percentage="Math.round(row[1] * 100)" :stroke-width="8" :show-text="false" />
                  <span style="margin-left: 8px; font-size: 12px;">{{ (row[1] * 100).toFixed(1) }}%</span>
                </template>
              </el-table-column>
            </el-table>
            <div v-else class="empty-tip" style="text-align: center; padding: 20px; background: #f8fafc; border-radius: 16px; color: #64748b;">
              暂无有效匹配数据（所有维度匹配度为0%）
            </div>
            <div id="radar-chart" style="width: 100%; height: 400px; margin-top: 20px;"></div>
          </div>

          <!-- 三、职业目标与路径规划 -->
          <div class="report-section">
            <div class="section-header">
              <el-icon><Promotion /></el-icon>
              <h3>三、职业目标与路径规划</h3>
            </div>
            <div class="path-cards">
              <div class="path-card target">
                <el-icon><Medal /></el-icon>
                <div>
                  <div class="path-label">推荐职业目标</div>
                  <div class="path-value">{{ reportData.job_title }}</div>
                </div>
              </div>
              <div v-if="reportData.paths.promotions?.length" class="path-card promotion">
                <el-icon><Connection /></el-icon>
                <div>
                  <div class="path-label">晋升路径</div>
                  <div class="path-value">{{ reportData.paths.promotions.join(' → ') }}</div>
                </div>
              </div>
              <div v-if="reportData.paths.transfers?.length" class="path-card transfer">
                <el-icon><Switch /></el-icon>
                <div>
                  <div class="path-label">横向换岗路径</div>
                  <div class="path-value">{{ reportData.paths.transfers.join('、') }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 四、区域机会分析 -->
          <div class="report-section" v-if="reportData.region_stats.length">
            <div class="section-header">
              <el-icon><MapLocation /></el-icon>
              <h3>四、区域机会分析</h3>
            </div>
            <div class="region-grid">
              <div 
                v-for="(stat, idx) in reportData.region_stats" 
                :key="stat.region" 
                class="region-card"
                :class="`region-color-${(idx % 4) + 1}`"
              >
                <div class="region-name">{{ stat.region }}</div>
                <div class="region-stats">
                  <div class="stat-item">
                    <el-icon><DataLine /></el-icon>
                    <span>招聘数量：{{ stat.demand_count }}</span>
                  </div>
                  <div class="stat-item">
                    <el-icon><Coin /></el-icon>
                    <span>薪资：{{ stat.salary_min_avg }} - {{ stat.salary_max_avg }}K</span>
                  </div>
                  <div class="stat-item">
                    <el-icon><Location /></el-icon>
                    <span>主要城市：{{ stat.top_cities.join(', ') }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 五、差距分析 -->
          <div class="report-section">
            <div class="section-header">
              <el-icon><Warning /></el-icon>
              <h3>五、差距分析</h3>
            </div>
            <div class="content-block">
              <el-input v-if="editMode" v-model="editable.gap_analysis" type="textarea" :rows="4" />
              <p v-else class="text-content">{{ reportData.gap_analysis }}</p>
            </div>
          </div>

          <!-- 六、PDCA发展计划 -->
          <div class="report-section">
            <div class="section-header">
              <el-icon><Timer /></el-icon>
              <h3>六、PDCA发展计划</h3>
            </div>
            <div v-if="editMode">
              <el-input v-model="editable.action_plan" type="textarea" :rows="12" placeholder="请输入 PDCA 计划文本，包含 Plan、Do、Check、Act 四个部分" />
            </div>
            <div v-else class="pdca-stages">
              <div v-for="section in pdcaSections" :key="section.title" class="pdca-card" :class="`card-${section.title.toLowerCase()}`">
                <div class="card-header">
                  <div class="card-icon">
                    <el-icon v-if="section.title === 'Plan'"><Edit /></el-icon>
                    <el-icon v-else-if="section.title === 'Do'"><Check /></el-icon>
                    <el-icon v-else-if="section.title === 'Check'"><Warning /></el-icon>
                    <el-icon v-else><Position /></el-icon>
                  </div>
                  <div class="card-title">
                    <span class="title-en">{{ section.title.toUpperCase() }}</span>
                    <span class="title-cn">{{ { Plan: '计划', Do: '执行', Check: '检查', Act: '调整' }[section.title] }}</span>
                  </div>
                </div>
                <div class="card-content" v-html="section.content.replace(/\n/g, '<br/>')"></div>
              </div>
            </div>
          </div>

          <!-- 七、岗位调动建议 -->
          <div class="report-section" v-if="reportData.transition_advice || editable.transition_advice">
            <div class="section-header">
              <el-icon><Switch /></el-icon>
              <h3>七、岗位调动建议</h3>
            </div>
            <div v-if="editMode">
              <el-input v-model="editable.transition_advice" type="textarea" :rows="8" placeholder="请输入岗位调动建议（可包含数字序号）" />
            </div>
            <div v-else class="transition-advice-list">
              <div 
                v-for="(item, idx) in transitionAdviceItems" 
                :key="idx" 
                class="advice-card"
                :class="`advice-card-${(idx % 3) + 1}`"
              >
                <div class="advice-number" v-if="item.number">{{ item.number }}</div>
                <div class="advice-content">
                  <div v-if="item.title" class="advice-title">{{ item.title }}</div>
                  <div class="advice-text">{{ item.content }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 八、学习资源推荐 -->
          <div class="report-section" v-if="reportData.learning_resources || editable.learning_resources">
            <div class="section-header">
              <el-icon><Reading /></el-icon>
              <h3>八、学习资源推荐</h3>
            </div>
            <div v-if="editMode">
              <el-input v-model="editable.learning_resources" type="textarea" :rows="10" placeholder="请输入学习资源推荐，建议使用【第X阶段：标题】格式" />
            </div>
            <div v-else class="resource-stages">
              <div v-for="(stage, idx) in resourceStages" :key="idx" class="resource-card" :class="`resource-color-${(idx % 4) + 1}`">
                <div class="resource-header">
                  <div class="resource-title">{{ stage.title }}</div>
                  <div v-if="stage.duration" class="resource-duration">
                    <el-icon><Timer /></el-icon>
                    <span>{{ stage.duration }}</span>
                  </div>
                </div>
                <div class="resource-content">
                  <div 
                    v-for="(line, lineIdx) in stage.content.split('\n')" 
                    :key="lineIdx"
                    class="resource-line"
                    :class="{ 'resource-list-item': line.trim().startsWith('•') || line.trim().startsWith('-') }"
                  >
                    {{ line }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 九、评估周期 -->
          <div class="report-section">
            <div class="section-header">
              <el-icon><Timer /></el-icon>
              <h3>九、评估周期与动态调整</h3>
            </div>
            <div class="content-block">
              <p class="text-content">{{ reportData.evaluation_cycle }}</p>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧润色栏 -->
      <div class="report-sidebar">
        <el-card class="polish-card" shadow="hover">
          <template #header>
            <div class="polish-header">
              <el-icon><MagicStick /></el-icon>
              <span>文本润色助手</span>
            </div>
          </template>
          <el-form label-position="top">
            <el-form-item label="选择段落">
              <el-select v-model="polishTarget" placeholder="请选择" size="default">
                <el-option label="差距分析" value="gap_analysis" />
                <el-option label="PDCA发展计划" value="action_plan" />
                <el-option label="岗位调动建议" value="transition_advice" />
                <el-option label="学习资源推荐" value="learning_resources" />
              </el-select>
            </el-form-item>
            <el-form-item label="润色要求">
              <el-input v-model="polishPrompt" type="textarea" :rows="4" placeholder="例如：语气更正式、更简洁、更适合应届生" />
            </el-form-item>
          </el-form>
          <el-button type="primary" @click="handlePolish" :loading="loading" style="width: 100%">开始润色</el-button>
        </el-card>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.report-page {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 28px;
  padding: 0 8px;
}
.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}
.title-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #e6f0ff, #ffffff);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px;
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
.header-actions {
  display: flex;
  gap: 12px;
}
.report-grid {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}
.report-main {
  flex: 1;
  min-width: 0;
}
.report-sidebar {
  width: 320px;
  flex-shrink: 0;
}
.section-card {
  border-radius: 24px;
  border: none;
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
  transition: all 0.3s;
  :deep(.el-card__body) {
    padding: 28px 32px;
  }
}
.report-section {
  margin-bottom: 48px;
  &:last-child {
    margin-bottom: 0;
  }
}
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  border-bottom: 2px solid #eef2f6;
  padding-bottom: 10px;
  .el-icon {
    font-size: 24px;
    color: #3b82f6;
  }
  h3 {
    font-size: 20px;
    font-weight: 600;
    color: #0f172a;
    margin: 0;
  }
}
/* 学生基本信息 - 淡青色 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: linear-gradient(135deg, #e0f2fe, #ffffff);
  padding: 12px 16px;
  border-radius: 16px;
  border: 1px solid #bae6fd;
  .info-label {
    font-size: 12px;
    color: #0369a1;
    font-weight: 500;
  }
  .info-value {
    font-size: 15px;
    color: #0c4a6e;
    font-weight: 500;
  }
  &.full-width {
    grid-column: span 2;
  }
  .reason {
    color: #475569;
    font-weight: normal;
    line-height: 1.5;
  }
}
.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.score-badge {
  display: flex;
  align-items: center;
  gap: 12px;
  .score-number {
    font-size: 18px;
    font-weight: 700;
    color: #0284c7;
  }
}
/* 匹配分析摘要 - 淡橙色 */
.match-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #ffedd5, #ffffff);
  padding: 20px;
  border-radius: 20px;
  margin-bottom: 24px;
  border: 1px solid #fed7aa;
  .target-job {
    .label {
      font-size: 13px;
      color: #9a3412;
    }
    .value {
      font-size: 20px;
      font-weight: 700;
      color: #7c2d12;
    }
  }
  .total-score {
    text-align: center;
    .label {
      font-size: 13px;
      color: #9a3412;
      display: block;
      margin-bottom: 8px;
    }
  }
}
.match-table {
  border-radius: 16px;
  overflow: hidden;
}
/* 路径规划卡片 - 三个不同浅色 */
.path-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.path-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 20px;
  transition: all 0.2s;
  border: 1px solid rgba(0,0,0,0.05);
  .el-icon {
    font-size: 28px;
  }
  .path-label {
    font-size: 12px;
    color: #64748b;
  }
  .path-value {
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
  }
  &.target {
    background: linear-gradient(135deg, #dbeafe, #ffffff);
    border-left: 4px solid #3b82f6;
    .el-icon { color: #2563eb; }
  }
  &.promotion {
    background: linear-gradient(135deg, #dcfce7, #ffffff);
    border-left: 4px solid #10b981;
    .el-icon { color: #059669; }
  }
  &.transfer {
    background: linear-gradient(135deg, #fef3c7, #ffffff);
    border-left: 4px solid #f59e0b;
    .el-icon { color: #d97706; }
  }
}
/* 区域机会分析 - 四种不同浅色 */
.region-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.region-card {
  border-radius: 20px;
  padding: 16px;
  transition: all 0.2s;
  border: 1px solid #eef2f6;
  background: #ffffff;
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  }
  .region-name {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid currentColor;
  }
  .region-stats {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .stat-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    .el-icon {
      font-size: 14px;
    }
  }
}
.region-color-1 {
  border-top: 4px solid #f97316;
  .region-name { color: #c2410c; border-bottom-color: #fed7aa; }
  .stat-item .el-icon { color: #f97316; }
  background: linear-gradient(135deg, #fff7ed, #ffffff);
}
.region-color-2 {
  border-top: 4px solid #14b8a6;
  .region-name { color: #0f766e; border-bottom-color: #ccfbf1; }
  .stat-item .el-icon { color: #14b8a6; }
  background: linear-gradient(135deg, #f0fdfa, #ffffff);
}
.region-color-3 {
  border-top: 4px solid #a855f7;
  .region-name { color: #6b21a5; border-bottom-color: #f3e8ff; }
  .stat-item .el-icon { color: #a855f7; }
  background: linear-gradient(135deg, #faf5ff, #ffffff);
}
.region-color-4 {
  border-top: 4px solid #ec489a;
  .region-name { color: #be185d; border-bottom-color: #fce7f3; }
  .stat-item .el-icon { color: #ec489a; }
  background: linear-gradient(135deg, #fdf2f8, #ffffff);
}
/* 差距分析 - 浅灰蓝 */
.content-block {
  background: #f1f5f9;
  border-radius: 16px;
  padding: 16px 20px;
  border: 1px solid #e2e8f0;
}
.text-content {
  line-height: 1.7;
  color: #334155;
  margin: 0;
}
/* PDCA 卡片 - 保持原有彩色（不改） */
.pdca-stages {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.pdca-card {
  border-radius: 20px;
  padding: 20px;
  transition: all 0.2s;
  border: 1px solid #f1f5f9;
  background: #ffffff;
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  }
}
.card-plan {
  background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
  border-left: 4px solid #3b82f6;
}
.card-do {
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
  border-left: 4px solid #10b981;
}
.card-check {
  background: linear-gradient(135deg, #fefce8 0%, #ffffff 100%);
  border-left: 4px solid #f59e0b;
}
.card-act {
  background: linear-gradient(135deg, #f5f3ff 0%, #ffffff 100%);
  border-left: 4px solid #8b5cf6;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}
.card-icon {
  width: 52px;
  height: 52px;
  background: white;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
  .card-plan & { color: #3b82f6; }
  .card-do & { color: #10b981; }
  .card-check & { color: #f59e0b; }
  .card-act & { color: #8b5cf6; }
}
.card-title {
  display: flex;
  flex-direction: column;
  .title-en {
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 1px;
    line-height: 1.2;
  }
  .title-cn {
    font-size: 13px;
    color: #64748b;
    font-weight: 500;
  }
  .card-plan & .title-en { color: #3b82f6; }
  .card-do & .title-en { color: #10b981; }
  .card-check & .title-en { color: #f59e0b; }
  .card-act & .title-en { color: #8b5cf6; }
}
.card-content {
  font-size: 15px;
  line-height: 1.7;
  color: #334155;
  white-space: pre-wrap;
  word-break: break-word;
}
/* 岗位调动建议 - 三个浅色 */
.transition-advice-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.advice-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 18px 20px;
  border-radius: 20px;
  transition: all 0.2s;
  border: 1px solid #eef2f6;
  .advice-number {
    font-size: 20px;
    font-weight: 800;
    min-width: 40px;
  }
  .advice-content {
    flex: 1;
  }
  .advice-title {
    font-weight: 600;
    font-size: 16px;
    margin-bottom: 8px;
  }
  .advice-text {
    font-size: 14px;
    line-height: 1.65;
  }
}
.advice-card-1 {
  background: linear-gradient(135deg, #e0f2fe, #ffffff);
  border-left: 4px solid #38bdf8;
  .advice-number { color: #0284c7; }
  .advice-title { color: #0c4a6e; }
  .advice-text { color: #334155; }
}
.advice-card-2 {
  background: linear-gradient(135deg, #dcfce7, #ffffff);
  border-left: 4px solid #4ade80;
  .advice-number { color: #15803d; }
  .advice-title { color: #14532d; }
  .advice-text { color: #334155; }
}
.advice-card-3 {
  background: linear-gradient(135deg, #fef3c7, #ffffff);
  border-left: 4px solid #fbbf24;
  .advice-number { color: #b45309; }
  .advice-title { color: #78350f; }
  .advice-text { color: #334155; }
}
/* 学习资源推荐 - 四种全新浅色（与区域不同） */
.resource-stages {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.resource-card {
  border-radius: 20px;
  transition: all 0.2s;
  overflow: hidden;
  background: #ffffff;
  border: 1px solid #eef2f6;
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
  }
}
.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}
.resource-title {
  font-size: 16px;
  font-weight: 600;
}
.resource-duration {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(0,0,0,0.04);
  padding: 4px 12px;
  border-radius: 30px;
  font-size: 12px;
}
.resource-content {
  padding: 16px 20px;
  font-size: 14px;
  line-height: 1.65;
}
.resource-line {
  margin-bottom: 8px;
  white-space: pre-wrap;
  word-break: break-word;
  &:last-child {
    margin-bottom: 0;
  }
}
.resource-list-item {
  padding-left: 8px;
  position: relative;
}
.resource-color-1 {
  border-top: 4px solid #f43f5e;
  .resource-header { background: linear-gradient(135deg, #ffe4e6, #ffffff); }
  .resource-title { color: #9f1239; }
  .resource-duration { background: #fecdd3; color: #9f1239; }
}
.resource-color-2 {
  border-top: 4px solid #06b6d4;
  .resource-header { background: linear-gradient(135deg, #cffafe, #ffffff); }
  .resource-title { color: #155e75; }
  .resource-duration { background: #a5f3fc; color: #155e75; }
}
.resource-color-3 {
  border-top: 4px solid #84cc16;
  .resource-header { background: linear-gradient(135deg, #ecfccb, #ffffff); }
  .resource-title { color: #3f6212; }
  .resource-duration { background: #d9f99d; color: #3f6212; }
}
.resource-color-4 {
  border-top: 4px solid #d946ef;
  .resource-header { background: linear-gradient(135deg, #fae8ff, #ffffff); }
  .resource-title { color: #86198f; }
  .resource-duration { background: #f3d4fc; color: #86198f; }
}
/* 右侧润色栏 */
.polish-card {
  position: sticky;
  top: 100px;
  border-radius: 24px;
  border: none;
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  :deep(.el-card__header) {
    padding: 18px 20px;
    border-bottom: 1px solid #f0f2f5;
  }
  :deep(.el-card__body) {
    padding: 20px;
  }
}
.polish-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  .el-icon {
    font-size: 20px;
    color: #3b82f6;
  }
}
@media (max-width: 1024px) {
  .report-grid {
    flex-direction: column;
  }
  .report-sidebar {
    width: 100%;
  }
  .polish-card {
    position: static;
    margin-top: 20px;
  }
}
@media (max-width: 768px) {
  .report-page {
    padding: 16px;
  }
  .section-card :deep(.el-card__body) {
    padding: 20px;
  }
  .info-grid {
    grid-template-columns: 1fr;
  }
  .info-item.full-width {
    grid-column: span 1;
  }
  .match-summary {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  .region-grid {
    grid-template-columns: 1fr;
  }
}
</style>