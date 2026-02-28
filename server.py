#!/usr/bin/env python3
import sys
import json
import os

# 唯一的日志函数，强制输出到 stderr 并立即刷新
def log(msg):
    sys.stderr.write(f"[LOG] {msg}\n")
    sys.stderr.flush()

def send_response(response_obj):
    """发送 JSON 响应到 stdout，并强制刷新"""
    if response_obj is None:
        return
    
    json_str = json.dumps(response_obj, ensure_ascii=False) + "\n"
    sys.stdout.write(json_str)
    sys.stdout.flush()  # <--- 关键！必须刷新缓冲区
    # log(f"Sent: {json_str.strip()}") # 调试时可打开

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")
    
    # 1. Initialize (握手)
    if method == "initialize":
        log("Received 'initialize'. Sending handshake...")
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": { "tools": {} },
                "serverInfo": { "name": "sync-tcm-mcp", "version": "1.0.0" }
            }
        }
    
    # 2. Initialized Notification
    if method == "notifications/initialized":
        log("✅ MCP Server Successfully Initialized & Ready!")
        return None
    
    # 3. Tools List
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "hello_world",
                        "description": "测试工具：证明同步模式部署成功。",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                ]
            }
        }
    
    # 4. Tools Call
    if method == "tools/call":
        tool_name = req.get("params", {}).get("name")
        if tool_name == "hello_world":
            log("Executing hello_world tool...")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        { "type": "text", "text": "🎉 成功！同步模式 MCP 服务已就绪！" }
                    ]
                }
            }
    
    # Error
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": { "code": -32601, "message": "Method not found" }
    }

def main():
    log("="*40)
    log("🚀 Starting SYNC MCP Server (No Asyncio)...")
    log("="*40)
    
    try:
        while True:
            # 阻塞式读取一行 stdin
            line = sys.stdin.readline()
            
            if not line:
                log("stdin ended. Exiting.")
                break
            
            line = line.strip()
            if not line:
                continue
            
            # log(f"Raw Input: {line}") # 生产环境可注释掉
            
            try:
                req = json.loads(line)
                resp = handle_request(req)
                send_response(resp)
            except json.JSONDecodeError as e:
                log(f"JSON Decode Error: {e}")
            except Exception as e:
                log(f"Critical Error in loop: {e}")
                # 即使出错也要尝试返回错误响应，防止连接断开
                send_response({
                    "jsonrpc": "2.0",
                    "id": req.get("id"),
                    "error": { "code": -32603, "message": str(e) }
                })
                
    except KeyboardInterrupt:
        log("Stopped by user.")
    except Exception as e:
        log(f"Fatal Crash: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()