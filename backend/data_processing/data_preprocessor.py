"""
数据预处理模块 - 使用真实行业基准数据
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
import os
import sys
import json

# 添加当前目录到路径以支持相对导入
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from data_validator import DataValidator
except ImportError:
    # 如果相对导入失败，使用绝对导入
    from backend.data_processing.data_validator import DataValidator

class DataPreprocessor:
    """数据预处理器 - 使用真实行业基准数据"""

    def __init__(self):
        self.validator = DataValidator()
        self.industry_benchmarks = self._load_industry_benchmarks()

    def _load_industry_benchmarks(self):
        """加载真实的行业基准数据"""
        benchmarks_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'industry_benchmarks.json')
        
        if os.path.exists(benchmarks_file):
            try:
                with open(benchmarks_file, 'r', encoding='utf-8') as f:
                    benchmarks = json.load(f)
                print(f"成功加载行业基准数据，共 {len(benchmarks)} 个行业")
                return benchmarks
            except Exception as e:
                print(f"加载行业基准数据失败: {e}")
                return self._get_default_benchmarks()
        else:
            print("行业基准数据文件不存在，使用默认数据")
            return self._get_default_benchmarks()

    def _get_default_benchmarks(self):
        """获取默认行业基准数据"""
        return {
            '制造业': {
                '平均资产负债率': 0.60,
                '平均净利润率': 0.06,
                '平均总资产周转率': 0.78,
                '平均市盈率': 10.30,
                '平均研发投入占比': 0.04
            },
            '信息技术': {
                '平均资产负债率': 0.35,
                '平均净利润率': 0.20,
                '平均总资产周转率': 1.50,
                '平均市盈率': 25.00,
                '平均研发投入占比': 0.10
            },
            '金融服务': {
                '平均资产负债率': 0.83,
                '平均净利润率': 0.16,
                '平均总资产周转率': 0.31,
                '平均市盈率': 8.09,
                '平均研发投入占比': 0.03
            },
            '房地产': {
                '平均资产负债率': 0.77,
                '平均净利润率': 0.10,
                '平均总资产周转率': 0.19,
                '平均市盈率': 6.70,
                '平均研发投入占比': 0.01
            },
            '零售': {
                '平均资产负债率': 0.51,
                '平均净利润率': 0.04,
                '平均总资产周转率': 2.04,
                '平均市盈率': 16.46,
                '平均研发投入占比': 0.01
            },
            '能源': {
                '平均资产负债率': 0.73,
                '平均净利润率': 0.08,
                '平均总资产周转率': 0.32,
                '平均市盈率': 9.98,
                '平均研发投入占比': 0.02
            },
            '医疗健康': {
                '平均资产负债率': 0.40,
                '平均净利润率': 0.15,
                '平均总资产周转率': 0.60,
                '平均市盈率': 28.00,
                '平均研发投入占比': 0.07
            },
            '交通运输': {
                '平均资产负债率': 0.65,
                '平均净利润率': 0.04,
                '平均总资产周转率': 0.40,
                '平均市盈率': 8.00,
                '平均研发投入占比': 0.02
            }
        }

    def preprocess(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """预处理原始数据"""
        processed_data = {}

        # 提取基本信息
        processed_data['公司名称'] = self.validator.to_string(raw_data.get('公司名称', '未知公司'))
        processed_data['行业分类'] = self.validator.to_string(raw_data.get('行业分类', '制造业'))
        processed_data['报告期'] = self.validator.to_string(raw_data.get('报告期', '未知'))
        processed_data['评估日期'] = datetime.now().strftime('%Y-%m-%d')

        # 处理财务指标
        financial_indicators = raw_data.get('财务指标', {})
        processed_data['财务指标'] = self.validator.validate_financial_indicators(financial_indicators)

        # 处理市场数据
        market_data = raw_data.get('市场数据', {})
        processed_data['市场数据'] = self.validator.validate_market_data(market_data)

        # 处理经营信息
        business_info = raw_data.get('经营信息', {})
        processed_data['经营信息'] = self.validator.validate_business_info(business_info)

        # 提取多维度特征
        processed_data['特征'] = self._extract_features(processed_data)

        # 计算信用评估指标
        processed_data['信用评估指标'] = self._calculate_credit_indicators(processed_data)

        # 计算与行业平均的对比
        processed_data['行业对比'] = self._calculate_industry_comparison(processed_data)

        return processed_data

    def _extract_features(self, processed_data: Dict[str, Any]) -> Dict[str, float]:
        """提取多维度特征"""
        features = {}
        
        # 1. 财务特征
        financials = processed_data.get('财务指标', {})
        features['营业收入'] = self.validator.to_float(financials.get('营业收入', 0))
        features['净利润'] = self.validator.to_float(financials.get('净利润', 0))
        features['总资产'] = self.validator.to_float(financials.get('总资产', 0))
        features['总负债'] = self.validator.to_float(financials.get('总负债', 0))
        features['流动资产'] = self.validator.to_float(financials.get('流动资产', 0))
        features['流动负债'] = self.validator.to_float(financials.get('流动负债', 0))
        features['股东权益'] = self.validator.to_float(financials.get('股东权益', 0))
        features['经营现金流'] = self.validator.to_float(financials.get('经营现金流', 0))
        features['应收账款'] = self.validator.to_float(financials.get('应收账款', 0))
        features['存货'] = self.validator.to_float(financials.get('存货', 0))
        
        # 从Excel直接读取的比率指标（如果有）
        # 这些指标在垂直排列的Excel中直接提供，不需要计算
        direct_ratio_indicators = [
            '流动比率', '速动比率', '资产负债率', '现金流负债比',
            'ROE', 'ROA', '销售毛利率', '销售净利率',
            '总资产周转率', '应收账款周转率', '存货周转率',
            '营收增长率', '利润增长率'
        ]
        
        for indicator in direct_ratio_indicators:
            if indicator in financials:
                value = self.validator.to_float(financials[indicator])
                if value is not None:
                    # 对百分比指标进行验证：如果值>1，可能是百分比形式（如18.64），需要转为小数（0.1864）
                    if indicator in ['ROE', 'ROA', '销售毛利率', '销售净利率', '资产负债率', '营收增长率', '利润增长率']:
                        if abs(value) > 1:
                            # 值可能是百分比形式（如18.64表示18.64%），转为小数
                            value = value / 100.0
                            print(f"从Excel读取直接指标 {indicator}: {value} (原始值{financials[indicator]}为百分比形式，已转为小数)")
                        else:
                            print(f"从Excel读取直接指标 {indicator}: {value} (已为小数形式)")
                    else:
                        print(f"从Excel读取直接指标 {indicator}: {value}")
                    features[indicator] = value
        
        # 智能推算缺失的财务数据
        if features['股东权益'] == 0 and features['总资产'] > 0 and features['总负债'] > 0:
            features['股东权益'] = features['总资产'] - features['总负债']
            print(f"智能推算: 股东权益 = 总资产 - 总负债 = {features['股东权益']}")
        
        if features['流动资产'] == 0 and features['总资产'] > 0:
            features['流动资产'] = features['总资产'] * 0.3
            print(f"智能估算: 流动资产 = 总资产 * 0.3 = {features['流动资产']}")
        
        if features['流动负债'] == 0 and features['总负债'] > 0:
            features['流动负债'] = features['总负债'] * 0.4
            print(f"智能估算: 流动负债 = 总负债 * 0.4 = {features['流动负债']}")
        
        if features['经营现金流'] == 0 and features['净利润'] > 0:
            features['经营现金流'] = features['净利润'] * 1.2
            print(f"智能估算: 经营现金流 = 净利润 * 1.2 = {features['经营现金流']}")

        # 2. 市场特征
        market = processed_data.get('市场数据', {})
        features['市值'] = self.validator.to_float(market.get('市值', 0))
        features['股价'] = self.validator.to_float(market.get('股价', 0))
        features['市盈率'] = self.validator.to_float(market.get('市盈率', 0))
        features['市净率'] = self.validator.to_float(market.get('市净率', 0))
        features['换手率'] = self.validator.to_float(market.get('换手率', 0))
        features['波动率'] = self.validator.to_float(market.get('波动率', 0))

        # 3. 经营特征
        business = processed_data.get('经营信息', {})
        features['成立年限'] = self.validator.to_float(business.get('成立年限', 0))
        features['员工人数'] = self.validator.to_float(business.get('员工人数', 0))
        features['管理层稳定性'] = self.validator.to_float(business.get('管理层稳定性', 0.5))
        features['业务多元化'] = self.validator.to_float(business.get('业务多元化', 0.5))
        features['负面新闻数量'] = self.validator.to_float(business.get('负面新闻数量', 0))

        # 4. 计算衍生特征
        features = self._calculate_derived_features(features)

        return features

    def _calculate_derived_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """计算衍生特征 - 优先使用从Excel直接读取的指标值"""
        derived = features.copy()

        # 检查指标是否已直接提供（包括负值情况）
        # 使用 'in' 检查而不是值是否为0，因为指标可能是负数
        # 同时保存原始值，用于后续验证
        directly_provided = {
            '流动比率': '流动比率' in features,
            '资产负债率': '资产负债率' in features,
            'ROE': 'ROE' in features,
            'ROA': 'ROA' in features,
            '毛利率': '毛利率' in features,
            '销售毛利率': '销售毛利率' in features,
            '销售净利率': '销售净利率' in features,
            '应收账款周转率': '应收账款周转率' in features,
            '存货周转率': '存货周转率' in features,
            '总资产周转率': '总资产周转率' in features,
            '营收增长率': '营收增长率' in features,
            '利润增长率': '利润增长率' in features,
            '现金流负债比': '现金流负债比' in features
        }
        
        # 保存用户直接提供的原始值（用于防止验证逻辑错误修正）
        user_provided_values = {
            '总资产周转率': features.get('总资产周转率'),
            '应收账款周转率': features.get('应收账款周转率'),
            '存货周转率': features.get('存货周转率'),
            'ROE': features.get('ROE'),
            'ROA': features.get('ROA'),
            '销售毛利率': features.get('销售毛利率'),
            '销售净利率': features.get('销售净利率'),
            '营收增长率': features.get('营收增长率'),
            '利润增长率': features.get('利润增长率')
        }

        # 偿债能力指标
        if not directly_provided['流动比率']:
            derived['流动比率'] = self.validator.safe_divide(
                features.get('流动资产', 0),
                features.get('流动负债', 0),
                default=0.0
            )
        else:
            print(f"使用Excel提供的流动比率: {features['流动比率']}")

        if not directly_provided['资产负债率']:
            derived['资产负债率'] = self.validator.safe_divide(
                features.get('总负债', 0),
                features.get('总资产', 0),
                default=0.0
            )
        else:
            print(f"使用Excel提供的资产负债率: {features['资产负债率']}")

        derived['产权比率'] = self.validator.safe_divide(
            features.get('总负债', 0),
            features.get('股东权益', 0),
            default=0.0
        )

        # 盈利能力指标
        if not directly_provided['ROE']:
            derived['ROE'] = self.validator.safe_divide(
                features.get('净利润', 0),
                features.get('股东权益', 0),
                default=0.0
            )
        else:
            print(f"使用Excel提供的ROE: {features['ROE']}")

        if not directly_provided['ROA']:
            derived['ROA'] = self.validator.safe_divide(
                features.get('净利润', 0),
                features.get('总资产', 0),
                default=0.0
            )
        else:
            print(f"使用Excel提供的ROA: {features['ROA']}")

        # 处理毛利率指标：如果用户直接提供了销售毛利率，确保derived中也有
        if directly_provided['销售毛利率']:
            derived['销售毛利率'] = features['销售毛利率']
            derived['毛利率'] = features['销售毛利率']  # 同时设置两个名称，保持兼容性
        elif directly_provided['毛利率']:
            derived['毛利率'] = features['毛利率']
            derived['销售毛利率'] = features['毛利率']
        else:
            # 用户没有提供，需要计算
            calculated_margin = self.validator.safe_divide(
                features.get('净利润', 0),
                features.get('营业收入', 0),
                default=0.0
            )
            derived['毛利率'] = calculated_margin
            derived['销售毛利率'] = calculated_margin
        
        # 处理净利率指标：如果用户直接提供了销售净利率，确保derived中也有
        if directly_provided['销售净利率']:
            derived['销售净利率'] = features['销售净利率']
            derived['净利率'] = features['销售净利率']  # 同时设置两个名称，保持兼容性

        # 营运能力指标
        if not directly_provided['应收账款周转率']:
            derived['应收账款周转率'] = self.validator.safe_divide(
                features.get('营业收入', 0),
                features.get('应收账款', 0),
                default=0.0
            )
        else:
            print(f"使用Excel提供的应收账款周转率: {features['应收账款周转率']}")

        if not directly_provided['存货周转率']:
            derived['存货周转率'] = self.validator.safe_divide(
                features.get('营业收入', 0),
                features.get('存货', 0),
                default=0.0
            )
        else:
            print(f"使用Excel提供的存货周转率: {features['存货周转率']}")

        if not directly_provided['总资产周转率']:
            derived['总资产周转率'] = self.validator.safe_divide(
                features.get('营业收入', 0),
                features.get('总资产', 0),
                default=0.0
            )
        else:
            print(f"使用Excel提供的总资产周转率: {features['总资产周转率']}")

        # 成长能力指标
        if not directly_provided['营收增长率']:
            derived['营收增长率'] = self._estimate_growth_rate(features.get('营业收入', 0))
        else:
            print(f"使用Excel提供的营收增长率: {features['营收增长率']}")
            derived['营收增长率'] = features['营收增长率']

        if not directly_provided['利润增长率']:
            derived['利润增长率'] = self._estimate_growth_rate(features.get('净利润', 0))
        else:
            print(f"使用Excel提供的利润增长率: {features['利润增长率']}")
            derived['利润增长率'] = features['利润增长率']

        # 现金流指标
        derived['现金流负债比'] = self.validator.safe_divide(
            features.get('经营现金流', 0),
            features.get('总负债', 0),
            default=0.0
        )

        derived['现金流利润率'] = self.validator.safe_divide(
            features.get('经营现金流', 0),
            features.get('营业收入', 0),
            default=0.0
        )

        # 规模指标（使用对数变换处理大数值）
        total_asset = features.get('总资产', 0)
        revenue = features.get('营业收入', 0)

        if total_asset > 0:
            derived['总资产对数'] = np.log10(float(total_asset)) if total_asset > 0 else 0.0
        else:
            derived['总资产对数'] = 0.0

        if revenue > 0:
            derived['营收对数'] = np.log10(float(revenue)) if revenue > 0 else 0.0
        else:
            derived['营收对数'] = 0.0

        # 风险指标
        derived['是否亏损'] = 1.0 if features.get('净利润', 0) < 0 else 0.0
        derived['高负债标志'] = 1.0 if derived.get('资产负债率', 0) > 0.7 else 0.0
        derived['低流动比率标志'] = 1.0 if derived.get('流动比率', 0) < 1.0 else 0.0

        # 市值相关
        if features.get('市值', 0) > 0 and features.get('净利润', 0) > 0:
            derived['PEG'] = self.validator.safe_divide(
                features.get('市盈率', 0),
                derived.get('利润增长率', 0) * 100,
                default=0.0
            )
        else:
            derived['PEG'] = 0.0

        # 计算市盈率和市净率（如果没有直接提供）
        if features.get('市盈率', 0) == 0 and features.get('市值', 0) > 0 and features.get('净利润', 0) > 0:
            derived['市盈率'] = self.validator.safe_divide(
                features.get('市值', 0),
                features.get('净利润', 0),
                default=0.0
            )
        elif features.get('市盈率', 0) == 0:
            derived['市盈率'] = features.get('市盈率', 0)

        if features.get('市净率', 0) == 0 and features.get('市值', 0) > 0 and features.get('股东权益', 0) > 0:
            derived['市净率'] = self.validator.safe_divide(
                features.get('市值', 0),
                features.get('股东权益', 0),
                default=0.0
            )
        elif features.get('市净率', 0) == 0:
            derived['市净率'] = features.get('市净率', 0)

        # 确保所有基本财务指标都被包含
        # 补充可能缺失的指标（但如果用户直接提供了这些指标，不要覆盖）
        if not directly_provided['ROA']:
            if 'ROA' not in derived or derived['ROA'] == 0:
                derived['ROA'] = self.validator.safe_divide(
                    features.get('净利润', 0),
                    features.get('总资产', 0),
                    default=0.0
                )
        
        # 确保ROE也不被覆盖
        if not directly_provided['ROE']:
            if 'ROE' not in derived or derived['ROE'] == 0:
                derived['ROE'] = self.validator.safe_divide(
                    features.get('净利润', 0),
                    features.get('股东权益', 0),
                    default=0.0
                )

        if '净利率' not in derived:
            derived['净利率'] = self.validator.safe_divide(
                features.get('净利润', 0),
                features.get('营业收入', 0),
                default=0.0
            )

        # 验证所有财务指标在合理范围内
        # 传入用户直接提供的原始值，防止正确的用户数据被错误修正
        derived = self._validate_financial_indicators(derived, user_provided_values)

        return derived

    def _validate_financial_indicators(self, features: Dict[str, float], user_provided: Dict[str, Any] = None) -> Dict[str, float]:
        """验证财务指标在合理范围内，修正异常值
        
        Args:
            features: 财务指标字典
            user_provided: 用户直接提供的原始值字典（这些值不应被自动修正）
        """
        validated = features.copy()
        if user_provided is None:
            user_provided = {}
        
        # 定义各指标的合理范围
        valid_ranges = {
            'ROE': (-2.0, 2.0),  # -200% 到 200%
            'ROA': (-1.0, 1.0),  # -100% 到 100%
            '资产负债率': (0.0, 1.0),  # 0% 到 100%
            '流动比率': (0.0, 50.0),  # 0 到 50
            '速动比率': (0.0, 50.0),
            '总资产周转率': (0.0, 10.0),  # 0 到 10
            '应收账款周转率': (0.0, 100.0),
            '存货周转率': (0.0, 100.0),
            '营收增长率': (-1.0, 5.0),  # -100% 到 500%
            '利润增长率': (-2.0, 10.0),
            '销售毛利率': (-1.0, 1.0),
            '销售净利率': (-1.0, 1.0),
            '现金流负债比': (-1.0, 2.0),
            '市盈率': (0.0, 1000.0),
            '市净率': (0.0, 100.0)
        }
        
        for indicator, (min_val, max_val) in valid_ranges.items():
            if indicator in validated:
                value = validated[indicator]
                
                # 如果这是用户直接提供的值，不进行自动修正（用户数据优先级最高）
                if indicator in user_provided and user_provided[indicator] is not None:
                    original_value = user_provided[indicator]
                    # 用户提供的值是可信的，只进行范围检查，不自动除以100
                    if value < min_val or value > max_val:
                        print(f"警告: {indicator} = {value} 超出合理范围 [{min_val}, {max_val}]")
                        print(f"  但此值为用户直接提供，保留原始值不做自动修正")
                        # 保留原始值，不做修正，继续处理下一个指标
                        continue
                    # 如果在范围内，也不做处理，继续下一个
                    continue
                
                if value < min_val or value > max_val:
                    print(f"警告: {indicator} = {value} 超出合理范围 [{min_val}, {max_val}]，尝试修正")
                    # 如果值过大，可能是百分比形式未转换（如50.9而不是0.509）
                    if value > max_val and value <= max_val * 100:
                        # 可能是百分比形式，除以100
                        corrected = value / 100.0
                        if min_val <= corrected <= max_val:
                            validated[indicator] = corrected
                            print(f"  修正为: {corrected} (除以100)")
                            continue
                    # 如果值仍然异常，标记为需要重新计算
                    validated[indicator] = 0.0
                    print(f"  标记为异常，将重新计算")
        
        return validated

    def _estimate_growth_rate(self, value: float) -> float:
        """估计增长率（基于数值大小估算）"""
        if value <= 0:
            return 0.0

        # 使用对数变换模拟增长率
        try:
            log_value = np.log10(float(value))
            if log_value > 8:  # 大型企业
                return 0.1
            elif log_value > 6:  # 中型企业
                return 0.15
            elif log_value > 4:  # 小型企业
                return 0.2
            else:
                return 0.25
        except (ValueError, TypeError):
            return 0.0

    def _calculate_credit_indicators(self, processed_data: Dict[str, Any]) -> Dict[str, float]:
        """计算信用评估指标"""
        indicators = {}
        features = processed_data.get('特征', {})
        industry = processed_data.get('行业分类', '制造业')

        # 获取行业基准
        benchmark = self.industry_benchmarks.get(industry, self._get_default_benchmarks().get(industry, {}))

        # 1. 财务健康度评分 (0-100)
        indicators['财务健康度'] = self._calculate_financial_health_score(features, benchmark)

        # 2. 行业地位评分 (0-100)
        indicators['行业地位'] = self._calculate_industry_position_score(features, benchmark)

        # 3. 市场表现评分 (0-100)
        indicators['市场表现'] = self._calculate_market_performance_score(features)

        # 4. 经营质量评分 (0-100)
        indicators['经营质量'] = self._calculate_business_quality_score(features)

        # 5. 合规风险评分 (0-100)
        indicators['合规风险'] = self._calculate_compliance_risk_score(features)

        # 综合信用评分 (加权平均)
        weights = {
            '财务健康度': 0.35,
            '行业地位': 0.20,
            '市场表现': 0.20,
            '经营质量': 0.15,
            '合规风险': 0.10
        }

        total_score = sum(indicators[key] * weights[key] for key in weights)
        indicators['综合信用评分'] = round(total_score, 2)

        # 风险等级
        indicators['风险等级'] = self._get_risk_level(total_score)

        return indicators

    def _calculate_industry_comparison(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算与行业平均的对比 - 扩展更多指标"""
        features = processed_data.get('特征', {})
        industry = processed_data.get('行业分类', '制造业')
        benchmark = self.industry_benchmarks.get(industry, {})
        
        # 计算净利润率
        net_profit_margin = self.validator.safe_divide(
            features.get('净利润', 0),
            features.get('营业收入', 0),
            default=0.0
        )

        comparison = {
            '行业分类': industry,
            '公司指标': {
                '资产负债率': round(features.get('资产负债率', 0), 4),
                '净利润率': round(net_profit_margin, 4),
                '总资产周转率': round(features.get('总资产周转率', 0), 4),
                '市盈率': round(features.get('市盈率', 0), 4),
                'ROE': round(features.get('ROE', 0), 4),
                'ROA': round(features.get('ROA', 0), 4),
                '流动比率': round(features.get('流动比率', 0), 4),
                '营收增长率': round(features.get('营收增长率', 0), 4)
            },
            '行业平均': {
                '资产负债率': round(benchmark.get('平均资产负债率', 0), 4),
                '净利润率': round(benchmark.get('平均净利润率', 0), 4),
                '总资产周转率': round(benchmark.get('平均总资产周转率', 0), 4),
                '市盈率': round(benchmark.get('平均市盈率', 0), 4),
                'ROE': round(benchmark.get('平均ROE', 0), 4),
                'ROA': round(benchmark.get('平均ROA', 0), 4),
                '流动比率': round(benchmark.get('平均流动比率', 0), 4),
                '营收增长率': round(benchmark.get('平均营收增长率', 0), 4)
            },
            '对比结果': {}
        }

        # 计算对比结果 - 扩展更多指标
        indicators = ['资产负债率', '净利润率', '总资产周转率', '市盈率', 'ROE', 'ROA', '流动比率', '营收增长率']
        for indicator in indicators:
            company_val = comparison['公司指标'][indicator]
            industry_val = comparison['行业平均'][indicator]
            
            # 处理行业基准为0的情况
            if industry_val == 0:
                if company_val > 0:
                    comparison['对比结果'][indicator] = '优于行业平均（行业基准为0）'
                else:
                    comparison['对比结果'][indicator] = '与行业平均持平'
                continue
            
            if indicator in ['资产负债率']:
                # 资产负债率越低越好
                if company_val < industry_val * 0.9:
                    comparison['对比结果'][indicator] = '显著优于行业平均'
                elif company_val < industry_val:
                    comparison['对比结果'][indicator] = '优于行业平均'
                elif company_val < industry_val * 1.1:
                    comparison['对比结果'][indicator] = '接近行业平均'
                else:
                    comparison['对比结果'][indicator] = '劣于行业平均'
            elif indicator in ['市盈率']:
                # 市盈率适中最好
                if industry_val * 0.8 <= company_val <= industry_val * 1.2:
                    comparison['对比结果'][indicator] = '估值合理'
                elif company_val < industry_val * 0.8:
                    comparison['对比结果'][indicator] = '估值偏低（可能被低估）'
                else:
                    comparison['对比结果'][indicator] = '估值偏高（可能被高估）'
            else:
                # 其他指标越高越好
                if company_val > industry_val * 1.1:
                    comparison['对比结果'][indicator] = '显著优于行业平均'
                elif company_val > industry_val:
                    comparison['对比结果'][indicator] = '优于行业平均'
                elif company_val > industry_val * 0.9:
                    comparison['对比结果'][indicator] = '接近行业平均'
                else:
                    comparison['对比结果'][indicator] = '劣于行业平均'

        return comparison

    def _calculate_financial_health_score(self, features: Dict[str, float], benchmark: Dict[str, float]) -> float:
        """计算财务健康度评分"""
        score = 50  # 基础分

        # 偿债能力 (30分)
        current_ratio = features.get('流动比率', 0)
        if current_ratio > 2:
            score += 15
        elif current_ratio > 1.5:
            score += 10
        elif current_ratio > 1:
            score += 5

        debt_ratio = features.get('资产负债率', 0)
        industry_debt = benchmark.get('平均资产负债率', 0.6)
        if debt_ratio < industry_debt * 0.8:
            score += 15
        elif debt_ratio < industry_debt:
            score += 10
        elif debt_ratio < industry_debt * 1.2:
            score += 5
        else:
            score -= 10

        # 盈利能力 (30分)
        roe = features.get('ROE', 0)
        industry_roe = benchmark.get('平均ROE', 0.12) or 0.12
        if roe > industry_roe * 1.2:
            score += 15
        elif roe > industry_roe:
            score += 10
        elif roe > 0:
            score += 5
        else:
            score -= 10

        # 营运能力 (20分)
        asset_turnover = features.get('总资产周转率', 0)
        industry_turnover = benchmark.get('平均总资产周转率', 0.8) or 0.8
        if asset_turnover > industry_turnover * 1.2:
            score += 10
        elif asset_turnover > industry_turnover:
            score += 5

        # 现金流 (20分)
        cash_flow_ratio = features.get('现金流负债比', 0)
        if cash_flow_ratio > 0.2:
            score += 10
        elif cash_flow_ratio > 0.1:
            score += 5
        elif cash_flow_ratio > 0:
            score += 2

        return min(100.0, max(0.0, score))

    def _calculate_industry_position_score(self, features: Dict[str, float], benchmark: Dict[str, float]) -> float:
        """计算行业地位评分"""
        score = 50  # 基础分

        # 营收规模 (30分)
        revenue_log = features.get('营收对数', 0)
        if revenue_log > 10:
            score += 15
        elif revenue_log > 8:
            score += 10
        elif revenue_log > 6:
            score += 5

        # 市场份额（用营收规模代理）(20分)
        if revenue_log > 9:
            score += 10
        elif revenue_log > 7:
            score += 5

        # 盈利能力 (30分)
        net_margin = features.get('毛利率', 0)
        industry_margin = benchmark.get('平均净利润率', 0.1) or 0.1
        if net_margin > industry_margin * 1.2:
            score += 15
        elif net_margin > industry_margin:
            score += 10
        elif net_margin > 0:
            score += 5

        # 成长能力 (20分)
        growth_rate = features.get('营收增长率', 0)
        if growth_rate > 0.2:
            score += 10
        elif growth_rate > 0.1:
            score += 5
        elif growth_rate > 0:
            score += 2

        return min(100.0, max(0.0, score))

    def _calculate_market_performance_score(self, features: Dict[str, float]) -> float:
        """计算市场表现评分"""
        score = 50  # 基础分

        # 市盈率 (25分)
        pe = features.get('市盈率', 0)
        if pe > 0 and pe < 20:
            score += 15
        elif pe >= 20 and pe < 30:
            score += 10
        elif pe >= 30 and pe < 40:
            score += 5

        # 市值规模 (25分)
        market_cap = features.get('市值', 0)
        if market_cap > 1000000:
            score += 15
        elif market_cap > 100000:
            score += 10
        elif market_cap > 10000:
            score += 5

        # 波动率 (25分)
        volatility = features.get('波动率', 0)
        if volatility < 0.2:
            score += 15
        elif volatility < 0.4:
            score += 10
        elif volatility < 0.6:
            score += 5

        # 换手率 (25分)
        turnover = features.get('换手率', 0)
        if turnover > 0.01 and turnover < 0.1:
            score += 15
        elif turnover >= 0.1 and turnover < 0.2:
            score += 10
        elif turnover >= 0.2 and turnover < 0.3:
            score += 5

        return min(100.0, max(0.0, score))

    def _calculate_business_quality_score(self, features: Dict[str, float]) -> float:
        """计算经营质量评分"""
        score = 50  # 基础分

        # 管理层稳定性 (20分)
        mgmt_stability = features.get('管理层稳定性', 0.5)
        score += mgmt_stability * 20

        # 业务多元化 (20分)
        diversification = features.get('业务多元化', 0.5)
        score += diversification * 20

        # 成立年限 (20分)
        years = features.get('成立年限', 0)
        if years > 20:
            score += 20
        elif years > 10:
            score += 15
        elif years > 5:
            score += 10
        elif years > 2:
            score += 5

        # 员工规模 (20分)
        employees = features.get('员工人数', 0)
        if employees > 1000:
            score += 20
        elif employees > 500:
            score += 15
        elif employees > 100:
            score += 10
        elif employees > 10:
            score += 5

        # 研发投入 (20分)
        rd_ratio = features.get('研发投入占比', 0)
        if rd_ratio > 0.1:
            score += 20
        elif rd_ratio > 0.05:
            score += 15
        elif rd_ratio > 0.02:
            score += 10
        elif rd_ratio > 0:
            score += 5

        return min(100.0, max(0.0, score))

    def _calculate_compliance_risk_score(self, features: Dict[str, float]) -> float:
        """计算合规风险评分"""
        score = 100  # 基础分

        # 负面新闻 (扣分)
        negative_news = features.get('负面新闻数量', 0)
        if negative_news > 5:
            score -= 30
        elif negative_news > 2:
            score -= 20
        elif negative_news > 0:
            score -= 10

        # 亏损 (扣分)
        is_loss = features.get('是否亏损', 0)
        if is_loss == 1:
            score -= 20

        # 高负债 (扣分)
        high_debt = features.get('高负债标志', 0)
        if high_debt == 1:
            score -= 15

        # 低流动比率 (扣分)
        low_current_ratio = features.get('低流动比率标志', 0)
        if low_current_ratio == 1:
            score -= 15

        return min(100.0, max(0.0, score))

    def _get_risk_level(self, score: float) -> str:
        """根据评分获取风险等级"""
        if score >= 85:
            return 'AAA'
        elif score >= 75:
            return 'AA'
        elif score >= 65:
            return 'A'
        elif score >= 55:
            return 'BBB'
        elif score >= 45:
            return 'BB'
        else:
            return 'B及以下'
