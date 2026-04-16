<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getPlanningProfile, updatePlanningProfile } from '@/api/planning'

const userStore = useUserStore()
const loading = ref(false)
const isEditing = ref(false)   // ✅ 添加编辑状态

// 表单数据
const form = reactive({
  name: userStore.user?.username || '',
  gender: '',
  age: '',
  school: '',
  major: '',
  grade: '',
  city: '',
  interests: [] as string[],
  strengths: [] as string[],
  selfIntroduction: ''
})

// 经历列表
type ExperienceItem = {
  id: number
  type: '项目' | '活动' | '竞赛'
  title: string
  role: string
  description: string
  technologies?: string[]
}
const experiences = ref<ExperienceItem[]>([])

const newInterest = ref('')
const newStrength = ref('')

// 加载规划档案
const loadData = async () => {
  loading.value = true
  try {
    const res = await getPlanningProfile()
    form.interests = res.interests || []
    form.strengths = res.strengths || []
    form.selfIntroduction = res.self_introduction || ''
    form.grade = res.grade || ''
    form.city = res.intended_city || ''
    form.gender = res.gender || ''
    form.age = res.age || ''
    form.school = res.school || ''
    form.major = res.major || ''

    // 处理经历
    const expData = res.experiences || { projects: [], activities: [], competitions: [] }
    const expList: ExperienceItem[] = []
    const addExp = (type: ExperienceItem['type'], items: any[]) => {
      items.forEach((item, idx) => {
        expList.push({
          id: Date.now() + idx,
          type,
          title: item.name || '',
          role: item.role || '',
          description: item.description || '',
          technologies: item.technologies || []
        })
      })
    }
    addExp('项目', expData.projects || [])
    addExp('活动', expData.activities || [])
    addExp('竞赛', expData.competitions || [])
    experiences.value = expList
  } catch (error) {
    console.error('加载档案失败', error)
    ElMessage.error('加载档案失败')
  } finally {
    loading.value = false
  }
}

// 保存
const handleSave = async () => {
  loading.value = true
  try {
    const experiencesUpdate = {
      projects: experiences.value.filter(e => e.type === '项目').map(e => ({
        name: e.title,
        role: e.role,
        description: e.description,
        technologies: e.technologies || []
      })),
      activities: experiences.value.filter(e => e.type === '活动').map(e => ({
        name: e.title,
        role: e.role,
        description: e.description,
        technologies: e.technologies || []
      })),
      competitions: experiences.value.filter(e => e.type === '竞赛').map(e => ({
        name: e.title,
        role: e.role,
        description: e.description,
        technologies: e.technologies || []
      }))
    }
    await updatePlanningProfile({
      interests: form.interests,
      strengths: form.strengths,
      experiences: experiencesUpdate,
      self_introduction: form.selfIntroduction,
      grade: form.grade,
      intended_city: form.city,
      gender: form.gender,
      age: form.age,
      school: form.school,
      major: form.major
    })
    ElMessage.success('档案已保存')
    isEditing.value = false
    await loadData()
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    loading.value = false
  }
}

const handleEdit = () => { isEditing.value = true }
const handleCancel = () => {
  isEditing.value = false
  loadData()
  ElMessage.info('已取消编辑')
}

const addInterest = () => {
  if (!newInterest.value.trim()) return
  form.interests.push(newInterest.value.trim())
  newInterest.value = ''
}
const removeInterest = (idx: number) => { form.interests.splice(idx, 1) }

const addStrength = () => {
  if (!newStrength.value.trim()) return
  form.strengths.push(newStrength.value.trim())
  newStrength.value = ''
}
const removeStrength = (idx: number) => { form.strengths.splice(idx, 1) }

