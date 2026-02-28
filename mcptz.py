#!/usr/bin/env python3
import os, sys, logging, random
from mcp.server.fastmcp import FastMCP

# --- 配置 ---
TCM_API_URL = os.getenv("TCM_API_URL", "")
TCM_API_KEY = os.getenv("TCM_API_KEY", "")

# 判断是否使用 Mock 模式
USE_MOCK = not TCM_API_URL or TCM_API_URL == "mock"

mcp = FastMCP("tcm-vision-analyzer")
logging.basicConfig(level=logging.INFO, stream=sys.stderr)

# --- Mock 数据生成器 ---
def generate_mock_result(face_url: str, tongue_url: str) -> dict:
    """生成模拟的体质分析结果"""
    constitutions = [
        {"type": "平和质", "desc": "阴阳气血调和，体态适中"},
        {"type": "气虚质", "desc": "元气不足，容易疲乏"},
        {"type": "阳虚质", "desc": "阳气不足，手脚发凉"},
        {"type": "阴虚质", "desc": "阴液亏少，口燥咽干"},
        {"type": "痰湿质", "desc": "痰湿凝聚，形体肥胖"},
        {"type": "湿热质", "desc": "湿热内蕴，面垢油光"},
        {"type": "血瘀质", "desc": "血行不畅，肤色晦暗"},
        {"type": "气郁质", "desc": "气机郁滞，神情抑郁"},
        {"type": "特禀质", "desc": "先天失常，易患过敏"}
    ]
    
    # 随机选择一个体质
    selected = random.choice(constitutions)
    confidence = round(random.uniform(0.75, 0.95), 2)
    
    return {
        "primary_constitution": selected["type"],
        "confidence_score": confidence,
        "secondary_constitutions": [],
        "face_evidence": f"基于面部图像分析：面色{'红润' if '平和' in selected['type'] else '偏黄'}，皮肤状态良好。",
        "tongue_evidence": f"基于舌部图像分析：舌质{'淡红' if '平和' in selected['type'] else '偏淡'}，舌苔薄白。",
        "diet_suggestion": "建议饮食清淡，多吃蔬菜水果，少吃辛辣油腻食物。",
        "lifestyle_suggestion": "保持规律作息，适量运动，避免熬夜。",
        "warning_flags": ["mock_mode"],  # 标记这是模拟数据
        "is_mock": True
    }

# --- MCP Tool 定义 ---
@mcp.tool()
async def analyze_constitution(
    face_image_url: str,
    tongue_image_url: str
) -> dict:
    """
    【核心功能】基于面部和舌部照片进行中医体质辨识分析。
    
    如果配置了真实的 TCM_API_URL，则调用后端 API；
    否则返回模拟数据用于测试验证。
    """
    logging.info(f"收到分析请求 - Face: {face_image_url}, Tongue: {tongue_image_url}")
    logging.info(f"当前模式：{'Mock 模式' if USE_MOCK else '真实 API 模式'}")
    
    try:
        if USE_MOCK:
            # 返回模拟数据
            logging.warning("⚠️  未配置有效 API 地址，使用 Mock 数据返回")
            result = generate_mock_result(face_image_url, tongue_image_url)
            result["_message"] = "【测试模式】此为模拟数据，非真实分析结果"
            return result
        
        else:
            # 调用真实后端 API
            import requests
            payload = {
                "data": {
                    "face_image": face_image_url,
                    "tongue_image": tongue_image_url
                },
                "config": {
                    "return_confidence": True,
                    "include_suggestions": True
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TCM_API_KEY}"
            }
            
            response = requests.post(TCM_API_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            api_result = response.json()
            if api_result.get('code') == 200:
                return api_result.get('data', {})
            else:
                return {"error": True, "message": f"API 返回错误：{api_result.get('message')}"}
                
    except Exception as e:
        logging.error(f"分析过程出错：{str(e)}")
        # 即使出错也返回一个友好的错误结构
        return {
            "error": True, 
            "message": str(e),
            "fallback_to_mock": True,
            "_message": "分析失败，已切换到模拟模式"
        }

if __name__ == "__main__":
    if USE_MOCK:
        logging.warning("=" * 50)
        logging.warning("🚀 启动于 MOCK 模式 - 用于开发测试")
        logging.warning("📝 未配置 TCM_API_URL 或设置为 'mock'")
        logging.warning("=" * 50)
    else:
        logging.info(f"✅ 启动于真实 API 模式 - 目标：{TCM_API_URL}")
    
    mcp.run()