<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getStudent, updateStudentProfile } from '@/api/student'
import type { StudentProfileUpdateRequest } from '@/api/student'
import { onBeforeRouteUpdate } from 'vue-router'

const userStore = useUserStore()
const studentId = ref<number | null>(userStore.user?.studentId || null)
const loading = ref(false)
const isEditing = ref(false)

// 表单数据
const form = reactive({
  name: '',
  gender: '',
  age: '',
  phone: '',
  email: '',
  school: '',
  major: '',
  education: '',
  graduationYear: '',
  targetJob: '',
  targetCity: '',
  selfIntroduction: '',
  skills: [] as string[],           // 技能数组
  certificates: [] as string[],     // 证书数组
  languages: [] as string[],        // 语言数组（前端用，后端存储分号分隔字符串）
  workExperiences: [] as string[],  // 工作/社团经历数组（前端用，后端分号分隔）
  internships: [] as string[],      // 实习经历数组
  innovationScore: 0,
  innovationReason: '',
  learningScore: 0,
  learningReason: '',
  stressScore: 0,
  stressReason: '',
  communicationScore: 0,
  communicationReason: '',
  overallScore: 0,
  overallReason: '',
  confidenceScore: 0,
  confidenceReason: ''
})

// 临时输入框
const newSkill = ref('')
const newCertificate = ref('')
const newLanguage = ref('')
const newWorkExp = ref('')
const newInternship = ref('')

// 加载学生数据
const loadStudentData = async () => {
  let id = studentId.value
  if (!id) {
    const storedId = localStorage.getItem('student_id')
    if (storedId) {
      id = parseInt(storedId)
      studentId.value = id
      if (userStore.user) userStore.user.studentId = id
    } else {
      ElMessage.warning('未找到学生ID，请先上传简历')
      return
    }
  }

  loading.value = true
  try {
    const res = await getStudent(id)
    const profile = res.profile_json || {}

    form.name = res.name || ''
    form.gender = profile.manual_basics?.gender || ''
    form.age = profile.age || ''
    form.phone = profile.phone || ''
    form.email = profile.email || ''
    form.school = profile.manual_basics?.school || ''
    form.major = profile.major || ''
    form.education = profile.education || ''
    form.graduationYear = profile.graduation_year || ''
    form.targetJob = profile.target_job || ''
    form.targetCity = profile.manual_basics?.intended_city || ''
    form.selfIntroduction = profile.self_introduction || ''
    form.skills = profile.skills || []
    form.certificates = profile.certificates || []

    // 语言：后端存储为分号分隔的字符串，前端拆分为数组
    const langStr = profile.language || ''
    form.languages = langStr ? langStr.split(';').map(s => s.trim()) : []
    // 工作经历：同样分号分隔
    const workStr = profile.work_experience || ''
    form.workExperiences = workStr ? workStr.split(';').map(s => s.trim()) : []
    // 实习经历：后端可能是数组，直接使用
    form.internships = profile.internships || []

    form.innovationScore = profile.innovation_score || 0
    form.innovationReason = profile.innovation_reason || ''
    form.learningScore = profile.learning_score || 0
    form.learningReason = profile.learning_reason || ''
    form.stressScore = profile.stress_score || 0
    form.stressReason = profile.stress_reason || ''
    form.communicationScore = profile.communication_score || 0
    form.communicationReason = profile.communication_reason || ''
    form.overallScore = profile.overall_score || 0
    form.overallReason = profile.overall_reason || ''
    form.confidenceScore = profile.confidence_score || 0
    form.confidenceReason = profile.confidence_reason || ''
  } catch (error) {
    console.error(error)
    ElMessage.error('加载学生信息失败')
  } finally {
    loading.value = false
  }
}

// 保存修改
const handleSave = async () => {
  if (!studentId.value) return
  loading.value = true
  try {
    const updateData: StudentProfileUpdateRequest = {
      manual_basics: {
        intended_city: form.targetCity,
        gender: form.gender,
        school: form.school,
        grade: form.graduationYear
      },
      skills: form.skills,
      certificates: form.certificates,
      age: form.age,
      phone: form.phone,
      email: form.email,
      graduation_year: form.graduationYear,
      target_job: form.targetJob,
      self_introduction: form.selfIntroduction,
      // 将数组转换为分号分隔的字符串
      language: form.languages.join(';'),
      work_experience: form.workExperiences.join(';'),
      internships: form.internships,
      innovation_score: form.innovationScore,
      innovation_reason: form.innovationReason,
      learning_score: form.learningScore,
      learning_reason: form.learningReason,
      stress_score: form.stressScore,
      stress_reason: form.stressReason,
      communication_score: form.communicationScore,
      communication_reason: form.communicationReason,
      overall_score: form.overallScore,
      overall_reason: form.overallReason,
      confidence_score: form.confidenceScore,
      confidence_reason: form.confidenceReason
    }

    await updateStudentProfile(studentId.value, updateData)
    ElMessage.success('信息已保存')
    isEditing.value = false
    await loadStudentData()
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    loading.value = false
  }
}

