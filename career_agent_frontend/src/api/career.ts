// src/api/career.ts
import request from '../utils/request';

export interface PathSelectRequest {
  student_id: number;
  path_name: string;
}

// 推荐职业路径
export const recommendPaths = (studentId: number) => {
  return request.get<any[]>('/api/v1/career-paths/recommendations', {
    params: { student_id: studentId },
  });
};

// 选择路径并生成发展计划
export const selectPath = (data: PathSelectRequest) => {
  return request.post<any>('/api/v1/career-paths/select', data);
};

// 刷新匹配度，获取备选路径
export const refreshPlan = (studentId: number) => {
  return request.get<any>('/api/v1/career-paths/refresh', {
    params: { student_id: studentId },
  });
};