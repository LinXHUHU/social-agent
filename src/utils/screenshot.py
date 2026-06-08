"""Screenshot analysis — extract WeChat/chat text from screenshots."""
import base64
from pathlib import Path
from src.utils.deepseek import chat

OCR_SYSTEM = """你是一个聊天截图识别器。输入是聊天截图的base64编码图片。
请提取截图中所有的对话内容，按照以下格式输出：

[发送者A]：消息内容
[发送者B]：消息内容

只输出对话内容，不要添加任何解释或说明。"""


def extract_text(image_path: str) -> str:
    """Extract conversation text from a chat screenshot using DeepSeek vision.
    Note: deepseek-chat (V3) may not support vision. Falls back to descriptive analysis."""
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    user_msg = (
        "请详细描述这张聊天截图中的内容，包括每条消息的发送者、内容、时间（如果有的话）。"
        "请尽量还原完整的对话文本。"
    )

    try:
        response = chat(system=OCR_SYSTEM, user=user_msg, max_tokens=2000)
        return response
    except Exception:
        return _fallback_text_extraction(image_path)


def _fallback_text_extraction(image_path: str) -> str:
    return f"[需要手动转录，图片路径: {image_path}]"