const handleEdit = () => { isEditing.value = true }
const handleCancel = () => {
  isEditing.value = false
  loadStudentData()
  ElMessage.info('已取消编辑')
}

// 技能操作
const addSkill = () => {
  if (!newSkill.value.trim()) return
  form.skills.push(newSkill.value.trim())
  newSkill.value = ''
}
const removeSkill = (idx: number) => { form.skills.splice(idx, 1) }

// 证书操作
const addCertificate = () => {
  if (!newCertificate.value.trim()) return
  form.certificates.push(newCertificate.value.trim())
  newCertificate.value = ''
}
const removeCertificate = (idx: number) => { form.certificates.splice(idx, 1) }

// 语言操作
const addLanguage = () => {
  if (!newLanguage.value.trim()) return
  form.languages.push(newLanguage.value.trim())
  newLanguage.value = ''
}
const removeLanguage = (idx: number) => { form.languages.splice(idx, 1) }

// 工作/社团经历操作
const addWorkExp = () => {
  if (!newWorkExp.value.trim()) return
  form.workExperiences.push(newWorkExp.value.trim())
  newWorkExp.value = ''
}
const removeWorkExp = (idx: number) => { form.workExperiences.splice(idx, 1) }

// 实习经历操作（保持列表）
const addInternship = () => {
  if (!newInternship.value.trim()) return
  form.internships.push(newInternship.value.trim())
  newInternship.value = ''
}
const removeInternship = (idx: number) => { form.internships.splice(idx, 1) }

onMounted(() => {
  if (studentId.value) loadStudentData()
  else ElMessage.warning('请先上传简历')
})
onBeforeRouteUpdate(() => { loadStudentData() })
</script>

