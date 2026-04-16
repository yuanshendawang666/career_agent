"""
大语言模型客户端模块

封装对 DashScope 平台通义千问模型的调用，提供统一的文本生成接口。
"""
import dashscope
from dashscope import Generation

from app.core.config import settings

# 设置 DashScope API Key，从配置中读取
dashscope.api_key = settings.dashscope_api_key

# 如果配置中设置了自定义 base_url（用于非北京地域或其他代理），则覆盖默认端点
if settings.dashscope_base_url:
    dashscope.base_http_api_url = settings.dashscope_base_url


def call_qwen(
    user_prompt: str,
    system_prompt: str = None,
    max_tokens: int = 800,
    temperature: float = 0.3,
    enable_thinking: bool = False,
) -> str:
    """
    调用通义千问模型，返回模型生成的文本内容。

    该函数封装了 DashScope 的对话接口，支持系统角色设定、输出长度控制、
    随机性调节及深度思考模式。

    Args:
        user_prompt (str): 用户的输入提示，即问题或指令。
        system_prompt (str, optional): 系统角色设定，用于约束模型的行为风格。
            例如：“你是一个专业的简历解析助手”。
        max_tokens (int, optional): 生成文本的最大 token 数，默认 800。
        temperature (float, optional): 采样温度，控制输出的随机性。
            范围 0~1，值越小越确定，默认 0.3。
        enable_thinking (bool, optional): 是否开启深度思考模式（仅部分模型支持），
            默认 False。

    Returns:
        str: 模型返回的文本内容。

    Raises:
        Exception: 当 API 调用失败时抛出，包含状态码和错误信息。
    """
    # 构建消息列表，符合 DashScope 对话格式
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    # 调用 DashScope 生成接口
    response = Generation.call(
        model=settings.qwen_model,           # 模型名称，从配置读取
        messages=messages,                   # 对话消息列表
        max_tokens=max_tokens,               # 最大输出 token 数
        temperature=temperature,             # 温度参数
        result_format="message",             # 返回格式为 message，便于提取内容
        enable_thinking=enable_thinking,     # 是否启用深度思考模式
    )

    # 检查 API 调用是否成功
    if response.status_code == 200:
        # 从响应中提取模型生成的文本内容
        return response.output.choices[0].message.content
    else:
        # 调用失败时抛出异常，包含详细错误信息
        raise Exception(
            f"API调用失败，状态码：{response.status_code}，错误：{response.message}"
        )