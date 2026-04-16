"""
职业发展路径图 API 路由模块

提供根据岗位名称获取职业发展路径的接口。
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from app.services.graph import get_job_paths
from urllib.parse import unquote

router = APIRouter()

@router.get("/{job_name}", response_model=List[Dict[str, Any]])
def get_graph(job_name: str):
    job_name = unquote(job_name)
    """
    获取指定岗位的职业发展路径图数据，返回节点和关系列表。
    """
    try:
        paths = get_job_paths(job_name)
        nodes = set()
        edges = []

        nodes.add(job_name)
        for target in paths.get("promotions", []):
            nodes.add(target)
            edges.append({"source": job_name, "target": target, "label": "晋升"})
        for target in paths.get("transfers", []):
            nodes.add(target)
            edges.append({"source": job_name, "target": target, "label": "转岗"})

        elements = []
        for node in nodes:
            elements.append({"data": {"id": node, "label": node}})
        for edge in edges:
            elements.append({"data": {"source": edge["source"], "target": edge["target"], "label": edge["label"]}})
        return elements
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))