<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import cytoscape from 'cytoscape'
import dagre from 'cytoscape-dagre'
import { getGraph } from '@/api/graph'
import { getJobs } from '@/api/jobs'  // 新增：获取岗位列表

cytoscape.use(dagre)

const loading = ref(false)
const jobName = ref('')
const containerRef = ref<HTMLElement | null>(null)
let cy: any = null

// 搜索建议相关
const allJobTitles = ref<string[]>([])      // 所有岗位名称列表
const searchOptions = ref<string[]>([])     // 模糊匹配后的选项
const searchLoading = ref(false)

// 加载所有岗位名称（用于搜索建议）
const loadJobTitles = async () => {
  searchLoading.value = true
  try {
    const jobs = await getJobs()
    // 去重
    const unique = [...new Set(jobs.map((job: any) => job.job_title))]
    allJobTitles.value = unique
  } catch (error) {
    console.error('加载岗位列表失败', error)
  } finally {
    searchLoading.value = false
  }
}

// 模糊匹配搜索
const handleSearch = (query: string) => {
  if (!query) {
    searchOptions.value = []
    return
  }
  const lowerQuery = query.toLowerCase()
  const matches = allJobTitles.value.filter(title =>
    title.toLowerCase().includes(lowerQuery)
  )
  // 取前 10 条
  searchOptions.value = matches.slice(0, 10)
}

// 选择岗位后加载图谱
const handleSelect = (value: string) => {
  jobName.value = value
  loadGraph()
}

// 加载图谱数据
const loadGraph = async () => {
  if (!jobName.value.trim()) {
    ElMessage.warning('请输入岗位名称')
    return
  }
  loading.value = true
  try {
    const elements = await getGraph(jobName.value)
    if (!elements || elements.length === 0) {
      ElMessage.info('未找到该岗位的图谱数据')
      return
    }
    await nextTick()
    renderGraph(elements)
  } catch (error: any) {
    ElMessage.error(error.message || '加载图谱失败')
  } finally {
    loading.value = false
  }
}

// 渲染图谱（使用圆形节点和力导向布局）
const renderGraph = (elements: any[]) => {
  if (cy) cy.destroy()
  cy = cytoscape({
    container: containerRef.value,
    elements: elements,
    style: [
      {
        selector: 'node',
        style: {
          'label': 'data(label)',
          'background-color': '#4a90e2',
          'color': '#fff',
          'font-size': '12px',
          'width': '80px',
          'height': '80px',
          'shape': 'ellipse',
          'text-valign': 'center',
          'text-halign': 'center',
          'border-width': 2,
          'border-color': '#2c5f8a',
          'shadow-blur': 6,
          'shadow-color': '#000',
          'shadow-opacity': 0.3
        }
      },
      {
        selector: 'edge[label="晋升"]',
        style: {
          'width': 3,
          'line-color': '#4caf50',
          'target-arrow-color': '#4caf50',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'label': 'data(label)',
          'font-size': '10px',
          'text-rotation': 'autorotate',
          'arrow-scale': 1.5
        }
      },
      {
        selector: 'edge[label="转岗"]',
        style: {
          'width': 2,
          'line-color': '#ff9800',
          'target-arrow-color': '#ff9800',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'line-style': 'dashed',
          'label': 'data(label)',
          'font-size': '10px',
          'text-rotation': 'autorotate',
          'arrow-scale': 1.2
        }
      },
      {
        selector: 'edge',
        style: {
          'width': 2,
          'line-color': '#aaa',
          'target-arrow-color': '#aaa',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'label': 'data(label)',
          'font-size': '10px',
          'text-rotation': 'autorotate'
        }
      }
    ],
    layout: {
      name: 'cose',
      animate: true,
      nodeRepulsion: 10000,
      idealEdgeLength: 100,
      gravity: 0.25,
      numIter: 1000
    }
  })
  cy.fit(50)
}

// 重置
const reset = () => {
  jobName.value = ''
  if (cy) {
    cy.destroy()
    cy = null
  }
  searchOptions.value = []
}

onMounted(() => {
  loadJobTitles()
})

onUnmounted(() => {
  if (cy) cy.destroy()
})
</script>

<template>
  <div class="graph-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">岗位图谱</h2>
        <p class="page-subtitle">查看岗位的晋升路径和横向换岗方向，可视化职业发展脉络。</p>
      </div>
    </div>

    <el-card class="control-card">
      <el-row :gutter="16" align="middle">
        <el-col :span="12">
          <!-- 搜索框：自动补全，模糊匹配，显示前10条 -->
          <el-autocomplete
            v-model="jobName"
            :fetch-suggestions="(query, cb) => {
              handleSearch(query)
              cb(searchOptions.map(s => ({ value: s })))
            }"
            placeholder="输入岗位名称（模糊匹配）"
            clearable
            :trigger-on-focus="false"
            @select="(item) => handleSelect(item.value)"
            @keyup.enter="loadGraph"
            :loading="searchLoading"
          />
        </el-col>
        <el-col :span="6">
          <el-button type="primary" :loading="loading" @click="loadGraph">查询图谱</el-button>
        </el-col>
        <el-col :span="6">
          <el-button @click="reset">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="graph-card">
      <div ref="containerRef" class="graph-container"></div>
    </el-card>

    <el-card class="panel-card">
      <template #header>
        <div class="panel-title">图谱说明</div>
      </template>
      <div class="desc-box">
        岗位图谱展示了不同岗位之间的晋升关系（箭头方向）和横向转换关系。
        你可以结合岗位画像与自身能力情况，判断当前更适合从哪个岗位切入，以及未来可以如何发展。
      </div>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.graph-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
  min-height: 100vh;  // 确保页面内容撑开，但背景由 body 提供
}

.page-subtitle {
  margin: -6px 0 0;
  font-size: 14px;
  color: var(--text-secondary);
}
.control-card,
.graph-card,
.panel-card {
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(2px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s;
  &:hover {
    background: rgba(255, 255, 255, 0.95);
  }
}

.graph-container {
  width: 100%;
  height: 70vh;
  min-height: 500px;
  background: #fafcff;
  border-radius: 12px;
  position: relative;
  overflow: hidden;
  contain: layout size;
}
.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}
.desc-box {
  padding: 18px;
  border-radius: 16px;
  background: #fafcff;
  line-height: 1.9;
  color: var(--text-regular);
  font-size: 14px;
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