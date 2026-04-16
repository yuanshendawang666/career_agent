"""
职业发展路径图服务模块

提供 Neo4j 图数据库操作，包括岗位节点创建、关系建立、路径查询和清空功能。
"""
import logging
from typing import Optional, Dict, List, Any

from app.database.neo4j import neo4j_driver

logger = logging.getLogger(__name__)


def create_job_node(job_name: str, job_id: Optional[int] = None) -> Optional[Any]:
    """
    在 Neo4j 中创建岗位节点（如果节点已存在则合并，不会重复创建）。

    Args:
        job_name (str): 岗位名称，作为节点的唯一标识（name 属性）。
        job_id (Optional[int]): 关联的 MySQL 中的岗位 ID，仅在创建时设置。

    Returns:
        Optional[Any]: 包含创建或匹配到的节点信息的 Record 对象，若无则返回 None。
    """
    with neo4j_driver.session() as session:
        # 使用 MERGE 确保节点唯一性
        # 如果节点不存在则创建，并设置 job_id；如果已存在则忽略创建部分
        result = session.run(
            "MERGE (j:Job {name: $name}) "
            "ON CREATE SET j.job_id = $job_id "
            "RETURN j",
            name=job_name,
            job_id=job_id,
        )
        return result.single()


def create_relationship(from_job: str, to_job: str, rel_type: str) -> None:
    """
    在两个岗位节点之间创建关系。

    Args:
        from_job (str): 源岗位名称（起点节点）。
        to_job (str): 目标岗位名称（终点节点）。
        rel_type (str): 关系类型，通常为 "PROMOTES_TO"（晋升）或 "TRANSFERS_TO"（转岗）。
    """
    with neo4j_driver.session() as session:
        # 确保源节点和目标节点存在（使用 MERGE）
        # 使用字典传递参数，避免与关键字 from、to 冲突
        session.run("MERGE (a:Job {name: $from})", {"from": from_job})
        session.run("MERGE (b:Job {name: $to})", {"to": to_job})

        # 创建关系，使用 MERGE 避免重复创建
        session.run(
            f"MATCH (a:Job {{name: $from}}) MATCH (b:Job {{name: $to}}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            f"RETURN r",
            {"from": from_job, "to": to_job},
        )


def get_job_paths(job_name: str) -> Dict[str, Any]:
    """
    获取指定岗位的职业发展路径，包括晋升路径和转岗路径。

    Args:
        job_name (str): 岗位名称。

    Returns:
        Dict[str, Any]: 包含岗位名称、晋升目标列表和转岗目标列表的字典。
              格式: {"job_name": str, "promotions": List[str], "transfers": List[str]}
    """
    with neo4j_driver.session() as session:
        # 查询晋升路径：从当前岗位出发，通过 PROMOTES_TO 关系连接的目标岗位
        promo_result = session.run(
            "MATCH (j:Job {name: $name})-[:PROMOTES_TO]->(target) "
            "RETURN target.name as target",
            name=job_name,
        )
        promotions = [record["target"] for record in promo_result]
        promotions.reverse()
        # 查询转岗路径：从当前岗位出发，通过 TRANSFERS_TO 关系连接的目标岗位
        trans_result = session.run(
            "MATCH (j:Job {name: $name})-[:TRANSFERS_TO]->(target) "
            "RETURN target.name as target",
            name=job_name,
        )
        transfers = [record["target"] for record in trans_result]

        return {
            "job_name": job_name,
            "promotions": promotions,
            "transfers": transfers,
        }


def clear_graph() -> None:
    """
    清空 Neo4j 数据库中的所有节点和关系（用于测试环境）。

    警告：此操作会删除所有数据，不可逆，请勿在生产环境中调用。
    """
    with neo4j_driver.session() as session:
        # DETACH DELETE 会删除节点及其所有关系
        session.run("MATCH (n) DETACH DELETE n")