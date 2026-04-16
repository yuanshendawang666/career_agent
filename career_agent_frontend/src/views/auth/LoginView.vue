<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { resetPasswordApi } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const forgotPasswordVisible = ref(false)
const resetLoading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const resetForm = reactive({
  email: '',
  new_password: '',
  confirm_password: ''
})

const handleLogin = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  try {
    loading.value = true
    const success = await userStore.doLogin({
      username: form.username,
      password: form.password
    })
    if (success) {
      router.push('/')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('登录失败，请检查网络或后端服务')
  } finally {
    loading.value = false
  }
}

const handleResetPassword = async () => {
  console.log('重置密码函数被触发')
  if (resetForm.new_password !== resetForm.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  if (resetForm.new_password !== resetForm.confirm_password) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  resetLoading.value = true
  try {
    await resetPasswordApi({ email: resetForm.email, new_password: resetForm.new_password })
    ElMessage.success('密码重置成功，请使用新密码登录')
    forgotPasswordVisible.value = false
    resetForm.email = ''
    resetForm.new_password = ''
    resetForm.confirm_password = ''
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '重置失败')
  } finally {
    resetLoading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-wrap">
      <div class="intro">
        <div class="badge">「智途」— 你的私人职业规划助手</div>
        <h1>登录系统</h1>
        <p>
          进入职业规划与岗位匹配平台，
          开始你的成长路径探索或求职准备。
        </p>
      </div>

      <el-card class="auth-card">
        <h2>欢迎回来</h2>
        <p class="sub-text">请输入你的账号信息</p>

        <el-form label-position="top">
          <el-form-item label="用户名">
            <el-input v-model="form.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
          </el-form-item>
          <el-button type="primary" style="width: 100%" :loading="loading" @click="handleLogin">
            登录
          </el-button>
          <div class="bottom-text">
            还没有账号？<router-link to="/register">去注册</router-link>
            <el-button link type="primary" class="forgot-link" style="display: inline-block; text-align: center;" @click="forgotPasswordVisible = true">忘记密码？</el-button>
          </div>
        </el-form>
      </el-card>
    </div>

    <el-dialog v-model="forgotPasswordVisible" title="重置密码" width="400px">
      <el-form :model="resetForm" label-position="top">
        <el-form-item label="注册邮箱">
          <el-input v-model="resetForm.email" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="resetForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="resetForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="forgotPasswordVisible = false">取消</el-button>
        <el-button type="primary" @click="handleResetPassword" :loading="resetLoading">重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
/* 保持原有样式不变 */
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
  display: flex;
  justify-content: center;
  gap: 16px;
  align-items: center;
}
.bottom-text a {
  color: #5a84db;
  margin-left: 4px;
}

.forgot-link {
  color: #ffffff !important;
}
</style>