<template>
  <div class="profile-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">我的信息</h2>
        <p class="page-subtitle">完善求职相关资料，让岗位匹配结果更准确。</p>
      </div>
      <div class="actions">
        <el-button v-if="!isEditing" type="primary" @click="handleEdit" :loading="loading">编辑信息</el-button>
        <template v-else>
          <el-button @click="handleCancel" :loading="loading">取消</el-button>
          <el-button type="primary" @click="handleSave" :loading="loading">保存</el-button>
        </template>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="16">
        <!-- 基本信息 -->
        <el-card class="panel-card">
          <template #header><div class="panel-title">基本信息</div></template>
          <el-form label-position="top">
            <el-row :gutter="16">
              <el-col :span="12"><el-form-item label="姓名"><el-input v-model="form.name" :disabled="!isEditing" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="性别"><el-select v-model="form.gender" :disabled="!isEditing" style="width:100%"><el-option label="男" value="男"/><el-option label="女" value="女"/><el-option label="其他" value="其他"/></el-select></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="年龄"><el-input v-model="form.age" :disabled="!isEditing" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="联系电话"><el-input v-model="form.phone" :disabled="!isEditing" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="邮箱"><el-input v-model="form.email" :disabled="!isEditing" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="毕业年份"><el-input v-model="form.graduationYear" :disabled="!isEditing" /></el-form-item></el-col>
            </el-row>
          </el-form>
        </el-card>

        <!-- 教育背景与求职意向 -->
        <el-card class="panel-card">
          <template #header><div class="panel-title">教育背景与求职意向</div></template>
          <el-form label-position="top">
            <el-row :gutter="16">
              <el-col :span="12"><el-form-item label="学校"><el-input v-model="form.school" :disabled="!isEditing" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="专业"><el-input v-model="form.major" :disabled="!isEditing" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="学历"><el-select v-model="form.education" :disabled="!isEditing" style="width:100%"><el-option label="专科" value="专科"/><el-option label="本科" value="本科"/><el-option label="硕士" value="硕士"/><el-option label="博士" value="博士"/></el-select></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="目标岗位"><el-input v-model="form.targetJob" :disabled="!isEditing" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="目标城市"><el-input v-model="form.targetCity" :disabled="!isEditing" /></el-form-item></el-col>
            </el-row>
            <el-form-item label="个人介绍"><el-input v-model="form.selfIntroduction" :disabled="!isEditing" type="textarea" :rows="4" /></el-form-item>
          </el-form>
        </el-card>

        <!-- 技能与证书 -->
        <el-card class="panel-card">
          <template #header><div class="panel-title">技能与证书</div></template>
          <div class="sub-title">技能</div>
          <div class="tag-wrap">
            <span v-for="(skill, idx) in form.skills" :key="idx" class="soft-tag blue">
              {{ skill }}
              <button v-if="isEditing" class="tag-close" @click="removeSkill(idx)">×</button>
            </span>
          </div>
          <div v-if="isEditing" class="add-row">
            <el-input v-model="newSkill" placeholder="新增技能" />
            <el-button @click="addSkill">添加</el-button>
          </div>

          <div class="sub-title">证书</div>
          <div class="tag-wrap">
            <span v-for="(cert, idx) in form.certificates" :key="idx" class="soft-tag yellow">
              {{ cert }}
              <button v-if="isEditing" class="tag-close" @click="removeCertificate(idx)">×</button>
            </span>
          </div>
          <div v-if="isEditing" class="add-row">
            <el-input v-model="newCertificate" placeholder="新增证书" />
            <el-button @click="addCertificate">添加</el-button>
          </div>
        </el-card>

        <!-- 能力评估 -->
        <el-card class="panel-card">
          <template #header><div class="panel-title">能力评估</div></template>
          <div class="score-grid">
            <div class="score-item">
              <strong>创新能力</strong>：{{ form.innovationScore }}分
              <el-input v-if="isEditing" v-model="form.innovationReason" type="textarea" :rows="2" placeholder="创新能力说明" />
              <p v-else class="reason">{{ form.innovationReason || '暂无说明' }}</p>
            </div>
            <div class="score-item">
              <strong>学习能力</strong>：{{ form.learningScore }}分
              <el-input v-if="isEditing" v-model="form.learningReason" type="textarea" :rows="2" placeholder="学习能力说明" />
              <p v-else class="reason">{{ form.learningReason || '暂无说明' }}</p>
            </div>
            <div class="score-item">
              <strong>抗压能力</strong>：{{ form.stressScore }}分
              <el-input v-if="isEditing" v-model="form.stressReason" type="textarea" :rows="2" placeholder="抗压能力说明" />
              <p v-else class="reason">{{ form.stressReason || '暂无说明' }}</p>
            </div>
            <div class="score-item">
              <strong>沟通能力</strong>：{{ form.communicationScore }}分
              <el-input v-if="isEditing" v-model="form.communicationReason" type="textarea" :rows="2" placeholder="沟通能力说明" />
              <p v-else class="reason">{{ form.communicationReason || '暂无说明' }}</p>
            </div>
          </div>
          <div class="score-summary">
            <p><strong>综合竞争力评分：</strong>{{ form.overallScore }}分</p>
            <p><strong>评分理由：</strong>{{ form.overallReason }}</p>
            <p><strong>置信度：</strong>{{ form.confidenceScore }}分</p>
            <p><strong>置信度理由：</strong>{{ form.confidenceReason }}</p>
          </div>
        </el-card>

        <!-- 实践经历 -->
        <el-card class="panel-card">
          <template #header><div class="panel-title">实践经历</div></template>

          <div class="sub-title">语言能力</div>
          <div class="tag-wrap">
            <span v-for="(lang, idx) in form.languages" :key="idx" class="soft-tag green">
              {{ lang }}
              <button v-if="isEditing" class="tag-close" @click="removeLanguage(idx)">×</button>
            </span>
          </div>
          <div v-if="isEditing" class="add-row">
            <el-input v-model="newLanguage" placeholder="新增语言（如：英语CET-6）" />
            <el-button @click="addLanguage">添加</el-button>
          </div>

          <div class="sub-title">工作/社团经历</div>
          <div class="tag-wrap">
            <span v-for="(exp, idx) in form.workExperiences" :key="idx" class="soft-tag orange">
              {{ exp }}
              <button v-if="isEditing" class="tag-close" @click="removeWorkExp(idx)">×</button>
            </span>
          </div>
          <div v-if="isEditing" class="add-row">
            <el-input v-model="newWorkExp" placeholder="新增经历（如：学校计算机协会 技术部部长）" />
            <el-button @click="addWorkExp">添加</el-button>
          </div>

          <div class="sub-title">实习经历</div>
          <div class="internship-list">
            <div v-for="(item, idx) in form.internships" :key="idx" class="internship-item">
              <el-input v-model="form.internships[idx]" :disabled="!isEditing" placeholder="实习经历描述" />
              <el-button v-if="isEditing" type="danger" size="small" @click="removeInternship(idx)">删除</el-button>
            </div>
          </div>
          <div v-if="isEditing" class="add-row">
            <el-input v-model="newInternship" placeholder="新增实习经历" />
            <el-button @click="addInternship">添加</el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧信息卡 -->
      <el-col :span="8">
        <el-card class="panel-card side-card">
          <div class="avatar-wrap"><div class="avatar">{{ (form.name || 'S').slice(0,1) }}</div><div class="student-name">{{ form.name || '未填写姓名' }}</div><div class="student-meta">{{ form.school || '学校未填写' }} · {{ form.major || '专业未填写' }}</div></div>
          <div class="side-section"><div class="side-title">求职方向</div><div class="side-content">{{ form.targetJob || '暂未填写目标岗位' }}</div></div>
          <div class="side-section"><div class="side-title">资料完成情况</div><div class="status-box">
            <div class="status-item"><span>基础资料</span><span>{{ form.name && form.school ? '已完善' : '待补充' }}</span></div>
            <div class="status-item"><span>技能</span><span>{{ form.skills.length }} 个</span></div>
            <div class="status-item"><span>证书</span><span>{{ form.certificates.length }} 个</span></div>
            <div class="status-item"><span>语言</span><span>{{ form.languages.length }} 项</span></div>
            <div class="status-item"><span>工作/社团</span><span>{{ form.workExperiences.length }} 项</span></div>
            <div class="status-item"><span>实习经历</span><span>{{ form.internships.length }} 条</span></div>
            <div class="status-item"><span>能力评估</span><span>{{ form.innovationScore ? '已评估' : '待完善' }}</span></div>
          </div></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
