<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { UploadFile, UploadFiles } from 'element-plus'
import { uploadResume, getResumeVersions } from '@/api/student'
import { useUserStore } from '@/stores/user'
import { getResumeVersion } from '@/api/student'

const versionDialogVisible = ref(false)
const currentVersionDetail = ref<any>(null)
const loadingVersion = ref(false)

const router = useRouter()
const userStore = useUserStore()
const studentId = ref<number | null>(userStore.user?.studentId || null)

const viewVersion = async (versionId: number) => {
  if (!studentId.value) return
  loadingVersion.value = true
  versionDialogVisible.value = true
  try {
    const res = await getResumeVersion(studentId.value, versionId)
    currentVersionDetail.value = res
  } catch (error) {
    ElMessage.error('加载版本详情失败')
    versionDialogVisible.value = false
  } finally {
    loadingVersion.value = false
  }
}


const uploadForm = reactive({
  resumeName: '',
  targetJob: '',
  targetCity: '',
  note: ''
})

const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const parsedResultVisible = ref(false)

const parsedResult = reactive({
  education: '',
  major: '',
  overall_score: 0,
  skills: [] as string[],
  certificates: [] as string[],
  internships: [] as string[]
})

const versionList = ref<{ id: number; version: number; created_at: string }[]>([])

// 获取历史版本
const fetchVersions = async () => {
  let id = studentId.value
  if (!id) {
    const storedId = localStorage.getItem('student_id')
    if (storedId) {
      id = parseInt(storedId)
      studentId.value = id
      if (userStore.user) userStore.user.studentId = id
    } else {
      return
    }
  }
  try {
    const res = await getResumeVersions(id)
    versionList.value = Array.isArray(res) ? res : []
  } catch (error) {
    console.error('获取版本列表失败', error)
    versionList.value = []
  }
}

// 文件选择
const handleFileChange = (file: UploadFile, _files: UploadFiles) => {
  selectedFile.value = file.raw || null
  if (selectedFile.value) {
    uploadForm.resumeName = selectedFile.value.name
  }
}

const handleRemove = () => {
  selectedFile.value = null
  uploadForm.resumeName = ''
  parsedResultVisible.value = false
}

// 上传简历
const handleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先上传简历文件')
    return
  }

  uploading.value = true
  try {
    // uploadResume 直接返回后端对象（StudentResponse）
    const student = await uploadResume(selectedFile.value)
    studentId.value = student.id
    // 更新用户 store 中的 studentId
    if (!userStore.user?.studentId) {
      userStore.user!.studentId = student.id
      localStorage.setItem('student_id', String(student.id))
    }

    // 填充解析结果
    const profile = student.profile_json || {}
    parsedResult.education = profile.education || ''
    parsedResult.major = profile.major || ''
    parsedResult.overall_score = profile.overall_score || 0
    parsedResult.skills = profile.skills || []
    parsedResult.certificates = profile.certificates || []
    parsedResult.internships = profile.internships || []

    parsedResultVisible.value = true
    ElMessage.success('简历上传成功，画像已生成')

    // 刷新版本列表
    await fetchVersions()
  } catch (error: any) {
    ElMessage.error(error.message || '上传失败，请稍后重试')
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  if (studentId.value) {
    fetchVersions()
  }
})
</script>

