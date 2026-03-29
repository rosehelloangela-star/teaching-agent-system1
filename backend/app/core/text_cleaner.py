import re
import unicodedata

def clean_pdf_text(raw_text: str) -> str:
    """
    专门面向 LLM 提取任务的 PDF 文本清洗函数。
    目标：去除导致报错的非法字符、排版乱码，保留完整的句子语义结构。
    """
    if not raw_text:
        return ""

    # 1. 解决 utf-8 代理对(surrogates)和非法字符报错 (解决你的报错痛点)
    text = raw_text.encode('utf-8', errors='ignore').decode('utf-8')

    # 2. Unicode 标准化 
    # 将全角英数字符转为半角，合并组合字符，消除奇怪的排版符号带来的困扰
    text = unicodedata.normalize('NFKC', text)

    # 3. 剔除不可见的控制字符 (但保留换行符 \n 和制表符 \t)
    # 很多 PDF 转换过来的乱码都属于这类不可见字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # 4. 修复 PDF 特有的断行问题
    # PDF 经常把一句话从中间截断并加上换行符，或者英文单词加上连字符断行
    text = re.sub(r'-\n\s*', '', text)  # 修复英文换行连字符 (如 "infor-\nmation" -> "information")
    
    # 5. 合并多余的空白和换行 (防止 Token 浪费)
    # 将连续多个空格或 Tab 压缩为一个空格
    text = re.sub(r'[ \t]+', ' ', text)
    # 将连续 3 个以上的换行符压缩为 2 个换行符 (保留段落的视觉划分)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 6. 去除不可见的零宽字符 (Zero-width characters)
    text = text.replace('\u200b', '').replace('\uFEFF', '')

    return text.strip()

def chunk_text_by_length(text: str, chunk_size: int = 2000, overlap: int = 100) -> list[str]:
    """
    （可选增强）提供一个带重叠(overlap)的切片函数，
    防止生硬截断导致上下文语义丢失。
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # 下一次切片往回退 overlap 的长度，确保句子不断裂
        start = end - overlap 
        
    return chunks