const addExperience = (type: ExperienceItem['type']) => {
  experiences.value.push({
    id: Date.now(),
    type,
    title: '',
    role: '',
    description: '',
    technologies: []
  })
}
const removeExperience = (id: number) => {
  experiences.value = experiences.value.filter(item => item.id !== id)
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="profile-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">我的档案</h2>
        <p class="page-subtitle">填写你的基础信息、兴趣和经历，系统才能做个性化职业规划。</p>
      </div>
      <div class="actions">
        <el-button v-if="!isEditing" type="primary" @click="handleEdit" :loading="loading">编辑档案</el-button>
        <template v-else>
          <el-button @click="handleCancel" :loading="loading">取消</el-button>
          <el-button type="primary" @click="handleSave" :loading="loading">保存</el-button>
        </template>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="panel-card">
          <template #header><div class="panel-title">基础信息</div></template>
          <el-form label-position="top">
            <el-row :gutter="16">
              <el-col :span="12"><el-form-item label="姓名"><el-input v-model="form.name" :disabled="!isEditing" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="性别"><el-select v-model="form.gender" :disabled="!isEditing" style="width:100%"><el-option label="男" value="男"/><el-option label="女" value="女"/><el-option label="其他" value="其他"/></el-select></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="年龄"><el-input v-model="form.age" :disabled="!isEditing" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="所在城市"><el-input v-model="form.city" :disabled="!isEditing" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="学校"><el-input v-model="form.school" :disabled="!isEditing" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="专业"><el-input v-model="form.major" :disabled="!isEditing" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="年级"><el-select v-model="form.grade" :disabled="!isEditing" style="width:100%"><el-option label="大一" value="大一"/><el-option label="大二" value="大二"/><el-option label="大三" value="大三"/><el-option label="大四" value="大四"/></el-select></el-form-item></el-col>
            </el-row>
            <el-form-item label="自我介绍"><el-input v-model="form.selfIntroduction" :disabled="!isEditing" type="textarea" :rows="4" placeholder="简单写一下你的兴趣、想尝试的方向、平时做过的事情" /></el-form-item>
          </el-form>
        </el-card>

        <el-card class="panel-card">
          <template #header><div class="panel-title">兴趣与优势</div></template>
          <div class="section-title">兴趣方向</div>
          <div class="tag-wrap">
            <span v-for="(tag, idx) in form.interests" :key="tag+idx" class="soft-tag blue">{{ tag }}<button v-if="isEditing" class="tag-close" @click="removeInterest(idx)">×</button></span>
          </div>
          <div v-if="isEditing" class="add-row"><el-input v-model="newInterest" placeholder="新增兴趣方向" /><el-button @click="addInterest">添加</el-button></div>
          <div class="section-title mt">优势能力</div>
          <div class="tag-wrap">
            <span v-for="(tag, idx) in form.strengths" :key="tag+idx" class="soft-tag yellow">{{ tag }}<button v-if="isEditing" class="tag-close" @click="removeStrength(idx)">×</button></span>
          </div>
          <div v-if="isEditing" class="add-row"><el-input v-model="newStrength" placeholder="新增优势能力" /><el-button @click="addStrength">添加</el-button></div>
        </el-card>

        <el-card class="panel-card">
          <template #header><div class="panel-title">个人经历</div></template>
          <div v-if="isEditing" class="experience-actions"><el-button @click="addExperience('项目')">新增项目</el-button><el-button @click="addExperience('活动')">新增活动</el-button><el-button @click="addExperience('竞赛')">新增竞赛</el-button></div>
          <div class="experience-list">
            <div v-for="item in experiences" :key="item.id" class="experience-card">
              <div class="experience-top"><el-tag round>{{ item.type }}</el-tag><el-button v-if="isEditing" text type="danger" @click="removeExperience(item.id)">删除</el-button></div>
              <el-row :gutter="16"><el-col :span="12"><el-form-item label="标题"><el-input v-model="item.title" :disabled="!isEditing" /></el-form-item></el-col><el-col :span="12"><el-form-item label="角色"><el-input v-model="item.role" :disabled="!isEditing" /></el-form-item></el-col></el-row>
              <el-form-item label="描述"><el-input v-model="item.description" :disabled="!isEditing" type="textarea" :rows="3" /></el-form-item>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="panel-card side-card">
          <div class="avatar-wrap"><div class="avatar">{{ (form.name || 'S').slice(0,1) }}</div><div class="student-name">{{ form.name || '未填写姓名' }}</div><div class="student-meta">{{ form.school || '学校未填写' }} · {{ form.major || '专业未填写' }}</div></div>
          <div class="side-section"><div class="side-title">当前阶段</div><div class="side-content">{{ form.grade || '未填写年级' }}</div></div>
          <div class="side-section"><div class="side-title">档案完成情况</div><div class="status-box"><div class="status-item"><span>基础资料</span><span>{{ form.name && form.school ? '已完善' : '待补充' }}</span></div><div class="status-item"><span>兴趣标签</span><span>{{ form.interests.length }} 个</span></div><div class="status-item"><span>经历条目</span><span>{{ experiences.length }} 条</span></div></div></div>
          <div class="side-section"><div class="side-title">为什么要填写？</div><ul class="tips-list"><li>系统会根据你的兴趣和能力推荐职业路径</li><li>经历越完整，成长建议越贴合你自己</li><li>后续路径推荐和计划生成都依赖这些信息</li></ul></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
/* 保留原有样式，此处省略（与之前相同） */
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.page-subtitle {
  margin-top: 16px;
  margin-bottom: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.actions {
  display: flex;
  gap: 10px;
}

.panel-card {
  margin-bottom: 20px;
}

.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.section-title.mt {
  margin-top: 18px;
}

.tag-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.soft-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 24px;
  font-size: 13px;
  background: #f0f2f5;
  color: #1f2d3d;
  transition: all 0.2s;
}

.soft-tag.blue {
  background: #e6f0ff;
  color: #2c5f9e;
}

.soft-tag.yellow {
  background: #fff7e0;
  color: #b87c00;
}

.tag-close {
  margin-left: 4px;
  cursor: pointer;
  font-weight: bold;
  background: none;
  border: none;
  color: inherit;
  font-size: 14px;
}

.add-row {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}

.experience-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.experience-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.experience-card {
  padding: 16px;
  background: #fafcff;
  border-radius: 16px;
}

.experience-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.side-card {
  position: sticky;
  top: 96px;
  align-self: flex-start;
}

.avatar-wrap {
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.avatar {
  width: 76px;
  height: 76px;
  margin: 0 auto 14px;
  border-radius: 50%;
  background: linear-gradient(135deg, #dceeff, #fff4cc);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
  color: #5578c9;
}

.student-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.student-meta {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.side-section {
  padding-top: 18px;
}

.side-content {
  background: #fafcff;
  border-radius: 14px;
  padding: 12px 14px;
  font-size: 14px;
  color: var(--text-regular);
}

.status-box {
  background: #fafcff;
  border-radius: 14px;
  padding: 12px 14px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-regular);
}

.tips-list {
  margin: 0;
  padding-left: 18px;
  color: var(--text-regular);
  line-height: 1.9;
  font-size: 14px;
}

@media (max-width: 992px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  .side-card {
    position: static;
  }
}

:deep(.el-card) {
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(2px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.95);
  }
}
</style>

