"""
Pydantic 报告相关数据模型（Schemas）

定义匹配结果、报告生成请求/响应、报告预览、文本润色及报告导出等接口的数据结构。
"""
from typing import Dict, Any, List, Optional

from pydantic import BaseModel


class MatchResult(BaseModel):
    """
    单个岗位与学生匹配结果的响应模型。

    用于返回匹配接口中每个岗位的匹配详情，包含岗位基本信息、综合得分及各维度得分。
    """

    job_id: int
    """岗位 ID"""
    job_title: str
    """岗位名称"""
    total_score: float
    """综合匹配得分，通常是各维度得分的加权和，取值范围 0~1 或 0~100"""
    details: Dict[str, float]
    """各维度的详细得分，如 {"skills": 0.85, "education": 0.90, "experience": 0.75}"""


class ReportRequest(BaseModel):
    """
    报告生成请求模型。

    包含学生 ID 和岗位名称，用于指定生成哪份报告。
    """

    student_id: int
    """学生唯一标识 ID"""
    job_title: str
    """岗位名称"""


class ReportResponse(BaseModel):
    """
    报告生成成功响应模型。

    返回报告文件的下载链接及操作状态信息。
    """

    report_url: str
    """报告文件的下载 URL，如 "/api/v1/report/files/report_xxx.docx" """
    message: str
    """操作结果提示信息，如 "报告生成成功" """


class ReportPreviewRequest(BaseModel):
    """
    报告预览请求模型。

    用于获取报告的结构化数据，供前端编辑。
    """

    student_id: int
    """学生唯一标识 ID"""
    job_title: str
    """岗位名称"""


class PolishRequest(BaseModel):
    """
    文本润色请求模型。

    用于请求对报告中的某段文本进行语言优化，可指定润色方向或风格。
    """

    text: str
    """待润色的原始文本"""
    instruction: Optional[str] = None
    """润色指导或风格要求，如 "更正式"、"更简洁"、"保留原意但提升专业性" 等，可选"""


class ExportRequest(BaseModel):
    """
    报告导出请求模型。

    接收前端编辑后的完整报告数据，用于生成最终的 Word 文档。
    """

    report_data: Dict[str, Any]
    """报告结构化数据，格式与预览接口返回的数据一致"""

class PathReportRequest(BaseModel):
    student: dict          # 学生信息（包含 id, name, major, grade, intended_city, skills, certificates, overall_score, overall_reason 等）
    path_name: str
    match_score: Optional[int] = None
    advice: Optional[str] = None
    alternative_path: Optional[str] = None
    development_plan: str