import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'backend'))

# 导入并运行Flask应用
from backend.api.app import app

if __name__ == '__main__':
    print("启动企业信用评估模型服务...")
    print("服务地址: http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)
