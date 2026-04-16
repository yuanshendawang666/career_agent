"""
Pydantic 岗位相关数据模型（Schemas）

定义岗位基础信息、具体岗位画像、岗位名称典型画像及区域统计数据的请求/响应模型。
"""
import json
from typing import List, Optional

from pydantic import BaseModel, validator


# ================== 岗位基础信息 ==================

class JobBase(BaseModel):
    """
    岗位基本信息模型，用于请求或响应的基础字段。

    包含岗位名称、公司名称、工作地点和薪资范围。
    """

    job_title: str
    """岗位名称"""
    company_name: str
    """公司名称"""
    location: Optional[str] = None
    """工作地点，可选"""
    salary_range: Optional[str] = None
    """薪资范围，如 "15k-25k"，可选"""


class JobResponse(JobBase):
    """
    岗位列表查询响应模型，继承自 JobBase，额外包含 id 字段。
    """

    id: int
    """岗位唯一标识 ID"""


# ================== 区域统计信息 ==================

class RegionStatsResponse(BaseModel):
    """
    岗位区域统计数据响应模型，用于返回某个岗位在特定地区的统计信息。
    """

    region: str
    """地区名称，如 "华东"、"北京" """
    demand_count: int
    """该地区岗位需求数量"""
    salary_min_avg: float
    """平均最低薪资（万元/年）"""
    salary_max_avg: float
    """平均最高薪资（万元/年）"""
    top_cities: List[str]
    """主要城市列表"""

    class Config:
        from_attributes = True  # 允许从 SQLAlchemy 模型实例创建 Pydantic 对象


# ================== 具体岗位画像（关联 job_id） ==================

class JobProfileResponse(BaseModel):
    """
    具体岗位画像响应模型，对应数据库表 job_profiles。

    用于返回某个具体岗位（由 job_id 标识）的详细画像数据，
    包含技能、证书、五大能力评分及招聘要求。
    """

    job_id: int
    """关联的岗位 ID"""
    job_title: Optional[str] = None
    """岗位名称，便于前端展示"""
    company_name: Optional[str] = None
    """公司名称，便于前端展示"""

    # 技能与证书
    skills: List[str]
    """所需技能列表"""
    certificates: List[str]
    """所需证书列表"""

    # 五大能力维度评分及理由
    innovation_score: float
    """创新能力得分"""
    innovation_reason: str
    """创新能力评分依据"""
    learning_score: float
    """学习能力得分"""
    learning_reason: str
    """学习能力评分依据"""
    stress_score: float
    """抗压能力得分"""
    stress_reason: str
    """抗压能力评分依据"""
    communication_score: float
    """沟通能力得分"""
    communication_reason: str
    """沟通能力评分依据"""

    # 招聘要求
    internship_required: str
    """实习经历要求"""
    education_required: Optional[str] = None
    """学历要求，如 "本科及以上" """
    major_required: Optional[str] = None
    """专业要求"""
    experience_required: Optional[str] = None
    """工作经验要求，如 "3年以上" """
    language_required: Optional[str] = None
    """语言能力要求，如 "英语六级" """
    industry_background: Optional[str] = None
    """行业背景要求"""
    other_requirements: Optional[str] = None
    """其他要求"""

    @validator("skills", "certificates", pre=True)
    def parse_json_string(cls, v):
        """
        验证器：将数据库中存储的 JSON 字符串（如 '["Python","SQL"]'）自动解析为 Python 列表。
        如果输入已经是列表，则直接返回；如果字符串解析失败，返回空列表。
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []  # 解析失败返回空列表
        return v

    class Config:
        from_attributes = True  # 允许从 SQLAlchemy 模型实例创建 Pydantic 对象


# ================== 岗位名称典型画像（按 job_title 聚合） ==================

class JobTitleProfileResponse(BaseModel):
    """
    岗位名称典型画像响应模型，对应数据库表 job_title_profiles。

    按岗位名称聚合的典型画像，用于学生与岗位的快速匹配。
    包含技能、证书、五大能力评分、招聘要求以及区域统计数据。
    """

    job_title: str
    """岗位名称"""
    skills: List[str]
    """所需技能列表"""
    certificates: List[str]
    """所需证书列表"""
    innovation_score: float
    """创新能力得分"""
    innovation_reason: str
    """创新能力评分依据"""
    learning_score: float
    """学习能力得分"""
    learning_reason: str
    """学习能力评分依据"""
    stress_score: float
    """抗压能力得分"""
    stress_reason: str
    """抗压能力评分依据"""
    communication_score: float
    """沟通能力得分"""
    communication_reason: str
    """沟通能力评分依据"""
    internship_required: str
    """实习经历要求"""
    education_required: Optional[str] = None
    """学历要求"""
    major_required: Optional[str] = None
    """专业要求"""
    experience_required: Optional[str] = None
    """工作经验要求"""
    language_required: Optional[str] = None
    """语言能力要求"""
    industry_background: Optional[str] = None
    """行业背景要求"""
    other_requirements: Optional[str] = None
    """其他要求"""
    region_stats: List[RegionStatsResponse] = []
    """岗位在不同地区的统计数据列表，默认为空列表"""

    @validator("skills", "certificates", pre=True)
    def parse_json_string(cls, v):
        """
        验证器：将数据库中存储的 JSON 字符串自动解析为 Python 列表。
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v

    class Config:
        from_attributes = True  # 允许从 SQLAlchemy 模型实例创建 Pydantic 对象