.profile-page { display: flex; flex-direction: column; gap: 20px; }
.page-header { display: flex; justify-content: space-between; gap: 20px; align-items: flex-start; }
.page-subtitle { margin: -6px 0 0; font-size: 14px; color: var(--text-secondary); }
.actions { display: flex; gap: 10px; }
.panel-card { margin-bottom: 20px; }
.panel-title { font-size: 16px; font-weight: 700; color: var(--text-primary); }
.sub-title { font-size: 14px; font-weight: 600; color: var(--text-primary); margin: 16px 0 8px; }
.tag-wrap { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; }
.soft-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 24px;
  font-size: 13px;
}
.soft-tag.blue { background: #dceeff; color: #567fd8; }
.soft-tag.yellow { background: #fff4cc; color: #a68118; }
.soft-tag.green { background: #dff7e8; color: #3f9160; }
.soft-tag.orange { background: #fff0e0; color: #c97e00; }
.tag-close { margin-left: 4px; cursor: pointer; font-weight: bold; background: none; border: none; color: inherit; }
.add-row { display: flex; gap: 10px; margin-top: 8px; margin-bottom: 8px; }
.score-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 16px; }
.score-item { background: #fafcff; padding: 12px; border-radius: 12px; }
.score-item .reason { margin-top: 8px; font-size: 13px; color: var(--text-secondary); }
.score-summary { background: #fafcff; padding: 12px; border-radius: 12px; }
.internship-list { display: flex; flex-direction: column; gap: 12px; margin-top: 8px; }
.internship-item { display: flex; gap: 8px; align-items: center; }
.internship-item .el-input { flex: 1; }
.side-card { position: sticky; top: 96px; align-self: flex-start; }
.avatar-wrap { text-align: center; padding-bottom: 20px; border-bottom: 1px solid var(--border-color); }
.avatar { width: 76px; height: 76px; margin: 0 auto 14px; border-radius: 50%; background: linear-gradient(135deg, #dceeff, #fff4cc); display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 700; color: #5578c9; }
.student-name { font-size: 20px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px; }
.student-meta { font-size: 13px; color: var(--text-secondary); line-height: 1.6; }
.side-section { padding-top: 18px; }
.side-content { background: #fafcff; border-radius: 14px; padding: 12px 14px; font-size: 14px; color: var(--text-regular); }
.status-box { background: #fafcff; border-radius: 14px; padding: 12px 14px; }
.status-item { display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px; color: var(--text-regular); }
@media (max-width: 992px) {
  .page-header { flex-direction: column; align-items: stretch; }
  .side-card { position: static; }
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