// src/api/graph.ts
import request from '../utils/request';

export const getGraph = (jobName: string) => {
  // 双重编码：先将斜杠替换为 %2F，再整体编码
  const encoded = encodeURIComponent(jobName.replace(/\//g, '%2F'))
  return request.get(`/api/v1/graph/${encoded}`)
}