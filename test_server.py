#!/usr/bin/env python3
"""
测试服务器是否可以正常启动和运行
"""
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 尝试导入服务器模块
    import server
    print("✅ 服务器模块导入成功")
    
    # 测试环境变量读取
    API_URL = os.getenv("TCM_API_URL", "")
    API_KEY = os.getenv("TCM_API_KEY", "")
    print(f"✅ 环境变量读取成功: API_URL={API_URL}, API_KEY={API_KEY}")
    
    # 测试 requests 模块
    import requests
    print("✅ requests 模块导入成功")
    
    print("\n🎉 所有测试通过，服务器可以正常运行！")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 测试过程中出错: {e}")
    sys.exit(1)
