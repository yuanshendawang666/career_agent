<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref('reports')

const reportHistory = ref([
  {
    id: 1,
    title: '职业规划报告 v3',
    time: '今天 14:20',
    desc: '根据最新简历和匹配结果生成的新报告。'
  },
  {
    id: 2,
    title: '岗位匹配分析报告',
    time: '昨天 18:30',
    desc: '基于当前学生画像生成的岗位匹配建议。'
  }
])

const versionHistory = ref([
  {
    id: 101,
    title: '画像版本 v3',
    time: '今天 13:50',
    desc: '补充了项目经历与目标岗位'
  },
  {
    id: 102,
    title: '画像版本 v2',
    time: '3 天前',
    desc: '上传新简历后生成的画像版本'
  }
])
</script>

<template>
  <div class="history-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">历史记录</h2>
        <p class="page-subtitle">分开查看报告历史和学生画像历史版本。</p>
      </div>
    </div>

    <el-card class="panel-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="报告历史" name="reports">
          <div class="history-list">
            <div v-for="item in reportHistory" :key="item.id" class="history-item">
              <div class="history-top">
                <div>
                  <div class="history-title">{{ item.title }}</div>
                  <div class="history-time">{{ item.time }}</div>
                </div>
                <el-button size="small">下载</el-button>
              </div>
              <div class="history-desc">{{ item.desc }}</div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="画像版本" name="versions">
          <div class="history-list">
            <div v-for="item in versionHistory" :key="item.id" class="history-item">
              <div class="history-top">
                <div>
                  <div class="history-title">{{ item.title }}</div>
                  <div class="history-time">{{ item.time }}</div>
                </div>
                <el-button size="small">查看版本</el-button>
              </div>
              <div class="history-desc">{{ item.desc }}</div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.history-page { display: flex; flex-direction: column; gap: 20px; }
.page-subtitle { margin: -6px 0 0; font-size: 14px; color: var(--text-secondary); }
.history-list { display: flex; flex-direction: column; gap: 14px; }
.history-item { background: #fafcff; padding: 16px; border-radius: 16px; }
.history-top { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.history-title { font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px; }
.history-time { font-size: 12px; color: var(--text-secondary); }
.history-desc { margin-top: 10px; font-size: 14px; line-height: 1.8; color: var(--text-regular); }
</style>