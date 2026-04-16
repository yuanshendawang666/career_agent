<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { registerApi } from '@/api/auth'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  role: 'student',
  studentId: undefined as number | undefined
})

const handleRegister = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  if (form.password !== form.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    const res = await registerApi({
      username: form.username,
      email: form.email,
      password: form.password,
      role: form.role,
      studentId: form.studentId
    })
    if (res.success && res.token) {
      localStorage.setItem('token', res.token)
      if (res.user?.studentId) {
        localStorage.setItem('student_id', String(res.user.studentId))
      }
      ElMessage.success('注册成功')
      router.push('/')
    } else {
      ElMessage.error(res.message || '注册失败')
    }
  } catch (error) {
    ElMessage.error('注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-wrap">
      <div class="intro">
        <div class="badge">「智途」— 你的私人职业规划助手</div>
        <h1>创建账号</h1>
        <p>
          注册后，你可以选择职业规划路径模式，
          也可以进入岗位匹配模式，生成属于你的成长与求职方案。
        </p>
      </div>

      <el-card class="auth-card">
        <h2>注册账号</h2>
        <p class="sub-text">开始使用你的职业规划平台</p>

        <el-form label-position="top">
          <el-form-item label="用户名">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
            />
          </el-form-item>

          <el-form-item label="邮箱">
            <el-input
              v-model="form.email"
              placeholder="请输入邮箱"
            />
          </el-form-item>

          <el-form-item label="密码">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              placeholder="请输入密码"
            />
          </el-form-item>

          <el-form-item label="确认密码">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              show-password
              placeholder="请再次输入密码"
            />
          </el-form-item>

          <el-button
            type="primary"
            style="width: 100%"
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </el-button>

          <div class="bottom-text">
            已有账号？
            <router-link to="/login">去登录</router-link>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<style scoped lang="scss">
.auth-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, #eef6ff 0%, transparent 30%),
    radial-gradient(circle at bottom right, #fff7d6 0%, transparent 28%),
    var(--bg-page);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.auth-wrap {
  width: 100%;
  max-width: 1080px;
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 28px;
  align-items: center;
}

.intro {
  padding: 20px;
}

.badge {
  display: inline-block;
  padding: 8px 14px;
  background: #ffffff;
  color: #6e8fd8;
  border-radius: 999px;
  font-size: 13px;
  margin-bottom: 18px;
  border: 1px solid var(--border-color);
}

.intro h1 {
  margin: 0 0 14px;
  font-size: 38px;
  line-height: 1.25;
  color: var(--text-primary);
}

.intro p {
  margin: 0;
  font-size: 15px;
  line-height: 1.9;
  color: var(--text-regular);
  max-width: 560px;
}

.auth-card {
  padding: 10px;
}

.auth-card h2 {
  margin: 0 0 8px;
  font-size: 26px;
  color: var(--text-primary);
}

.sub-text {
  margin: 0 0 18px;
  color: var(--text-secondary);
  font-size: 14px;
}

.bottom-text {
  margin-top: 16px;
  text-align: center;
  color: var(--text-regular);
  font-size: 14px;
}

.bottom-text a {
  color: #5a84db;
  margin-left: 4px;
}
</style>