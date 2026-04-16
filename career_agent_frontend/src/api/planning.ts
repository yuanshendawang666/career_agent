// src/api/planning.ts
import request from '../utils/request';

export interface PathReportRequest {
  student: Record<string, any>;   // 学生完整画像对象
  path_name: string;
  match_score?: number | null;
  advice?: string | null;
  alternative_path?: string | null;
  development_plan: string;
}

export interface ReportResponse {
  report_url: string;
  message: string;
}

// 生成规划报告（探索主线）
export const generatePathReport = (data: PathReportRequest) => {
  return request.post<ReportResponse>('/api/v1/report/generate_path_report', data);
};

export const getPlanningProfile = () => {
  return request.get('/api/v1/planning/profile')
}

export const updatePlanningProfile = (data: any) => {
  return request.put('/api/v1/planning/profile', data)
}

export const getLearningResource = (pathName: string) => {
  return request.get('/api/v1/planning/get-learning-resource', { params: { path_name: pathName } })
}

export const saveLearningResource = (data: { path_name: string; content: string }) => {
  return request.post('/api/v1/planning/save-learning-resource', data)
}