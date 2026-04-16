// src/api/match.ts
import request from '../utils/request';

export interface MatchResult {
  job_id: number;
  job_title: string;
  total_score: number;
  details: Record<string, number>;
}

// 获取学生与所有岗位的匹配度
export const matchStudent = (studentId: number) => {
  return request.get<MatchResult[]>(`/api/v1/match/student/${studentId}`);
};