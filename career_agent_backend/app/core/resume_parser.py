"""
简历解析模块

提供从 PDF、Word (.docx) 和纯文本文件中提取文本内容的功能。
"""
import os
from typing import Optional

import PyPDF2
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """
    从 PDF 文件中提取所有页面的文本内容。

    Args:
        file_path (str): PDF 文件的路径。

    Returns:
        str: 提取的全部文本内容，若页面无文本则可能为空字符串。

    Raises:
        Exception: 当文件读取或解析失败时抛出，包含具体错误信息。
    """
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        raise Exception(f"PDF解析失败: {e}")
    return text


def extract_text_from_docx(file_path: str) -> str:
    """
    从 Word 文档 (.docx) 中提取所有段落的文本内容。

    Args:
        file_path (str): Word 文档的路径。

    Returns:
        str: 提取的全部文本内容，段落之间用换行符连接。

    Raises:
        Exception: 当文件读取或解析失败时抛出，包含具体错误信息。
    """
    try:
        doc = Document(file_path)
        # 收集所有段落的文本，并用换行符拼接
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        raise Exception(f"Word解析失败: {e}")


def extract_text_from_txt(file_path: str) -> str:
    """
    从纯文本文件中读取内容（UTF-8 编码）。

    Args:
        file_path (str): 文本文件的路径。

    Returns:
        str: 文件的全部内容。

    Raises:
        Exception: 当文件读取失败时抛出，包含具体错误信息。
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise Exception(f"文本文件读取失败: {e}")


def parse_resume(file_path: str) -> str:
    """
    根据文件扩展名选择相应的解析器，提取简历文本内容。

    支持的文件类型：
        - .pdf  : 使用 PyPDF2 提取
        - .docx : 使用 python-docx 提取
        - .txt  : 直接读取文本内容

    Args:
        file_path (str): 简历文件的路径。

    Returns:
        str: 提取出的简历文本内容。

    Raises:
        ValueError: 当文件扩展名不在支持列表中时抛出。
        Exception: 当具体解析函数抛出异常时，向上传递。
    """
    # 获取文件扩展名并转换为小写
    ext = os.path.splitext(file_path)[1].lower()

    # 根据扩展名调用对应的解析函数
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {ext}")