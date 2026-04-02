import io
import re
import uuid
from pathlib import Path

import docx
import pypdf
from fastapi import UploadFile

from app.core.text_cleaner import clean_pdf_text

ATTACHMENT_ROOT = Path('uploaded_teacher_files')
ATTACHMENT_ROOT.mkdir(parents=True, exist_ok=True)


def _sanitize_filename(filename: str) -> str:
    filename = Path(filename or 'attachment').name
    filename = re.sub(r'[^A-Za-z0-9._-]+', '_', filename)
    return filename[:120] or 'attachment'


async def save_teacher_attachment(file: UploadFile) -> dict:
    original_name = file.filename or 'attachment'
    safe_name = _sanitize_filename(original_name)
    stored_name = f"{uuid.uuid4().hex}_{safe_name}"
    target = ATTACHMENT_ROOT / stored_name

    content = await file.read()
    with open(target, 'wb') as f:
        f.write(content)

    try:
        await file.seek(0)
    except Exception:
        pass

    return {
        'file_id': stored_name,
        'name': original_name,
        'size': len(content),
        'type': getattr(file, 'content_type', None) or '',
        'download_url': f'/api/v1/conversations/attachments/{stored_name}',
    }


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
