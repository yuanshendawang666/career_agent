// src/api/jobs.ts
import request from '../utils/request';

export interface JobResponse {
  id: number;
  job_title: string;
  company_name: string;
  location?: string | null;
  salary_range?: string | null;
}

export interface RegionStatsResponse {
  region: string;
  demand_count: number;
  salary_min_avg: number;
  salary_max_avg: number;
  top_cities: string[];
}

export interface JobTitleProfileResponse {
  job_title: string;
  skills: string[];
  certificates: string[];
  innovation_score: number;
  innovation_reason: string;
  learning_score: number;
  learning_reason: string;
  stress_score: number;
  stress_reason: string;
  communication_score: number;
  communication_reason: string;
  internship_required: string;
  education_required?: string | null;
  major_required?: string | null;
  experience_required?: string | null;
  language_required?: string | null;
  industry_background?: string | null;
  other_requirements?: string | null;
  region_stats?: RegionStatsResponse[];
}

export const getJobs = () => {
  return request.get<JobResponse[]>('/api/v1/jobs/');
};

export const getJobProfile = (jobTitle: string) => {
  // 双重编码：先将斜杠替换为 %2F，再整体编码
  const encoded = encodeURIComponent(jobTitle.replace(/\//g, '%2F'))
  return request.get(`/api/v1/jobs/${encoded}/profile`)
}
