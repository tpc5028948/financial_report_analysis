"""
数据验证和清洗模块
确保所有数据类型安全，避免比较错误
"""

import re
import pandas as pd
import numpy as np
from typing import Any, Dict, Optional, Union


class DataValidator:
    """数据验证和清洗器"""

    @staticmethod
    def to_float(value: Any, default: float = 0.0) -> float:
        """安全转换为浮点数"""
        if value is None:
            return default

        if isinstance(value, (int, float, np.integer, np.floating)):
            if pd.isna(value):
                return default
            return float(value)

        if isinstance(value, str):
            value = value.strip()
            if not value:
                return default

            # 移除常见分隔符
            value = value.replace(',', '').replace('，', '').replace(' ', '')

            # 处理万、亿单位
            multiplier = 1.0
            if '亿' in value:
                multiplier = 100000000.0
                value = value.replace('亿', '')
            elif '万' in value:
                multiplier = 10000.0
                value = value.replace('万', '')

            # 提取数字部分
            numbers = re.findall(r'-?\d+\.?\d*', value)
            if numbers:
                try:
                    return float(numbers[0]) * multiplier
                except (ValueError, TypeError):
                    return default

        try:
            result = float(value)
            return result if not pd.isna(result) else default
        except (ValueError, TypeError):
            return default

    @staticmethod
    def to_int(value: Any, default: int = 0) -> int:
        """安全转换为整数"""
        return int(DataValidator.to_float(value, default))

    @staticmethod
    def to_string(value: Any, default: str = '') -> str:
        """安全转换为字符串"""
        if value is None:
            return default

        if isinstance(value, (int, float, np.integer, np.floating)):
            if pd.isna(value):
                return default
            return str(value)

        if isinstance(value, str):
            return value.strip()

        try:
            return str(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def validate_financial_indicators(indicators: Dict[str, Any]) -> Dict[str, float]:
        """验证和清洗财务指标 - 保留所有用户提供的指标"""
        validated = {}

        required_fields = [
            '营业收入', '净利润', '总资产', '总负债',
            '流动资产', '流动负债', '股东权益', '经营现金流'
        ]

        optional_fields = [
            '应收账款', '存货', '固定资产', '无形资产',
            '短期借款', '长期借款', '应付账款', '预收账款',
            '货币资金', '营业成本', '销售费用', '管理费用',
            '财务费用', '研发费用', '营业利润', '利润总额', '所得税'
        ]
        
        # 用户直接提供的比率指标（不应被过滤掉）
        ratio_indicators = [
            '流动比率', '速动比率', '资产负债率', '现金流负债比',
            'ROE', 'ROA', '销售毛利率', '销售净利率', '毛利率', '净利率',
            '总资产周转率', '应收账款周转率', '存货周转率',
            '营收增长率', '利润增长率',
            '上期营收', '上期净利润'
        ]

        # 处理必需字段
        for field in required_fields:
            value = indicators.get(field, 0)
            validated[field] = DataValidator.to_float(value, 0.0)

        # 处理可选字段
        for field in optional_fields:
            value = indicators.get(field)
            if value is not None:
                validated[field] = DataValidator.to_float(value, 0.0)
        
        # 处理用户直接提供的比率指标（优先级最高，不过滤）
        for field in ratio_indicators:
            value = indicators.get(field)
            if value is not None:
                validated[field] = DataValidator.to_float(value, 0.0)
                print(f"验证器保留用户提供的比率指标: {field} = {validated[field]}")

        return validated

    @staticmethod
    def validate_market_data(market_data: Dict[str, Any]) -> Dict[str, float]:
        """验证和清洗市场数据"""
        validated = {}

        fields = [
            '市值', '股价', '市盈率', '市净率', '换手率', '波动率',
            '52周最高', '52周最低', '成交量', '成交额'
        ]

        for field in fields:
            value = market_data.get(field, 0)
            validated[field] = DataValidator.to_float(value, 0.0)

        return validated

    @staticmethod
    def validate_business_info(business_info: Dict[str, Any]) -> Dict[str, Any]:
        """验证和清洗经营信息"""
        validated = {}

        # 数值字段
        numeric_fields = [
            '成立年限', '员工人数', '管理层稳定性', '业务多元化',
            '负面新闻数量', '法律诉讼数量', '行政处罚数量', '专利数量', '研发投入占比'
        ]

        for field in numeric_fields:
            value = business_info.get(field, 0)
            if field in ['管理层稳定性', '业务多元化', '研发投入占比']:
                validated[field] = DataValidator.to_float(value, 0.5)
            else:
                validated[field] = DataValidator.to_int(value, 0)

        # 字符串字段
        string_fields = ['公司名称', '行业分类', '主营业务']

        for field in string_fields:
            value = business_info.get(field, '')
            validated[field] = DataValidator.to_string(value, '')

        return validated

    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """安全除法，避免除零错误"""
        if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
            return default
        try:
            result = numerator / denominator
            return result if not pd.isna(result) else default
        except (ValueError, TypeError, ZeroDivisionError):
            return default

    @staticmethod
    def safe_compare(value1: Any, operator: str, value2: Any) -> bool:
        """安全的比较操作，避免类型不匹配错误"""
        try:
            # 先转换为浮点数
            v1 = DataValidator.to_float(value1)
            v2 = DataValidator.to_float(value2)

            if operator == '>':
                return v1 > v2
            elif operator == '>=':
                return v1 >= v2
            elif operator == '<':
                return v1 < v2
            elif operator == '<=':
                return v1 <= v2
            elif operator == '==':
                return v1 == v2
            elif operator == '!=':
                return v1 != v2
            else:
                return False
        except (ValueError, TypeError):
            return False
