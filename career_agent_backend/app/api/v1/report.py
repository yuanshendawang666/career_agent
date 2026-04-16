"""
报告生成 API 路由模块

提供报告预览、润色、导出、历史记录等功能。
支持用户认证，确保用户只能操作自己的报告。
"""
"""
报告生成 API 路由模块

提供报告预览、润色、导出、历史记录等功能。
支持用户认证，确保用户只能操作自己的报告。
"""
import os
import glob
from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.mysql import get_db                     # 修正导入
from app.dependencies import get_current_user             # 修正导入
from app.core.config import settings
from app.models.user import User
from app.schemas.report import (
    ReportRequest,
    ReportResponse,
    ReportPreviewRequest,
    PolishRequest,
    ExportRequest,
    PathReportRequest,          # 确保已导入
)
from app.services.report import (
    get_report_data,
    polish_text,
    generate_report_from_data,
    generate_report,
    generate_path_report,
)

router = APIRouter()


@router.post("/generate", response_model=ReportResponse)
def generate_report_endpoint(
    request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ReportResponse:
    # 权限校验：只能生成自己的报告
    if request.student_id != current_user.student_id:      # 改为 student_id
        raise HTTPException(status_code=404, detail="学生不存在或无权访问")
    try:
        report_path = generate_report(db, request.student_id, request.job_title)
        filename = os.path.basename(report_path)
        return ReportResponse(
            report_url=f"/api/v1/report/files/{filename}",
            message="报告生成成功"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


@router.get("/files/{filename}")
def download_report(
    filename: str,
    current_user: User = Depends(get_current_user)
) -> FileResponse:
    parts = filename.split('_')
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="无效的文件名")
    try:
        student_id = int(parts[1])
    except ValueError:
        raise HTTPException(status_code=400, detail="无法解析学生 ID")
    if student_id != current_user.student_id:
        raise HTTPException(status_code=404, detail="文件不存在或无权访问")
    file_path = os.path.join(settings.report_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )


@router.post("/preview")
def preview_report(
    request: ReportPreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    if request.student_id != current_user.student_id:
        raise HTTPException(status_code=404, detail="学生不存在或无权访问")
    try:
        data = get_report_data(db, request.student_id, request.job_title)
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成报告数据失败: {str(e)}")


@router.post("/polish")
def polish_report_text(request: PolishRequest) -> Dict[str, str]:
    if not request.text:
        return {"polished_text": ""}
    try:
        # 如果服务层 polish_text 不支持 instruction，可只传 text
        polished = polish_text(request.text, request.instruction)  # 或者只传 text
        return {"polished_text": polished}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"润色失败: {str(e)}")


@router.post("/export")
def export_report(
    request: ExportRequest,
    current_user: User = Depends(get_current_user)
) -> FileResponse:
    student_data = request.report_data.get("student", {})
    student_id = student_data.get("id")
    if not student_id:
        student_id = request.report_data.get("student_id")
    if not student_id:
        raise HTTPException(status_code=400, detail="报告数据中缺少学生 ID")
    if student_id != current_user.student_id:
        raise HTTPException(status_code=404, detail="无权导出此报告")
    try:
        file_path = generate_report_from_data(request.report_data)
        filename = os.path.basename(file_path)
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出报告失败: {str(e)}")


@router.get("/history", response_model=List[dict])
def list_report_history(
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    student_id = current_user.student_id
    if not student_id:
        return []
    pattern = f"report_{student_id}_*.docx"
    full_pattern = os.path.join(settings.report_dir, pattern)
    files = glob.glob(full_pattern)
    result = []
    for file_path in files:
        filename = os.path.basename(file_path)
        parts = filename.split('_')
        if len(parts) >= 3:
            job_title = '_'.join(parts[2:]).replace('.docx', '')
        else:
            job_title = "未知岗位"
        mtime = os.path.getmtime(file_path)
        created_at = datetime.fromtimestamp(mtime).isoformat()
        result.append({
            "filename": filename,
            "created_at": created_at,
            "job_title": job_title,
            "url": f"/api/v1/report/files/{filename}"
        })
    result.sort(key=lambda x: x["created_at"], reverse=True)
    return result


@router.post("/generate_path_report", response_model=ReportResponse)
def generate_path_report_endpoint(
    request: PathReportRequest,
    current_user: User = Depends(get_current_user)
) -> ReportResponse:
    # 权限校验：确保 student.id 与当前用户匹配
    if request.student.get('id') != current_user.student_id:
        raise HTTPException(status_code=404, detail="学生不存在或无权访问")
    try:
        report_path = generate_path_report(request.dict())
        filename = os.path.basename(report_path)
        return ReportResponse(
            report_url=f"/api/v1/report/files/{filename}",
            message="报告生成成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")