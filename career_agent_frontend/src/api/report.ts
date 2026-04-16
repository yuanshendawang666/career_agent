// src/api/report.ts
import request from '../utils/request';

export interface ReportRequest {
  student_id: number;
  job_title: string;
}

export interface ReportResponse {
  report_url: string;
  message: string;
}

export interface ExportRequest {
  report_data: Record<string, any>;
}

export interface PolishRequest {
  text: string;
  instruction?: string | null;
}

// 一键生成报告（求职主线）
export const generateReport = (data: ReportRequest) => {
  return request.post<ReportResponse>('/api/v1/report/generate', data);
};

// 预览报告数据（供前端编辑）
export const previewReport = (data: ReportRequest) => {
  return request.post<Record<string, any>>('/api/v1/report/preview', data);
};

// 导出编辑后的报告（返回文件 Blob）
export const exportReport = (data: ExportRequest) => {
  return request.post('/api/v1/report/export', data, {
    responseType: 'blob',
  });
};

// 润色文本
export const polishText = (data: PolishRequest) => {
  return request.post<{ polished_text: string }>('/api/v1/report/polish', data);
};

// 获取当前用户的历史报告列表
export const getReportHistory = () => {
  return request.get<Array<{ filename: string; created_at: string; job_title: string; url: string }>>(
    '/api/v1/report/history'
  );
};

export const downloadReport = (filename: string) => {
  // 注意：该接口需要认证，但直接通过 URL 访问时，浏览器会自动携带 Cookie 或需要手动加 token
  // 最简单的方式是直接用 window.open 或 a 标签，因为 token 已经在请求拦截器中自动添加
  return request.get(`/api/v1/report/files/${filename}`, {
    responseType: 'blob',
  });
};

export const getReportData = (student_id: number, job_title: string) => {
  return previewReport({ student_id, job_title })
}