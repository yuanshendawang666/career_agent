// src/stores/user.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { loginApi, registerApi } from '@/api/auth';
import type { UserLoginRequest, UserRegisterRequest, UserResponse } from '@/types/api';
import { ElMessage } from 'element-plus';

const TOKEN_KEY = 'token';
const USER_KEY = 'user';

export const useUserStore = defineStore('user', () => {
  // 从 localStorage 读取初始值
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY));
  const savedUser = localStorage.getItem(USER_KEY);
  const user = ref<UserResponse | null>(savedUser ? JSON.parse(savedUser) : null);

  // 辅助函数：保存 user 到 localStorage
  const persistUser = (userData: UserResponse | null) => {
    if (userData) {
      localStorage.setItem(USER_KEY, JSON.stringify(userData));
    } else {
      localStorage.removeItem(USER_KEY);
    }
  };

  // 登录
  const doLogin = async (data: UserLoginRequest) => {
  try {
    const res = await loginApi(data);
    console.log('登录响应:', res); // 调试：查看后端返回的完整结构

    // 假设后端返回 { success: boolean, message?: string, token?: string, user?: UserResponse }
    if (res.success && res.token) {
      token.value = res.token;
      user.value = res.user;
      localStorage.setItem(TOKEN_KEY, res.token);
      persistUser(res.user);
      if (res.user?.studentId) {
        localStorage.setItem('student_id', String(res.user.studentId));
      }
      ElMessage.success('登录成功');
      return true;
    } else {
      // 确保错误信息有内容
      const errorMsg = res.message || res.msg || '用户名或密码错误，请重试';
      ElMessage.error(errorMsg);
      return false;
    }
  } catch (error: any) {
    console.error('登录请求异常:', error);
    // 处理网络错误或后端抛出的异常（如 axios 拦截器返回的 reject）
    const errorMsg = error?.response?.data?.message || error?.message || '登录请求失败，请检查网络';
    ElMessage.error(errorMsg);
    return false;
  }
};

  // 注册
  const doRegister = async (data: UserRegisterRequest) => {
    try {
      const res = await registerApi(data);
      if (res.success && res.token) {
        token.value = res.token;
        user.value = res.user;
        localStorage.setItem(TOKEN_KEY, res.token);
        persistUser(res.user);
        if (res.user?.studentId) {
          localStorage.setItem('student_id', String(res.user.studentId));
        }
        ElMessage.success('注册成功');
        return true;
      } else {
        ElMessage.error(res.message || '注册失败');
        return false;
      }
    } catch (error) {
      ElMessage.error('注册请求失败');
      return false;
    }
  };

  // 退出登录
  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem('student_id');
    persistUser(null);
    ElMessage.info('已退出登录');
  };

  return { token, user, doLogin, doRegister, logout };
});