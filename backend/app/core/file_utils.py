# import io
# from fastapi import UploadFile
# import pypdf
# import docx
# from app.core.text_cleaner import clean_pdf_text  # 引入清洗模块

# async def extract_text_from_file(file: UploadFile) -> str:
#     """提取上传文件中的文本内容"""
#     content = await file.read()
#     raw_text = ""

#     try:
#         if file.filename.endswith(".pdf"):
#             reader = pypdf.PdfReader(io.BytesIO(content))
#             for page in reader.pages:
#                 raw_text += (page.extract_text() or "") + "\n"
#         elif file.filename.endswith(".docx") or file.filename.endswith(".doc"):
#             doc = docx.Document(io.BytesIO(content))
#             for para in doc.paragraphs:
#                 raw_text += para.text + "\n"
#         elif file.filename.endswith(".txt") or file.filename.endswith(".md"):
#             raw_text += content.decode("utf-8", errors="ignore")
#         else:
#             return f"\n\n--- 附件：{file.filename} （暂不支持该格式自动提取） ---\n"
#     except Exception as e:
#         return f"\n\n--- 附件：{file.filename} （文件解析失败: {str(e)}） ---\n"

#     # 【关键修改】：对提取出来的文本进行全局清洗
#     cleaned_text = clean_pdf_text(raw_text)
    
#     return f"\n\n--- 附件：{file.filename} 开始 ---\n{cleaned_text}\n--- 附件：{file.filename} 结束 ---\n"

import io

import docx
import pypdf
from fastapi import UploadFile

from app.core.text_cleaner import clean_pdf_text


async def extract_file_payload(file: UploadFile) -> dict:
    """
    返回一个统一结构，供“会话绑定文档”和“普通 prompt 拼接”两种场景复用。
    """
    filename = file.filename or "未命名文件"
    lower_name = filename.lower()

    content = await file.read()
    try:
        await file.seek(0)
    except Exception:
        pass

    raw_text = ""

    try:
        if lower_name.endswith(".pdf"):
            reader = pypdf.PdfReader(io.BytesIO(content))
            for page in reader.pages:
                raw_text += (page.extract_text() or "") + "\n"

        elif lower_name.endswith(".docx") or lower_name.endswith(".doc"):
            doc = docx.Document(io.BytesIO(content))
            for para in doc.paragraphs:
                raw_text += para.text + "\n"

        elif lower_name.endswith(".txt") or lower_name.endswith(".md"):
            raw_text += content.decode("utf-8", errors="ignore")

        else:
            return {
                "filename": filename,
                "text": "",
                "supported": False,
                "error": f"暂不支持该格式自动提取：{filename}",
            }

    except Exception as e:
        return {
            "filename": filename,
            "text": "",
            "supported": False,
            "error": f"文件解析失败: {str(e)}",
        }

    cleaned_text = clean_pdf_text(raw_text)

    return {
        "filename": filename,
        "text": cleaned_text,
        "supported": True,
        "error": None,
    }


async def extract_text_from_file(file: UploadFile) -> str:
    """
    兼容你旧的 agent 路由逻辑：仍然返回带包装标记的字符串。
    """
    payload = await extract_file_payload(file)

    if not payload["supported"]:
        return f"\n\n--- 附件：{payload['filename']} （{payload['error']}） ---\n"

    return (
        f"\n\n--- 附件：{payload['filename']} 开始 ---\n"
        f"{payload['text']}\n"
        f"--- 附件：{payload['filename']} 结束 ---\n"
    )