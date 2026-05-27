#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据一致性：验证系统使用的数据与Excel原始数据一致
"""
import os
import sys
import pandas as pd

# 添加项目路径
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_path, 'backend'))

from data_processing.data_parser import DataParser
from data_processing.data_preprocessor import DataPreprocessor

def create_test_excel():
    """创建模拟腾讯财务数据的Excel文件"""
    sample_file = os.path.join(project_path, 'test_tencent_data.xlsx')
    
    # 模拟腾讯财务数据（与用户提供的一致）
    data = {
        '指标': [
            '流动比率', '速动比率', '资产负债率(%)', '现金流负债比',
            'ROE(%)', 'ROA(%)', '销售毛利率(%)', '销售净利率(%)',
            '总资产周转率', '应收账款周转率', '存货周转率',
            '营收增长率(%)', '利润增长率(%)',
            '市盈率(P/E)', '市净率(P/B)', '市销率(P/S)',
            '公司名称', '股票代码',
            '总资产(亿元)', '总负债(亿元)', '流动资产(亿元)', '流动负债(亿元)',
            '存货(亿元)', '应收账款(亿元)', '股东权益(亿元)',
            '营业收入(亿元)', '营业成本(亿元)', '净利润(亿元)', '经营现金流(亿元)',
            '上期营收(亿元)', '上期净利润(亿元)',
            '市值(亿元)'
        ],
        '数值': [
            1.53, 1.53, 40.83, 0.36,
            18.64, 11.03, 52.89, 29.75,
            0.37, 13.70, 707.05,
            7.98, 66.50,
            21.07, 3.93, 6.27,
            '腾讯控股', '00700.HK',
            17810.00, 7271.00, 5962.00, 3885.00,
            4.40, 482.00, 10539.00,
            6603.00, 3111.00, 1964.67, 2585.00,
            6115.00, 1180.00,
            'N/A'
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(sample_file, index=False, engine='openpyxl')
    print(f"已创建测试文件: {sample_file}")
    return sample_file

def test_data_consistency():
    """测试数据一致性"""
    print("="*70)
    print("测试数据一致性")
    print("="*70)
    
    # 创建解析器实例
    parser = DataParser()
    preprocessor = DataPreprocessor()
    
    # 创建测试文件
    print("\n1. 创建模拟腾讯财务数据的Excel文件...")
    test_file = create_test_excel()
    
    print(f"\n2. 正在测试文件解析: {os.path.basename(test_file)}")
    print("-"*70)
    
    try:
        # 解析文件
        print("   解析文件...")
        raw_data = parser.parse_file(test_file)
        
        print(f"\n   解析到的财务指标:")
        for key, value in raw_data['财务指标'].items():
            print(f"     {key}: {value}")
        
        # 添加必要信息
        raw_data['公司名称'] = '腾讯控股'
        raw_data['行业分类'] = '科技'
        
        # 预处理数据
        print("\n3. 预处理数据...")
        processed_data = preprocessor.preprocess(raw_data)
        
        features = processed_data.get('特征', {})
        
        print("\n   预处理后的特征指标:")
        for key, value in features.items():
            print(f"     {key}: {value}")
        
        # 验证关键指标
        print("\n4. 验证关键指标一致性:")
        print("-"*70)
        
        checks = {
            '流动比率': (1.53, 0.01),
            '资产负债率': (0.4083, 0.01),
            'ROE': (0.1864, 0.01),
            'ROA': (0.1103, 0.01),
            '销售毛利率': (0.5289, 0.01),
            '销售净利率': (0.2975, 0.01),
            '总资产周转率': (0.37, 0.01),
            '应收账款周转率': (13.70, 0.01),
            '存货周转率': (707.05, 0.01),
            '营收增长率': (0.0798, 0.01),
            '利润增长率': (0.6650, 0.01),
            '总资产': (17810.00, 1),
            '营业收入': (6603.00, 1),
            '净利润': (1964.67, 1),
        }
        
        all_passed = True
        for indicator, (expected, tolerance) in checks.items():
            actual = features.get(indicator, 'N/A')
            if actual != 'N/A':
                if abs(actual - expected) <= tolerance:
                    print(f"   [OK] {indicator}: {actual} (期望: {expected})")
                else:
                    print(f"   [FAIL] {indicator}: {actual} (期望: {expected})")
                    all_passed = False
            else:
                print(f"   [FAIL] {indicator}: 未找到 (期望: {expected})")
                all_passed = False
        
        print("\n" + "="*70)
        if all_passed:
            print("[OK] 所有指标验证通过！数据一致性良好！")
        else:
            print("[WARNING] 部分指标不一致，需要进一步调试")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_consistency()
