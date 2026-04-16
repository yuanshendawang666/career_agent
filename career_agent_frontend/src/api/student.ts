// src/api/student.ts
import request from '../utils/request'

// 类型定义（如果已在 types/api.ts 中定义，可导入）
export interface StudentResponse {
  id: number
  name: string
  profile_json: Record<string, any> | null
}

export interface ResumeVersionResponse {
  id: number
  version: number
  created_at: string
}

export interface ResumeVersionDetail extends ResumeVersionResponse {
  resume_text: string
  profile_json: Record<string, any>
}

export interface StudentProfileUpdateRequest {
  manual_basics?: {
    intended_city?: string | null;
    gender?: string | null;
    school?: string | null;
    grade?: string | null;
  } | null;
  experiences?: {
    projects?: Array<{ name: string; role?: string; description?: string; technologies?: string[] }> | null;
    papers?: Array<{ name: string; role?: string; description?: string; technologies?: string[] }> | null;
    internships?: Array<{ name: string; role?: string; description?: string; technologies?: string[] }> | null;
    competitions?: Array<{ name: string; role?: string; description?: string; technologies?: string[] }> | null;
  } | null;
  skills?: string[] | null;
  certificates?: string[] | null;
  education?: string | null;
  major?: string | null;
  // 以下为新增字段，与后端 StudentProfileUpdateRequest 保持一致
  age?: string | null;
  phone?: string | null;
  email?: string | null;
  graduation_year?: string | null;
  target_job?: string | null;
  self_introduction?: string | null;
  interests?: string[] | null;
  strengths?: string[] | null;
}

export interface FreeTextParseRequest {
  text: string
  type: string
}

// 上传简历
export const uploadResume = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<StudentResponse>('/api/v1/students/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取学生信息
export const getStudent = (studentId: number) => {
  return request.get<StudentResponse>(`/api/v1/students/${studentId}`)
}

// 更新学生画像
export const updateStudentProfile = (studentId: number, data: StudentProfileUpdateRequest) => {
  return request.put<StudentResponse>(`/api/v1/students/${studentId}/profile`, data)
}

// 确认生成完整画像
export const finalizeStudent = (studentId: number) => {
  return request.post<StudentResponse>(`/api/v1/students/${studentId}/finalize`)
}

// 获取简历版本列表
export const getResumeVersions = (studentId: number) => {
  return request.get<ResumeVersionResponse[]>(`/api/v1/students/${studentId}/versions`)
}

// 获取指定版本详情
export const getResumeVersion = (studentId: number, versionId: number) => {
  return request.get<ResumeVersionDetail>(`/api/v1/students/${studentId}/versions/${versionId}`)
}

// 解析自由文本
export const parseText = (data: FreeTextParseRequest) => {
  return request.post<any>('/api/v1/students/parse-text', data)
}