<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { matchStudent } from '@/api/match'
import { getJobProfile } from '@/api/jobs'

const router = useRouter()
const userStore = useUserStore()
const studentId = ref<number | null>(userStore.user?.studentId || null)

const loading = ref(false)
const matchFinished = ref(false)

const matchForm = reactive({
  targetJob: '',
  targetCity: '',
  salaryPreference: '',
  degreePreference: '',
  keyword: ''
})

const selectedJobId = ref<number | null>(null)

const matchSummary = reactive({
  totalJobs: 0,
  highMatchCount: 0,
  mediumMatchCount: 0,
  lowMatchCount: 0
})

type MatchResultItem = {
  job_id: number
  job_title: string
  total_score: number
  details: Record<string, number>
}

type MatchJob = {
  id: number
  title: string
  company: string
  city: string
  salary: string
  degree: string
  experience: string
  matchScore: number
  tags: string[]
  highlights: string[]
  gaps: string[]
  description: string
  responsibilities: string[]
  requirements: string[]
}

const dimensionMap: Record<string, string> = {
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
  base_match: '基础要求',
  professional_match: '职业技能',
  quality_match: '职业素养',
  potential_match: '发展潜力',
  total_score: '全局评分',
  internship_match: '实习匹配',
}

const jobList = ref<MatchJob[]>([])

// 画像弹窗相关
const profileDialogVisible = ref(false)
const currentProfile = ref<any>(null)
const loadingProfile = ref(false)

const generateHighlightsAndGaps = (details: Record<string, number>) => {
  const highlights: string[] = []
  const gaps: string[] = []
  for (const [key, value] of Object.entries(details)) {
    const chineseKey = dimensionMap[key] || key
    if (value >= 0.7) {
      highlights.push(`${chineseKey} 匹配度较高（${(value * 100).toFixed(0)}%）`)
    } else if (value < 0.5) {
      gaps.push(`${chineseKey} 匹配度较低（${(value * 100).toFixed(0)}%），需加强`)
    }
  }
  if (highlights.length === 0) highlights.push('暂无明显匹配亮点')
  if (gaps.length === 0) gaps.push('各项匹配度尚可，可进一步优化')
  return { highlights, gaps }
}

const runMatch = async () => {
  if (!studentId.value) {
    ElMessage.warning('未找到学生ID，请先上传简历')
    return
  }

  loading.value = true
  matchFinished.value = false

  try {
    const res = await matchStudent(studentId.value)
    const matchResults: MatchResultItem[] = res

    const jobs: MatchJob[] = matchResults.map((item) => {
      const { highlights, gaps } = generateHighlightsAndGaps(item.details)
      return {
        id: item.job_id,
        title: item.job_title,
        company: '待补充',
        city: '待补充',
        salary: '面议',
        degree: '本科及以上',
        experience: '经验不限',
        matchScore: Math.round(item.total_score * 100),
        tags: Object.keys(item.details).slice(0, 4).map(key => dimensionMap[key] || key),
        highlights,
        gaps,
        description: `匹配度 ${(item.total_score * 100).toFixed(0)}%，详情见下方维度分析。`,
        responsibilities: [],
        requirements: [],
      }
    })

    jobList.value = jobs
    matchFinished.value = true

    matchSummary.totalJobs = jobs.length
    matchSummary.highMatchCount = jobs.filter(j => j.matchScore >= 85).length
    matchSummary.mediumMatchCount = jobs.filter(j => j.matchScore >= 70 && j.matchScore < 85).length
    matchSummary.lowMatchCount = jobs.filter(j => j.matchScore < 70).length

    if (jobs.length > 0) {
      selectedJobId.value = jobs[0].id
      ElMessage.success('岗位匹配完成，已为你推荐最适合的岗位')
    } else {
      selectedJobId.value = null
      ElMessage.warning('未找到符合条件的岗位')
    }
  } catch (error: any) {
    console.error('匹配失败', error)
    ElMessage.error(error.message || '岗位匹配失败，请稍后重试')
    matchFinished.value = false
  } finally {
    loading.value = false
  }
}

