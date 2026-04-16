"""
Neo4j 图数据库连接模块

封装 Neo4j 驱动，提供数据库连接管理和会话创建功能。
"""
from neo4j import GraphDatabase, Session

from app.core.config import settings


class Neo4jDriver:
    """
    Neo4j 图数据库驱动封装类。

    负责管理数据库连接生命周期，提供会话创建方法。
    全局单例通过 neo4j_driver 实例暴露。
    """

    def __init__(self) -> None:
        """
        初始化 Neo4j 驱动，建立连接。

        从配置中读取 URI、用户名和密码，创建驱动实例。
        """
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,  # Neo4j 连接地址（如 bolt://localhost:7687）
            auth=(settings.neo4j_user, settings.neo4j_password),  # 认证信息
        )

    def close(self) -> None:
        """
        关闭驱动，释放所有连接资源。

        应在应用退出时调用，避免连接泄漏。
        """
        self.driver.close()

    def session(self) -> Session:
        """
        创建一个新的数据库会话。

        Returns:
            Session: 用于执行 Cypher 查询的会话对象。
        """
        return self.driver.session()


# 全局单例实例，供整个应用使用
neo4j_driver = Neo4jDriver()