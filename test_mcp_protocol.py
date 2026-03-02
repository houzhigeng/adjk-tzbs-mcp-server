#!/usr/bin/env python3
"""
测试MCP服务器的协议实现
"""
import json
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import handle_request

def test_initialize():
    """测试initialize方法"""
    print("=== 测试 initialize 方法 ===")
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    resp = handle_request(req)
    print(f"请求: {json.dumps(req, ensure_ascii=False)}")
    print(f"响应: {json.dumps(resp, ensure_ascii=False)}")
    print()

def test_tools_list():
    """测试tools/list方法"""
    print("=== 测试 tools/list 方法 ===")
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    resp = handle_request(req)
    print(f"请求: {json.dumps(req, ensure_ascii=False)}")
    print(f"响应: {json.dumps(resp, ensure_ascii=False)}")
    print()

def test_tools_call():
    """测试tools/call方法"""
    print("=== 测试 tools/call 方法 ===")
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "analyze_constitution",
            "arguments": {
                "face_image_url": "https://example.com/face.jpg",
                "tongue_image_url": "https://example.com/tongue.jpg"
            }
        }
    }
    resp = handle_request(req)
    print(f"请求: {json.dumps(req, ensure_ascii=False)}")
    print(f"响应: {json.dumps(resp, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    test_initialize()
    test_tools_list()
    test_tools_call()
    print("=== 所有测试完成 ===")