const filteredJobList = computed(() => {
  let list = jobList.value
  if (matchForm.targetJob) {
    list = list.filter(job => job.title.includes(matchForm.targetJob))
  }
  if (matchForm.targetCity) {
    list = list.filter(job => job.city.includes(matchForm.targetCity))
  }
  if (matchForm.keyword) {
    const kw = matchForm.keyword.toLowerCase()
    list = list.filter(job => job.title.toLowerCase().includes(kw) || job.tags.some(t => t.toLowerCase().includes(kw)))
  }
  return list
})

const selectedJob = computed(() => {
  return jobList.value.find(item => item.id === selectedJobId.value) || null
})

const scoreLevelText = computed(() => {
  if (!selectedJob.value) return ''
  const score = selectedJob.value.matchScore
  if (score >= 85) return '高匹配'
  if (score >= 70) return '中匹配'
  return '低匹配'
})

const scoreTagClass = computed(() => {
  if (!selectedJob.value) return ''
  const score = selectedJob.value.matchScore
  if (score >= 85) return 'green'
  if (score >= 70) return 'blue'
  return 'yellow'
})

const handleSelectJob = (job: MatchJob) => {
  selectedJobId.value = job.id
}

const resetForm = () => {
  matchForm.targetJob = ''
  matchForm.targetCity = ''
  matchForm.salaryPreference = ''
  matchForm.degreePreference = ''
  matchForm.keyword = ''
  selectedJobId.value = null
  matchFinished.value = false
  matchSummary.totalJobs = 0
  matchSummary.highMatchCount = 0
  matchSummary.mediumMatchCount = 0
  matchSummary.lowMatchCount = 0
  ElMessage.success('筛选条件已重置')
}

const goOptimizeResume = () => {
  if (!selectedJob.value) {
    ElMessage.warning('请先选择岗位')
    return
  }
  if (!studentId.value) {
    ElMessage.warning('学生ID不存在，请先上传简历')
    return
  }
  router.push({
    path: '/job/report',
    query: {
      student_id: studentId.value.toString(),
      job_title: selectedJob.value.title
    }
  })
}

const viewJobProfile = async (jobTitle: string) => {
  loadingProfile.value = true
  try {
    const profile = await getJobProfile(jobTitle)
    if (profile.region_stats && typeof profile.region_stats === 'string') {
      profile.region_stats = JSON.parse(profile.region_stats)
    }
    currentProfile.value = profile
    profileDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '加载岗位画像失败')
  } finally {
    loadingProfile.value = false
  }
}

onMounted(() => {
  if (!studentId.value) {
    const storedId = localStorage.getItem('student_id')
    if (storedId) {
      studentId.value = parseInt(storedId)
      if (userStore.user) userStore.user.studentId = studentId.value
    }
  }
})
</script>

