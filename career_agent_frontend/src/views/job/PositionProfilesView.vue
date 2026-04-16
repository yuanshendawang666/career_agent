<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getJobs, getJobProfile } from '@/api/jobs'

const loading = ref(false)
const loadingProfile = ref(false)
const keyword = ref('')
const activeTag = ref('全部')
const tags = ref<string[]>(['全部'])

const jobTitles = ref<string[]>([])
const dialogVisible = ref(false)
const selectedProfile = ref<any>(null)

// 加载岗位名称列表
const loadJobTitles = async () => {
  loading.value = true
  try {
    const jobs = await getJobs()
    const uniqueTitles = [...new Set(jobs.map((job: any) => job.job_title))]
    jobTitles.value = uniqueTitles
    const categories = new Set<string>()
    uniqueTitles.forEach(title => {
      const cat = title.split(/[ -]/)[0]
      categories.add(cat)
    })
    tags.value = ['全部', ...Array.from(categories)]
  } catch (error) {
    ElMessage.error('加载岗位列表失败')
  } finally {
    loading.value = false
  }
}

// 筛选后的岗位名称列表
const filteredTitles = computed(() => {
  let list = jobTitles.value
  if (keyword.value) {
    const kw = keyword.value.toLowerCase()
    list = list.filter(title => title.toLowerCase().includes(kw))
  }
  if (activeTag.value !== '全部') {
    list = list.filter(title => title.split(/[ -]/)[0] === activeTag.value)
  }
  return list
})

// 查看岗位画像
const viewProfile = async (jobTitle: string) => {
  loadingProfile.value = true
  try {
    const profile = await getJobProfile(jobTitle)
    // 如果 region_stats 是字符串，解析为数组
    if (profile.region_stats && typeof profile.region_stats === 'string') {
      profile.region_stats = JSON.parse(profile.region_stats)
    }
    selectedProfile.value = profile
    dialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '加载岗位画像失败')
  } finally {
    loadingProfile.value = false
  }
}

onMounted(() => {
  loadJobTitles()
})
</script>

<template>
  <div class="profiles-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">岗位画像库</h2>
        <p class="page-subtitle">查看典型岗位的学历、技能、能力与实习要求。</p>
      </div>
    </div>

    <el-card class="filter-card">
      <div class="filter-row">
        <el-input
          v-model="keyword"
          placeholder="搜索岗位名称"
          clearable
          class="search-input"
        />
        <div class="tag-filter">
          <button
            v-for="tag in tags"
            :key="tag"
            class="tag-btn"
            :class="{ active: activeTag === tag }"
            @click="activeTag = tag"
          >
            {{ tag }}
          </button>
        </div>
      </div>
    </el-card>

    <el-card class="panel-card" v-loading="loading">
      <el-table :data="filteredTitles" stripe style="width: 100%" max-height="600">
        <el-table-column prop="label" label="岗位名称">
          <template #default="{ row }">
            {{ row }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewProfile(row)">
              查看画像
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 画像详情弹窗 -->
    <el-dialog v-model="dialogVisible" :title="selectedProfile?.job_title || '岗位画像'" width="700px" v-loading="loadingProfile">
      <div v-if="selectedProfile" class="profile-detail">
        <!-- 技能要求 -->
        <div class="section">
          <h4>技能要求</h4>
          <div class="tag-wrap">
            <span v-for="skill in (typeof selectedProfile.skills === 'string' ? JSON.parse(selectedProfile.skills) : selectedProfile.skills)" :key="skill" class="soft-tag blue">{{ skill }}</span>
          </div>
        </div>

        <!-- 证书要求 -->
        <div class="section">
          <h4>证书要求</h4>
          <div class="tag-wrap">
            <span v-for="cert in (typeof selectedProfile.certificates === 'string' ? JSON.parse(selectedProfile.certificates) : selectedProfile.certificates)" :key="cert" class="soft-tag yellow">{{ cert }}</span>
          </div>
        </div>

        <!-- 能力评分 -->
        <div class="section">
          <h4>能力评分</h4>
          <div class="score-grid">
            <div class="score-item">创新：{{ selectedProfile.innovation_score }}分</div>
            <div class="score-item">学习：{{ selectedProfile.learning_score }}分</div>
            <div class="score-item">抗压：{{ selectedProfile.stress_score }}分</div>
            <div class="score-item">沟通：{{ selectedProfile.communication_score }}分</div>
          </div>
        </div>

        <!-- 能力说明 -->
        <div class="section">
          <h4>能力说明</h4>
          <p><strong>创新能力说明：</strong>{{ selectedProfile.innovation_reason || '无' }}</p>
          <p><strong>学习能力说明：</strong>{{ selectedProfile.learning_reason || '无' }}</p>
          <p><strong>抗压能力说明：</strong>{{ selectedProfile.stress_reason || '无' }}</p>
          <p><strong>沟通能力说明：</strong>{{ selectedProfile.communication_reason || '无' }}</p>
        </div>

        <!-- 置信度说明 -->
        <div class="section" v-if="selectedProfile.confidence_reason">
          <h4>置信度说明</h4>
          <p>{{ selectedProfile.confidence_reason }}</p>
        </div>

        <!-- 招聘要求 -->
        <div class="section">
          <h4>招聘要求</h4>
          <p><strong>学历：</strong>{{ selectedProfile.education_required || '无' }}</p>
          <p><strong>专业：</strong>{{ selectedProfile.major_required || '无' }}</p>
          <p><strong>经验：</strong>{{ selectedProfile.experience_required || '无' }}</p>
          <p><strong>语言：</strong>{{ selectedProfile.language_required || '无' }}</p>
          <p><strong>实习要求：</strong>{{ selectedProfile.internship_required }}</p>
          <p v-if="selectedProfile.industry_background"><strong>行业背景：</strong>{{ selectedProfile.industry_background }}</p>
          <p v-if="selectedProfile.other_requirements"><strong>其他要求：</strong>{{ selectedProfile.other_requirements }}</p>
        </div>

        <!-- 新增：区域机会分析 -->
        <div class="section" v-if="selectedProfile.region_stats && selectedProfile.region_stats.length">
          <h4>区域机会分析</h4>
          <el-table :data="selectedProfile.region_stats" border size="small" style="width: 100%">
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
/* 保留原有样式，添加弹窗内表格样式 */
.profiles-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.page-subtitle {
  margin: -6px 0 0;
  font-size: 14px;
  color: var(--text-secondary);
}
.filter-row {
  display: flex;
  gap: 16px;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}
.search-input {
  width: 260px;
}
.tag-filter {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.tag-btn {
  border: none;
  background: #f5f8fd;
  color: var(--text-regular);
  padding: 9px 14px;
  border-radius: 999px;
  cursor: pointer;
}
.tag-btn.active {
  background: var(--primary-color-light);
  color: #4f7fdc;
  font-weight: 600;
}
.panel-card {
  margin-bottom: 20px;
}
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
.tag-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}
.soft-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 24px;
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