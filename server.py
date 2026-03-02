#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCM Constitution MCP Server (Sync Version)
专为阿里云百炼 + 函数计算环境优化
"""
import sys
import json
import os
import random

# 尝试导入requests库
HAS_REQUESTS = False
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    sys.stderr.write("[TCM-MCP] Warning: requests library not found, will run in mock mode\n")
    sys.stderr.flush()

# ==========================================
# 1. 安全日志配置 (严禁污染 stdout)
# ==========================================
def log(msg):
    """
    将日志输出到 stderr 并立即刷新。
    绝对禁止使用 print()，否则会破坏 MCP 协议 JSON 流。
    """
    try:
        sys.stderr.write(f"[TCM-MCP] {msg}\n")
        sys.stderr.flush()
    except Exception:
        pass

# ==========================================
# 2. 配置与环境变量
# ==========================================
API_URL = os.getenv("TCM_API_URL", "")
API_KEY = os.getenv("TCM_API_KEY", "")
# 如果未配置 URL 或设置为 'mock'，则启用模拟模式
IS_MOCK = not API_URL or API_URL == "mock"

# ==========================================
# 3. 业务逻辑 (Mock 数据生成)
# ==========================================
def get_mock_analysis_result(face_url: str, tongue_url: str) -> dict:
    """生成模拟的体质分析结果"""
    constitutions = [
        {"type": "平和质", "desc": "阴阳气血调和，体态适中，面色红润"},
        {"type": "气虚质", "desc": "元气不足，容易疲乏，气短懒言"},
        {"type": "阳虚质", "desc": "阳气不足，手脚发凉，喜热饮食"},
        {"type": "阴虚质", "desc": "阴液亏少，口燥咽干，手足心热"},
        {"type": "痰湿质", "desc": "痰湿凝聚，形体肥胖，腹部肥满"},
        {"type": "湿热质", "desc": "湿热内蕴，面垢油光，易生痤疮"},
        {"type": "血瘀质", "desc": "血行不畅，肤色晦暗，色素沉着"},
        {"type": "气郁质", "desc": "气机郁滞，神情抑郁，忧虑脆弱"},
        {"type": "特禀质", "desc": "先天失常，易患过敏，适应能力差"}
    ]
    
    selected = random.choice(constitutions)
    confidence = round(random.uniform(0.75, 0.95), 2)
    
    return {
        "status": "success",
        "is_mock": True,
        "primary_constitution": selected["type"],
        "confidence_score": confidence,
        "description": selected["desc"],
        "evidence": {
            "face": f"基于面部图像 ({face_url})：面色{'红润' if '平和' in selected['type'] else '偏黄/白'}，神态{'佳' if '平和' in selected['type'] else '一般'}。",
            "tongue": f"基于舌部图像 ({tongue_url})：舌质{'淡红' if '平和' in selected['type'] else '偏淡/红'}，舌苔薄白。"
        },
        "suggestions": {
            "diet": "建议饮食清淡，规律作息，避免辛辣油腻。" if "湿热" in selected['type'] else "建议均衡饮食，适量运动，保持心情舒畅。",
            "lifestyle": "推荐进行温和的有氧运动，如散步、太极拳。"
        },
        "warning": "【测试模式】此为模拟数据，仅供开发验证，不作为医疗诊断依据。"
    }

# ==========================================
# 4. MCP 协议处理逻辑
# ==========================================
def handle_request(req: dict) -> dict:
    """处理传入的 JSON-RPC 请求"""
    method = req.get("method")
    req_id = req.get("id")
    params = req.get("params", {})
    
    log(f"Received method: {method}")

    # --- 1. 处理 initialize (握手关键) ---
    if method == "initialize":
        log("✅ Received 'initialize'. Sending handshake response...")
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "tcm-vision-analyzer",
                    "version": "1.0.0"
                }
            }
        }

    # --- 2. 处理 initialized 通知 (无需回复) ---
    if method == "notifications/initialized":
        log("🎉 Client initialized successfully! Server is ready to serve tools.")
        return None

    # --- 3. 处理 tools/list (注册工具) ---
    if method == "tools/list":
        log("Sending tools list...")
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "analyze_constitution",
                        "description": "基于用户上传的面部和舌部照片，进行中医体质辨识分析，返回体质类型及调理建议。",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "face_image_url": {
                                    "type": "string",
                                    "description": "用户正面免冠面部照片的 URL 地址"
                                },
                                "tongue_image_url": {
                                    "type": "string",
                                    "description": "用户自然伸舌照片的 URL 地址"
                                }
                            },
                            "required": ["face_image_url", "tongue_image_url"]
                        }
                    }
                ]
            }
        }

    # --- 4. 处理 tools/call (执行工具) ---
    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        log(f"Calling tool: {tool_name} with args: {arguments}")
        
        # 检查工具名称
        if tool_name != "analyze_constitution":
            log(f"Unknown tool: {tool_name}")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
        
        # 处理 analyze_constitution 工具
        face_url = arguments.get("face_image_url", "")
        tongue_url = arguments.get("tongue_image_url", "")
            
        if not face_url or not tongue_url:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": "Missing required arguments: face_image_url and tongue_image_url"
                }
            }
            
        # 执行业务逻辑
        if IS_MOCK or not HAS_REQUESTS:
            log("⚠️ Running in MOCK mode" + (" (requests library not available)" if not HAS_REQUESTS else ""))
            result_data = get_mock_analysis_result(face_url, tongue_url)
        else:
            # 真实 API 调用逻辑
            log(f"✅ Running in REAL API mode: {API_URL}")
            try:
                # 构建请求数据
                payload = {
                    "faceImgUrl": face_url,
                    "tongueImgUrl": tongue_url
                }
                
                # 设置请求头
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}"
                }
                
                # 调用 API
                response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                # 解析响应
                api_result = response.json()
                
                if api_result.get('code') == 200:
                    data = api_result.get('data', {})
                    # 转换为标准格式
                    result_data = {
                        "status": "success",
                        "is_mock": False,
                        "primary_constitution": data.get('primary_constitution', ''),
                        "confidence_score": data.get('confidence_score', 0.0),
                        "description": data.get('description', ''),
                        "evidence": {
                            "face": data.get('face_evidence', ''),
                            "tongue": data.get('tongue_evidence', '')
                        },
                        "suggestions": {
                            "diet": data.get('diet_suggestion', ''),
                            "lifestyle": data.get('lifestyle_suggestion', '')
                        },
                        "warning": "" if not data.get('warning_flags') else "，".join(data.get('warning_flags', []))
                    }
                else:
                    log(f"API returned error: {api_result.get('message')}")
                    result_data = {
                        "status": "error",
                        "message": f"API 返回错误：{api_result.get('message')}"
                    }
                    
            except Exception as e:
                log(f"API request failed: {str(e)}")
                result_data = {
                    "status": "error",
                    "message": f"API 调用失败：{str(e)}"
                }
            
        # 构造符合 MCP 标准的返回格式
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result_data, ensure_ascii=False)
                    }
                ]
            }
        }

    # --- 5. 未知方法 ---
    log(f"Unknown method: {method}")
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": "Method not found"
        }
    }

def send_response(response_obj: dict):
    """发送 JSON 响应到 stdout，并强制刷新缓冲区"""
    if response_obj is None:
        return
    
    try:
        json_str = json.dumps(response_obj, ensure_ascii=False) + "\n"
        sys.stdout.write(json_str)
        sys.stdout.flush()  # <--- 关键！必须立即刷新，否则平台收不到数据
        # log(f"Sent response (length: {len(json_str)})") # 调试时可打开
    except Exception as e:
        log(f"CRITICAL: Failed to write to stdout: {e}")

# ==========================================
# 5. 主入口函数 (被 pyproject.toml 调用)
# ==========================================
def main():
    """MCP 服务主入口"""
    log("="*50)
    log("🚀 Starting TCM Vision Analyzer MCP Server (Sync Mode)")
    log(f"   Mode: {'MOCK' if IS_MOCK else 'REAL'}")
    log(f"   Python Version: {sys.version}")
    log("="*50)
    
    try:
        while True:
            # 阻塞式读取 stdin 一行
            line = sys.stdin.readline()
            
            # 检测 EOF (连接关闭)
            if not line:
                log("stdin closed. Exiting server loop.")
                break
            
            line = line.strip()
            if not line:
                continue
            
            # log(f"Raw Input: {line}") # 生产环境建议关闭，减少日志噪音
            
            try:
                req = json.loads(line)
                resp = handle_request(req)
                send_response(resp)
            except json.JSONDecodeError as e:
                log(f"JSON Decode Error: {e}")
                # 尝试返回错误响应
                send_response({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"}
                })
            except Exception as e:
                log(f"Critical Error in loop: {e}", exc_info=True)
                # 即使出错也尝试返回错误，防止连接断开
                send_response({
                    "jsonrpc": "2.0",
                    "id": req.get("id"),
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                })
                
    except KeyboardInterrupt:
        log("Stopped by user (KeyboardInterrupt).")
    except Exception as e:
        log(f"Fatal Crash: {e}", exc_info=True)
        sys.exit(1)
    
    log("Server shutdown complete.")

if __name__ == "__main__":
    main()