import request from '../utils/request'

export const getJobs = () => {
  return request.get('/api/v1/jobs/')
}

export const getJobProfile = (jobTitle: string) => {
  return request.get(`/api/v1/jobs/${encodeURIComponent(jobTitle)}/profile`)
}