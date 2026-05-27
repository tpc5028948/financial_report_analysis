#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版测试文件解析器
"""
import os
import sys

# 添加项目路径
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_path, 'backend'))

from data_processing.data_parser import DataParser
from data_processing.data_preprocessor import DataPreprocessor
import pandas as pd

def create_sample_excel():
    """创建简单的示例Excel文件"""
    sample_file = os.path.join(project_path, 'sample_financial_data.xlsx')
    
    # 创建简单的财务数据
    data = {
        '财务指标': ['营业收入', '净利润', '总资产', '总负债', '流动资产', '流动负债', '股东权益', '经营现金流'],
        '2023年': [10000000, 1500000, 50000000, 20000000, 15000000, 10000000, 30000000, 2000000]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(sample_file, index=False, engine='openpyxl')
    print(f"已创建示例文件: {sample_file}")
    return sample_file

def test_file_parser():
    """测试文件解析器"""
    print("="*60)
    print("开始测试文件解析器")
    print("="*60)
    
    # 创建解析器实例
    parser = DataParser()
    preprocessor = DataPreprocessor()
    
    # 创建示例文件
    print("\n1. 创建示例Excel文件...")
    test_file = create_sample_excel()
    
    print(f"\n2. 正在测试文件解析: {os.path.basename(test_file)}")
    print("-"*60)
    
    try:
        # 解析文件
        print("   解析文件...")
        raw_data = parser.parse_file(test_file)
        print(f"   解析结果 - 财务指标: {list(raw_data['财务指标'].keys())}")
        
        # 添加必要信息
        raw_data['公司名称'] = '测试公司'
        raw_data['行业分类'] = '制造业'
        
        # 预处理数据
        print("\n3. 预处理数据...")
        processed_data = preprocessor.preprocess(raw_data)
        
        features = processed_data.get('特征', {})
        print(f"   提取特征数: {len(features)}")
        
        # 打印计算的财务指标
        print("\n4. 计算的财务指标:")
        if features:
            print(f"   - 流动比率: {features.get('流动比率', 'N/A'):.4f}")
            print(f"   - 资产负债率: {features.get('资产负债率', 'N/A'):.4f}")
            print(f"   - ROE: {features.get('ROE', 'N/A'):.4f}")
            print(f"   - ROA: {features.get('ROA', 'N/A'):.4f}")
        
        print("\n[OK] 文件解析成功!")
        
    except Exception as e:
        print(f"\n[ERROR] 文件解析失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    test_file_parser()