<template>
  <div class="match-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">岗位匹配</h2>
        <p class="page-subtitle">
          基于简历解析结果，匹配适合的岗位方向，并展示匹配度与能力差距分析。
        </p>
      </div>
      <div class="match-actions">
        <el-button type="primary" :loading="loading" @click="runMatch">开始匹配</el-button>
        <el-button @click="resetForm">重置条件</el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="panel-card">
          <template #header><div class="panel-title">岗位推荐列表</div></template>
          <div v-if="!matchFinished" class="empty-block">
            点击“开始匹配”后，系统将根据简历能力画像推荐岗位。
          </div>
          <div v-else-if="jobList.length === 0" class="empty-block">
            未找到匹配岗位，请完善简历信息后重试。
          </div>
          <div v-else class="job-list">
            <div
              v-for="item in jobList"
              :key="item.id"
              class="job-item"
              :class="{ active: selectedJobId === item.id }"
              @click="handleSelectJob(item)"
            >
              <div class="job-top">
                <div class="job-title">{{ item.title }}</div>
                <div style="display: flex; gap: 8px; align-items: center;">
                  <div class="job-score">{{ item.matchScore }}%</div>
                  <el-button size="small" text type="primary" class="profile-btn" @click.stop="viewJobProfile(item.title)">画像</el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="panel-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div class="panel-title">岗位详情与分析</div>
              <el-button v-if="selectedJob" type="primary" size="small" @click="goOptimizeResume">生成报告</el-button>
            </div>
          </template>
          <div v-if="!selectedJob" class="empty-block">
            请选择左侧岗位查看具体匹配分析。
          </div>
          <div v-else class="detail-wrap">
            <div class="detail-top">
              <div>
                <div class="detail-title">{{ selectedJob.title }}</div>
              </div>
              <span class="level-tag" :class="scoreTagClass">{{ scoreLevelText }}</span>
            </div>
            <div class="section-block">
              <div class="section-title">匹配度</div>
              <el-progress :percentage="selectedJob.matchScore" :stroke-width="12" :show-text="true" />
            </div>
            <div class="section-block">
              <div class="section-title">岗位描述</div>
              <div class="text-content">{{ selectedJob.description }}</div>
            </div>
            <div class="section-block">
              <div class="section-title">匹配亮点</div>
              <div class="analysis-list">
                <div v-for="item in selectedJob.highlights" :key="item" class="analysis-item success">
                  {{ item }}
                </div>
              </div>
            </div>
            <div class="section-block">
              <div class="section-title">能力差距</div>
              <div class="analysis-list">
                <div v-for="item in selectedJob.gaps" :key="item" class="analysis-item warning">
                  {{ item }}
                </div>
              </div>
            </div>
            <div class="section-block">
              <div class="section-title">核心标签</div>
              <div class="tag-wrap">
                <span v-for="tag in selectedJob.tags" :key="tag" class="soft-tag yellow">{{ tag }}</span>
              </div>
            </div>
            <div class="detail-actions">
              <el-button type="primary" @click="goOptimizeResume">生成报告</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 岗位画像弹窗 -->
    <el-dialog v-model="profileDialogVisible" :title="currentProfile?.job_title || '岗位画像'" width="700px" v-loading="loadingProfile">
      <div v-if="currentProfile" class="profile-detail">
        <!-- 技能要求 -->
        <div class="section">
          <h4>技能要求</h4>
          <div class="tag-wrap">
            <span v-for="skill in (typeof currentProfile.skills === 'string' ? JSON.parse(currentProfile.skills) : currentProfile.skills)" :key="skill" class="soft-tag blue">{{ skill }}</span>
          </div>
        </div>
        <!-- 证书要求 -->
        <div class="section">
          <h4>证书要求</h4>
          <div class="tag-wrap">
            <span v-for="cert in (typeof currentProfile.certificates === 'string' ? JSON.parse(currentProfile.certificates) : currentProfile.certificates)" :key="cert" class="soft-tag yellow">{{ cert }}</span>
          </div>
        </div>
        <!-- 能力评分 -->
        <div class="section">
          <h4>能力评分</h4>
          <div class="score-grid">
            <div class="score-item">创新：{{ currentProfile.innovation_score }}分</div>
            <div class="score-item">学习：{{ currentProfile.learning_score }}分</div>
            <div class="score-item">抗压：{{ currentProfile.stress_score }}分</div>
            <div class="score-item">沟通：{{ currentProfile.communication_score }}分</div>
          </div>
        </div>
        <!-- 能力说明 -->
        <div class="section">
          <h4>能力说明</h4>
          <p><strong>创新能力说明：</strong>{{ currentProfile.innovation_reason || '无' }}</p>
          <p><strong>学习能力说明：</strong>{{ currentProfile.learning_reason || '无' }}</p>
          <p><strong>抗压能力说明：</strong>{{ currentProfile.stress_reason || '无' }}</p>
          <p><strong>沟通能力说明：</strong>{{ currentProfile.communication_reason || '无' }}</p>
        </div>
        <!-- 置信度说明 -->
        <div class="section" v-if="currentProfile.confidence_reason">
          <h4>置信度说明</h4>
          <p>{{ currentProfile.confidence_reason }}</p>
        </div>
        <!-- 招聘要求 -->
        <div class="section">
          <h4>招聘要求</h4>
          <p><strong>学历：</strong>{{ currentProfile.education_required || '无' }}</p>
          <p><strong>专业：</strong>{{ currentProfile.major_required || '无' }}</p>
          <p><strong>经验：</strong>{{ currentProfile.experience_required || '无' }}</p>
          <p><strong>语言：</strong>{{ currentProfile.language_required || '无' }}</p>
          <p><strong>实习要求：</strong>{{ currentProfile.internship_required }}</p>
          <p v-if="currentProfile.industry_background"><strong>行业背景：</strong>{{ currentProfile.industry_background }}</p>
          <p v-if="currentProfile.other_requirements"><strong>其他要求：</strong>{{ currentProfile.other_requirements }}</p>
        </div>
        <!-- 区域机会分析 -->
        <div class="section" v-if="currentProfile.region_stats && currentProfile.region_stats.length">
          <h4>区域机会分析</h4>
          <el-table :data="currentProfile.region_stats" border size="small" style="width: 100%">
            <el-table-column prop="region" label="地区" width="80" />
            <el-table-column prop="demand_count" label="岗位数量" width="100" />
            <el-table-column label="平均薪资(K)" width="120">
              <template #default="{ row }">
                {{ row.salary_min_avg }} - {{ row.salary_max_avg }}
              </template>
            </el-table-column>
            <el-table-column prop="top_cities" label="主要城市">
              <template #default="{ row }">
                {{ row.top_cities.join('、') }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.match-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.match-actions {
  display: flex;
  gap: 12px;
}

.page-subtitle {
  margin: -6px 0 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.panel-card {
  margin-bottom: 20px;
}

.panel-title,
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.job-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.job-item {
  padding: 14px;
  border-radius: 14px;
  background: #fafcff;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.job-item:hover {
  border-color: #dceeff;
  background: #f4f8ff;
}

.job-item.active {
  border-color: #7da2ff;
  background: #eef4ff;
}

.job-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.job-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.job-score {
  font-size: 16px;
  font-weight: 700;
  color: #567fd8;
}

.detail-wrap {
  display: flex;
  flex-direction: column;
}

.detail-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 12px;
}

.detail-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.level-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.level-tag.green {
  background: #e8f8ee;
  color: #1f9d55;
}

.level-tag.blue {
  background: #dceeff;
  color: #567fd8;
}

.level-tag.yellow {
  background: #fff4cc;
  color: #a68118;
}

.section-block {
  margin-top: 22px;
}

.text-content {
  margin-top: 12px;
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-regular);
}

.analysis-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
}

.analysis-item {
  padding: 12px 14px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.7;
}

.analysis-item.success {
  background: #eef9f1;
  color: #256f48;
}

.analysis-item.warning {
  background: #fff8e8;
  color: #9a6b00;
}

.tag-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
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

.detail-actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-start;
}

.empty-block {
  padding: 42px 16px;
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

/* 弹窗样式 */
.profile-detail {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 8px;
}

.section {
  margin-bottom: 20px;
  h4 {
    margin-bottom: 8px;
    color: var(--text-primary);
    font-size: 16px;
  }
  p {
    margin: 4px 0;
    line-height: 1.6;
  }
}

.score-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 8px;
}

.score-item {
  background: #fafcff;
  padding: 8px 12px;
  border-radius: 8px;
}

.profile-btn {
  color: white !important;
}

:deep(.el-card) {
  background: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(2px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.95);
  }
}
</style>