<template>
  <div class="job-home">
    <section class="hero">
      <div class="hero-left">
        <div class="badge">岗位匹配模式</div>
        <h1>从岗位要求出发，找到更适合你的方向</h1>
        <p>
          这个模式更适合已经准备求职的学生或应届生。
          你可以查看岗位画像、上传简历、分析岗位匹配度，并生成求职报告。
        </p>

        <div class="actions">
          <router-link to="/job/profile">
            <el-button type="primary">我的信息</el-button>
          </router-link>
          <router-link to="/job/position-profiles">
            <el-button>查看岗位画像</el-button>
          </router-link>
        </div>
      </div>

      <el-card class="hero-card">
        <div class="hero-card-title">求职流程建议</div>
        <div class="tip-item">先了解目标岗位画像与要求</div>
        <div class="tip-item">完善信息并上传最新简历</div>
        <div class="tip-item">查看岗位匹配结果与求职报告</div>
      </el-card>
    </section>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="card-label">已收录岗位画像</div>
          <div class="card-value">12</div>
          <div class="card-desc">覆盖典型就业岗位画像与要求</div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="stat-card">
          <div class="card-label">推荐匹配岗位</div>
          <div class="card-value">18</div>
          <div class="card-desc">基于个人画像给出岗位推荐</div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="stat-card">
          <div class="card-label">最新报告状态</div>
          <div class="card-value">可生成</div>
          <div class="card-desc">完成简历上传后可生成求职报告</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <el-col :span="14">
        <el-card class="panel-card">
          <template #header>
            <div class="panel-header">
              <span>快速入口</span>
            </div>
          </template>

          <div class="quick-grid">
            <router-link to="/job/position-profiles" class="quick-card">
              <div class="quick-title">岗位画像库</div>
              <div class="quick-desc">查看岗位要求、技能、学历、证书和能力画像</div>
            </router-link>

            <router-link to="/job/career-graph" class="quick-card">
              <div class="quick-title">岗位图谱</div>
              <div class="quick-desc">查看岗位晋升路径与换岗方向</div>
            </router-link>

            <router-link to="/job/resume" class="quick-card">
              <div class="quick-title">简历上传</div>
              <div class="quick-desc">上传最新简历，生成个人画像</div>
            </router-link>

            <router-link to="/job/match" class="quick-card">
              <div class="quick-title">岗位匹配</div>
              <div class="quick-desc">查看四维度得分与岗位推荐</div>
            </router-link>
          </div>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card class="panel-card">
          <template #header>
            <div class="panel-header">
              <span>本周建议</span>
            </div>
          </template>

          <div class="growth-list">
            <div class="growth-item">
              <div class="index blue">1</div>
              <div>
                <div class="growth-title">先看岗位画像</div>
                <div class="growth-desc">明确岗位需要什么，再决定怎么准备简历和能力。</div>
              </div>
            </div>

            <div class="growth-item">
              <div class="index yellow">2</div>
              <div>
                <div class="growth-title">完善个人信息</div>
                <div class="growth-desc">填写详细的个人资料，帮助系统更精准匹配。</div>
              </div>
            </div>

            <div class="growth-item">
              <div class="index green">3</div>
              <div>
                <div class="growth-title">补足技能差距</div>
                <div class="growth-desc">根据岗位匹配结果，优先提升待补强技能。</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
.job-home {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero {
  display: grid;
  grid-template-columns: 1.4fr 0.9fr;
  gap: 20px;
}

.hero-left {
  background: linear-gradient(135deg, #eef6ff, #fffdf4);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 32px;
}

.badge {
  display: inline-block;
  padding: 8px 14px;
  background: #ffffff;
  color: #6e8fd8;
  border-radius: 999px;
  font-size: 13px;
  margin-bottom: 18px;
}

.hero-left h1 {
  margin: 0 0 14px;
  font-size: 34px;
  line-height: 1.25;
  color: var(--text-primary);
}

.hero-left p {
  margin: 0 0 22px;
  font-size: 15px;
  line-height: 1.9;
  color: var(--text-regular);
  max-width: 620px;
}

.actions {
  display: flex;
  gap: 12px;
}

.hero-card-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 14px;
  color: var(--text-primary);
}

.tip-item {
  padding: 12px 14px;
  background: #f8fbff;
  border-radius: 12px;
  color: var(--text-regular);
  margin-bottom: 10px;
}

.stat-card {
  min-height: 140px;
}

.card-label {
  font-size: 14px;
  color: #8a94a6;
  margin-bottom: 10px;
}

.card-value {
  font-size: 30px;
  font-weight: 700;
  color: #2f3a4a;
  margin-bottom: 10px;
}

.card-desc {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.content-row {
  margin: 0;
}

.panel-card {
  min-height: 300px;
}

.panel-header {
  font-weight: 700;
  color: var(--text-primary);
}

.quick-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.quick-card {
  display: block;
  padding: 16px;
  border-radius: 16px;
  background: #fafcff;
  border: 1px solid #edf2f8;
  transition: 0.2s ease;
}

.quick-card:hover {
  transform: translateY(-2px);
  border-color: #dce8fb;
}

.quick-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.quick-desc {
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-regular);
}

.growth-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.growth-item {
  display: flex;
  gap: 14px;
  padding: 14px;
  border-radius: 14px;
  background: #fafcff;
}

.index {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.index.blue {
  background: #dceeff;
  color: #567fd8;
}

.index.yellow {
  background: #fff4cc;
  color: #a68118;
}

.index.green {
  background: #dff7e8;
  color: #3f9160;
}

.growth-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.growth-desc {
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-regular);
}

@media (max-width: 992px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .quick-grid {
    grid-template-columns: 1fr;
  }
}

:deep(.el-card) {
  background: rgba(255, 255, 255, 0.5) !important;
  backdrop-filter: blur(2px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.95);
  }
}
</style>