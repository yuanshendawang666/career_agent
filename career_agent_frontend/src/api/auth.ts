// src/api/auth.ts
import request from '../utils/request';

export interface LoginParams {
  username: string;
  password: string;
}

export interface RegisterParams {
  username: string;
  email: string;
  password: string;
  role?: string | null;      // 可选，默认 'student'
  studentId?: number | null; // 可选
}

export interface LoginResponse {
  success: boolean;
  user: {
    username: string;
    role: string;
    studentId?: number | null;
  };
  token?: string | null;
  message?: string | null;
}

export const loginApi = (data: LoginParams) => {
  return request.post('/api/v1/auth/login', data);
};

export const registerApi = (data: RegisterParams) => {
  return request.post<LoginResponse>('/api/v1/auth/register', data);
};

export interface ResetPasswordParams {
  email: string;
  new_password: string;
}

export const resetPasswordApi = (data: ResetPasswordParams) => {
  return request.post('/api/v1/auth/reset-password', data);
};