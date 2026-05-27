#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细的后端服务启动脚本，捕获并显示所有错误
"""

import sys
import traceback

print('Starting backend service...')
print('Python version:', sys.version)
print('Current directory:', sys.path)

try:
    from backend.api.app import app
    print('Imported app successfully')
    
    if __name__ == '__main__':
        print('Running app...')
        app.run(debug=True, host='0.0.0.0', port=5000)
        
except Exception as e:
    print('Error:', str(e))
    print('Traceback:')
    traceback.print_exc()
    print('Exiting...')
    sys.exit(1)