<template>
  <div class="resume-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">简历上传</h2>
        <p class="page-subtitle">上传简历后，系统会自动解析并生成学生画像，同时保存历史版本。</p>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="15">
        <el-card class="panel-card">
          <template #header>
            <div class="panel-title">上传简历文件</div>
          </template>

          <el-upload
            class="upload-box"
            drag
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleRemove"
          >
            <div class="upload-inner">
              <div class="upload-icon">↑</div>
              <div class="upload-title">拖拽文件到这里，或点击上传</div>
              <div class="upload-desc">支持 PDF / DOCX / TXT</div>
            </div>
          </el-upload>

          <el-form label-position="top" class="resume-form">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="简历名称">
                  <el-input v-model="uploadForm.resumeName" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="目标岗位">
                  <el-input v-model="uploadForm.targetJob" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="目标城市">
                  <el-input v-model="uploadForm.targetCity" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="补充说明">
              <el-input v-model="uploadForm.note" type="textarea" :rows="4" />
            </el-form-item>

            <div class="form-actions">
              <el-button type="primary" :loading="uploading" @click="handleUpload">
                开始解析
              </el-button>
            </div>
          </el-form>
        </el-card>

        <el-card v-if="parsedResultVisible" class="panel-card">
          <template #header>
            <div class="panel-title">解析结果</div>
          </template>

          <el-row :gutter="16">
            <el-col :span="8">
              <div class="result-block">
                <div class="result-label">学历</div>
                <div class="result-value">{{ parsedResult.education || '未识别' }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="result-block">
                <div class="result-label">专业</div>
                <div class="result-value">{{ parsedResult.major || '未识别' }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="result-block">
                <div class="result-label">综合竞争力</div>
                <div class="result-value">{{ parsedResult.overall_score }}分</div>
              </div>
            </el-col>
          </el-row>

          <div class="section-block">
            <div class="section-title">识别到的技能</div>
            <div class="tag-wrap">
              <span v-for="tag in parsedResult.skills" :key="tag" class="soft-tag blue">{{ tag }}</span>
            </div>
          </div>

          <div class="section-block">
            <div class="section-title">识别到的证书</div>
            <div class="tag-wrap">
              <span v-for="tag in parsedResult.certificates" :key="tag" class="soft-tag yellow">{{ tag }}</span>
            </div>
          </div>

          <div class="section-block">
            <div class="section-title">识别到的实习/项目经历</div>
            <div class="experience-list">
              <div v-for="item in parsedResult.internships" :key="item" class="experience-item">
                {{ item }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="9">
        <el-card class="panel-card">
          <div class="guide-title">历史版本</div>
          <div class="version-list">
            <div v-for="item in versionList" :key="item.id" class="version-item">
              <div class="version-top">
                <div class="version-title">版本 v{{ item.version }}</div>
                <el-button size="small" @click="viewVersion(item.id)">查看</el-button>
              </div>
              <div class="version-time">{{ new Date(item.created_at).toLocaleString() }}</div>
            </div>
            <div v-if="versionList.length === 0" class="empty-tip">暂无历史版本</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 弹窗 -->
    <el-dialog v-model="versionDialogVisible" title="简历版本详情" width="60%" v-loading="loadingVersion">
      <div v-if="currentVersionDetail">
        <h4>简历原文</h4>
        <pre>{{ currentVersionDetail.resume_text }}</pre>
        <h4>画像信息</h4>
        <pre>{{ JSON.stringify(currentVersionDetail.profile_json, null, 2) }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
/* 保持原有样式不变 */
.empty-tip {
  text-align: center;
  color: var(--text-secondary);
  padding: 20px;
}

.resume-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.page-header {
  margin-bottom: 8px;
}
.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}
.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}
.panel-card {
  margin-bottom: 20px;
}
.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}
.upload-box {
  width: 100%;
  margin-bottom: 20px;
}
.upload-inner {
  padding: 40px 20px;
  text-align: center;
}
.upload-icon {
  font-size: 48px;
  color: #b0c4de;
}
.upload-title {
  font-size: 16px;
  margin: 12px 0 8px;
}
.upload-desc {
  font-size: 12px;
  color: #94a3b8;
}
.resume-form {
  margin-top: 10px;
}
.form-actions {
  margin-top: 10px;
  text-align: center;
}
.result-block {
  background: #f8fafc;
  padding: 12px;
  border-radius: 12px;
  text-align: center;
}
.result-label {
  font-size: 12px;
  color: #64748b;
}
.result-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}
.section-block {
  margin-top: 20px;
}
.section-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}
.tag-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.soft-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
}
.soft-tag.blue {
  background: #e0f2fe;
  color: #0369a1;
}
.soft-tag.yellow {
  background: #fef9c3;
  color: #854d0e;
}
.experience-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.experience-item {
  background: #f8fafc;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
}
.guide-title {
  font-weight: 700;
  margin-bottom: 12px;
}
.version-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.version-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}
.version-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.version-title {
  font-weight: 600;
}
.version-time {
  font-size: 12px;
  color: #64748b;
  margin-top: 6px;
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