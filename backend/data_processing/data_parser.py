"""
数据解析模块 - 智能识别和提取财务数据
"""

import os
import re
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import pdfplumber
from bs4 import BeautifulSoup
import sys

# 添加当前目录到路径以支持相对导入
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from data_validator import DataValidator
except ImportError:
    # 如果相对导入失败，使用绝对导入
    from backend.data_processing.data_validator import DataValidator

class DataParser:
    """数据解析器 - 智能识别和提取财务数据"""

    def __init__(self):
        self.validator = DataValidator()
        # 扩展的财务指标关键词映射 - 包含更多变体和常见写法
        self.financial_keywords = {
            '营业收入': ['营业收入', '主营业务收入', '营业总收入', '销售收入', 'Revenue', 'Sales', '营收', '收入', '营业额'],
            '净利润': ['净利润', '归属于母公司股东的净利润', 'Net Profit', 'Net Income', '净利', '利润', '净收益'],
            '总资产': ['总资产', '资产总计', '资产总额', 'Total Assets', '资产', '资产合计'],
            '总负债': ['总负债', '负债合计', '负债总计', 'Total Liabilities', '负债', '负债总额'],
            '流动资产': ['流动资产', 'Current Assets', '流动资', '流动资产合计'],
            '流动负债': ['流动负债', 'Current Liabilities', '流动负', '流动负债合计'],
            '股东权益': ['股东权益', '所有者权益', 'Equity', '权益', '净资产', '股东权益合计'],
            '经营现金流': ['经营现金流', '经营活动现金流量', 'Operating Cash Flow', '现金流', '经营活动现金流', '经营现金'],
            '应收账款': ['应收账款', '应收款项', 'Accounts Receivable', '应收', '应收账款净额'],
            '存货': ['存货', '库存', 'Inventory', '库存商品', '存货净额']
        }
        
        # 市场数据关键词
        self.market_keywords = {
            '市值': ['市值', 'Market Cap', 'Market Capitalization', '市值规模', '总市值'],
            '股价': ['股价', '收盘价', 'Stock Price', 'Close Price', '价格', '当前股价'],
            '市盈率': ['市盈率', 'PE', 'Price Earnings Ratio', 'PE Ratio', 'P/E'],
            '市净率': ['市净率', 'PB', 'Price Book Ratio', 'PB Ratio', 'P/B'],
            '市销率': ['市销率', 'PS', 'Price Sales Ratio', 'PS Ratio', 'P/S'],
            '换手率': ['换手率', 'Turnover Rate', 'Turnover'],
            '波动率': ['波动率', 'Volatility', '波动']
        }
        
        # 经营信息关键词
        self.business_keywords = {
            '成立年限': ['成立年限', '成立时间', 'Established', '创立时间', '成立日期'],
            '员工人数': ['员工人数', '员工总数', 'Employees', '职工人数', '人员数量'],
            '管理层稳定性': ['管理层稳定性', '管理层变动', 'Management Stability'],
            '业务多元化': ['业务多元化', '多元化程度', 'Business Diversification'],
            '负面新闻数量': ['负面新闻数量', '负面报道', 'Negative News']
        }
        
        # 直接指标映射（用于垂直排列的Excel，第一列是指标名，第二列是数值）
        self.direct_indicator_map = {
            # 基础财务指标
            '总资产': ['总资产', '资产总计', '资产总额', 'Total Assets'],
            '总负债': ['总负债', '负债合计', '负债总计', 'Total Liabilities'],
            '流动资产': ['流动资产', 'Current Assets'],
            '流动负债': ['流动负债', 'Current Liabilities'],
            '股东权益': ['股东权益', '所有者权益', 'Equity', '净资产'],
            '营业收入': ['营业收入', '主营业务收入', '营业总收入', 'Revenue', 'Sales'],
            '营业成本': ['营业成本', '主营业务成本', 'Cost of Revenue'],
            '净利润': ['净利润', 'Net Profit', 'Net Income'],
            '经营现金流': ['经营现金流', '经营活动现金流量', 'Operating Cash Flow'],
            '应收账款': ['应收账款', '应收款项', 'Accounts Receivable'],
            '存货': ['存货', '库存', 'Inventory'],
            '市值': ['市值', 'Market Cap', '总市值'],
            # 上期数据（用于计算增长率，不应覆盖本期数据）
            '上期营收': ['上期营收', '上期营业收入', '上年营收', '上年营业收入'],
            '上期净利润': ['上期净利润', '上年净利润', '上期净利'],
            # 比率指标
            '流动比率': ['流动比率', 'Current Ratio'],
            '速动比率': ['速动比率', 'Quick Ratio'],
            '资产负债率': ['资产负债率', 'Debt to Asset Ratio', '负债率'],
            '现金流负债比': ['现金流负债比', 'Cash Flow to Debt'],
            'ROE': ['ROE', '净资产收益率', 'Return on Equity'],
            'ROA': ['ROA', '总资产收益率', 'Return on Assets'],
            '销售毛利率': ['销售毛利率', 'Gross Margin', '毛利率'],
            '销售净利率': ['销售净利率', 'Net Margin', '净利率'],
            '总资产周转率': ['总资产周转率', 'Total Asset Turnover'],
            '应收账款周转率': ['应收账款周转率', 'Receivables Turnover'],
            '存货周转率': ['存货周转率', 'Inventory Turnover'],
            '营收增长率': ['营收增长率', 'Revenue Growth', '收入增长率'],
            '利润增长率': ['利润增长率', 'Profit Growth'],
            '市盈率': ['市盈率', 'PE', 'P/E'],
            '市净率': ['市净率', 'PB', 'P/B'],
            '市销率': ['市销率', 'PS', 'P/S']
        }

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """解析不同格式的财报文件"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # 支持常见的财务报表文件格式
        supported_extensions = ['.pdf', '.xlsx', '.xls', '.html', '.csv', '.txt', '.xltx', '.xlt', '.ods']
        if file_extension not in supported_extensions:
            raise ValueError(f"不支持的文件格式: {file_extension}，支持格式: {', '.join(supported_extensions)}")
        
        print(f"正在解析文件，扩展名: {file_extension}")
        
        # 根据文件扩展名选择解析方法
        try:
            if file_extension in ['.pdf']:
                return self._parse_pdf(file_path)
            elif file_extension in ['.xlsx', '.xls', '.xltx', '.xlt', '.ods']:
                return self._parse_excel(file_path)
            elif file_extension in ['.html']:
                return self._parse_html(file_path)
            elif file_extension in ['.csv']:
                return self._parse_csv(file_path)
            elif file_extension in ['.txt']:
                return self._parse_txt(file_path)
            else:
                # 对于未知格式，尝试先用Excel解析，再尝试文本解析
                print(f"尝试用Excel方法解析: {file_extension}")
                try:
                    return self._parse_excel(file_path)
                except:
                    print(f"尝试用文本方法解析: {file_extension}")
                    return self._parse_txt(file_path)
        except Exception as e:
            print(f"文件解析失败: {e}")
            import traceback
            traceback.print_exc()
            # 返回空数据结构，但不报错
            return {
                '财务指标': {},
                '市场数据': {},
                '经营信息': {}
            }
    
    def _parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """解析PDF文件"""
        data = {
            '财务指标': {},
            '市场数据': {},
            '经营信息': {}
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() + '\n'
                
            # 提取财务指标
            data['财务指标'] = self._extract_financial_data_from_text(text)
            # 提取市场数据
            data['市场数据'] = self._extract_market_data_from_text(text)
            # 提取经营信息
            data['经营信息'] = self._extract_business_info_from_text(text)
            
        except Exception as e:
            print(f"PDF解析失败: {e}")
        
        return data
    
    def _parse_excel(self, excel_path: str) -> Dict[str, Any]:
        """解析Excel文件 - 智能识别表格结构"""
        data = {
            '财务指标': {},
            '市场数据': {},
            '经营信息': {}
        }
        
        try:
            print(f"开始读取Excel文件: {excel_path}")
            
            # 尝试不同的Excel引擎
            engines = ['openpyxl', 'xlrd', None]
            
            for engine in engines:
                try:
                    print(f"尝试使用引擎: {engine}")
                    
                    # 读取所有工作表
                    xl = pd.ExcelFile(excel_path, engine=engine)
                    print(f"工作表数量: {len(xl.sheet_names)}")
                    
                    # 遍历所有工作表
                    for sheet_name in xl.sheet_names:
                        print(f"正在解析工作表: {sheet_name}")
                        
                        # 尝试多种方式读取工作表
                        for try_method in range(3):
                            try:
                                if try_method == 0:
                                    # 标准读取
                                    df = pd.read_excel(xl, sheet_name, engine=engine)
                                elif try_method == 1:
                                    # 不将第一行作为表头
                                    df = pd.read_excel(xl, sheet_name, header=None, engine=engine)
                                else:
                                    # 跳过前几行尝试
                                    try:
                                        test_df = pd.read_excel(xl, sheet_name, nrows=10, engine=engine)
                                        df = pd.read_excel(xl, sheet_name, header=None, skiprows=min(5, len(test_df)), engine=engine)
                                    except:
                                        continue
                                
                                print(f"工作表 {sheet_name} 形状: {df.shape}")
                                
                                # 智能提取数据
                                sheet_data = self._smart_extract_from_dataframe(df)
                                
                                # 合并数据 - 垂直解析(method4)的结果优先级高于单元格搜索(method2)
                                # 所以这里先暂存，等所有方法尝试完后再合并
                                for key, value in sheet_data['财务指标'].items():
                                    if key not in data['财务指标']:
                                        data['财务指标'][key] = value
                                    elif value != 0 and data['财务指标'].get(key) == 0:
                                        data['财务指标'][key] = value
                                
                                for key, value in sheet_data['市场数据'].items():
                                    if key not in data['市场数据']:
                                        data['市场数据'][key] = value
                                    elif value != 0 and data['市场数据'].get(key) == 0:
                                        data['市场数据'][key] = value
                                
                                for key, value in sheet_data['经营信息'].items():
                                    if key not in data['经营信息']:
                                        data['经营信息'][key] = value
                                    elif value != 0 and data['经营信息'].get(key) == 0:
                                        data['经营信息'][key] = value
                                
                                # 如果已经提取到数据，停止尝试其他方法
                                if len(data['财务指标']) > 0 or len(data['市场数据']) > 0 or len(data['经营信息']) > 0:
                                    break
                                
                            except Exception as sheet_error:
                                print(f"工作表 {sheet_name} 第 {try_method} 种方法解析失败: {sheet_error}")
                                continue
                        
                        # 如果找到数据，停止尝试其他引擎
                        if len(data['财务指标']) > 3:
                            print(f"成功提取数据，当前引擎: {engine}")
                            break
                    
                except Exception as engine_error:
                    print(f"引擎 {engine} 失败: {engine_error}")
                    continue
            
            # 如果上面都没找到数据，尝试直接用pandas读取所有sheet
            if len(data['财务指标']) == 0:
                print("尝试直接读取所有工作表...")
                try:
                    # 尝试不带引擎参数
                    all_dfs = pd.read_excel(excel_path, sheet_name=None, header=None)
                    for sheet_name, df in all_dfs.items():
                        sheet_data = self._smart_extract_from_dataframe(df)
                        for key, value in sheet_data['财务指标'].items():
                            if key not in data['财务指标'] or value != 0:
                                data['财务指标'][key] = value
                        for key, value in sheet_data['市场数据'].items():
                            if key not in data['市场数据'] or value != 0:
                                data['市场数据'][key] = value
                        for key, value in sheet_data['经营信息'].items():
                            if key not in data['经营信息'] or value != 0:
                                data['经营信息'][key] = value
                except Exception as last_error:
                    print(f"最后的备用方法也失败: {last_error}")
            
            print(f"最终解析到的数据 - 财务指标: {list(data['财务指标'].keys())}")
            
        except Exception as e:
            print(f"Excel解析失败: {e}")
            import traceback
            traceback.print_exc()
        
        return data
    
    def _smart_extract_from_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """智能从DataFrame中提取数据"""
        result = {
            '财务指标': {},
            '市场数据': {},
            '经营信息': {}
        }
        
        try:
            # 首先清理数据，处理缺失值
            df = df.fillna('')
            
            # 方法1: 直接匹配列名
            print("尝试方法1：列名匹配")
            for col in df.columns:
                col_str = str(col).strip().lower()
                
                # 检查财务指标
                for indicator, keywords in self.financial_keywords.items():
                    if any(keyword.lower() in col_str for keyword in keywords):
                        # 获取该列的数值
                        value = self._get_first_numeric_value(df[col])
                        if value is not None:
                            result['财务指标'][indicator] = value
                            print(f"找到财务指标 {indicator} = {value}")
                
                # 检查市场数据
                for indicator, keywords in self.market_keywords.items():
                    if any(keyword.lower() in col_str for keyword in keywords):
                        value = self._get_first_numeric_value(df[col])
                        if value is not None:
                            result['市场数据'][indicator] = value
                
                # 检查经营信息
                for indicator, keywords in self.business_keywords.items():
                    if any(keyword.lower() in col_str for keyword in keywords):
                        value = self._get_first_numeric_value(df[col])
                        if value is not None:
                            result['经营信息'][indicator] = value
            
            # 如果方法1找到数据，直接返回
            if len(result['财务指标']) > 3:
                print(f"方法1成功，找到 {len(result['财务指标'])} 个财务指标")
                return result
            
            # 方法2: 遍历所有单元格寻找关键词
            print("尝试方法2：单元格搜索")
            max_rows = min(200, len(df))
            max_cols = min(100, len(df.columns))
            
            for i in range(max_rows):
                for j in range(max_cols):
                    try:
                        cell_value = str(df.iloc[i, j]).strip().lower()
                        
                        if len(cell_value) < 2:
                            continue
                        
                        # 检查财务指标
                        for indicator, keywords in self.financial_keywords.items():
                            if any(keyword.lower() in cell_value for keyword in keywords):
                                if indicator not in result['财务指标']:
                                    value = self._get_adjacent_value(df, i, j)
                                    if value is not None:
                                        result['财务指标'][indicator] = value
                                        print(f"单元格搜索找到 {indicator} = {value}")
                        
                        # 检查市场数据
                        for indicator, keywords in self.market_keywords.items():
                            if any(keyword.lower() in cell_value for keyword in keywords):
                                if indicator not in result['市场数据']:
                                    value = self._get_adjacent_value(df, i, j)
                                    if value is not None:
                                        result['市场数据'][indicator] = value
                        
                        # 检查经营信息
                        for indicator, keywords in self.business_keywords.items():
                            if any(keyword.lower() in cell_value for keyword in keywords):
                                if indicator not in result['经营信息']:
                                    value = self._get_adjacent_value(df, i, j)
                                    if value is not None:
                                        result['经营信息'][indicator] = value
                    except:
                        continue
                
                # 如果已经找到足够数据，提前退出
                if len(result['财务指标']) > 5:
                    break
            
            # 方法3: 尝试将第一行作为表头重新解析
            if len(result['财务指标']) < 2 and len(df) > 3:
                print("尝试方法3：重设表头")
                try:
                    # 尝试多种可能的表头位置
                    for header_row in range(min(5, len(df)-1)):
                        new_df = df.iloc[header_row+1:].copy()
                        new_df.columns = df.iloc[header_row].astype(str).values
                        method3_result = self._smart_extract_from_dataframe(new_df)
                        
                        # 如果找到更多数据，更新结果
                        if len(method3_result['财务指标']) > len(result['财务指标']):
                            result['财务指标'].update(method3_result['财务指标'])
                        if len(method3_result['市场数据']) > len(result['市场数据']):
                            result['市场数据'].update(method3_result['市场数据'])
                        if len(method3_result['经营信息']) > len(result['经营信息']):
                            result['经营信息'].update(method3_result['经营信息'])
                except Exception as e:
                    print(f"方法3失败: {e}")
            
            # 方法4: 专门针对垂直排列的Excel（第一列指标名，第二列数值）
            # 总是尝试垂直排列解析，以获取更完整的指标（如ROE、ROA等比率指标）
            print("尝试方法4：垂直排列解析（第一列指标名，第二列数值）")
            try:
                vertical_data = self._extract_vertical_data(df)
                if vertical_data:
                    # 合并垂直解析结果（垂直解析结果优先级最高，因为它更精确）
                    for key, value in vertical_data['财务指标'].items():
                        # 垂直解析结果直接覆盖之前的结果（即使之前的值不为0）
                        # 因为垂直解析是精确匹配，比单元格搜索更可靠
                        result['财务指标'][key] = value
                        print(f"垂直解析覆盖财务指标 {key} = {value}")
                    for key, value in vertical_data['市场数据'].items():
                        result['市场数据'][key] = value
                        print(f"垂直解析覆盖市场数据 {key} = {value}")
                    for key, value in vertical_data['经营信息'].items():
                        result['经营信息'][key] = value
                        print(f"垂直解析覆盖经营信息 {key} = {value}")
                    print(f"垂直排列解析成功，找到 {len(vertical_data['财务指标'])} 个财务指标")
            except Exception as e:
                print(f"方法4失败: {e}")
        
        except Exception as e:
            print(f"智能提取失败: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"最终提取结果: 财务指标 {len(result['财务指标'])} 个")
        return result
    
    def _extract_vertical_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        专门解析垂直排列的数据（第一列是指标名，第二列是数值）
        适用于用户提供的Excel格式
        """
        result = {
            '财务指标': {},
            '市场数据': {},
            '经营信息': {}
        }
        
        try:
            # 确保至少有2列
            if len(df.columns) < 2:
                print("垂直解析：列数不足")
                return result
            
            # 遍历每一行
            for i in range(len(df)):
                try:
                    # 获取第一列的值（指标名）
                    indicator_name = str(df.iloc[i, 0]).strip()
                    
                    # 跳过空行和标题行
                    if not indicator_name or indicator_name.lower() in ['nan', 'none', '']:
                        continue
                    
                    # 获取第二列的值（数值）
                    value_cell = df.iloc[i, 1]
                    
                    # 尝试转换为数值
                    value = self.validator.to_float(value_cell)
                    if value is None or pd.isna(value):
                        continue
                    
                    # 检测单位并转换
                    unit_multiplier = self._detect_unit_multiplier(indicator_name)
                    converted_value = value * unit_multiplier
                    
                    # 对百分比指标进行智能判断：如果值已经很小（<1），可能已经是小数形式，不再转换
                    if unit_multiplier == 0.01 and abs(value) < 1:
                        # 值已经可能是小数形式（如0.1864表示18.64%），不再转换
                        converted_value = value
                        print(f"  百分比指标{indicator_name}的值{value}已为小数形式，不再转换")
                    
                    # 清理指标名称（去除单位等）
                    clean_name = self._clean_indicator_name(indicator_name)
                    
                    # 在直接指标映射中查找匹配
                    matched = False
                    
                    # 首先检查是否是上期数据（避免上期数据被匹配到本期指标）
                    if '上期' in clean_name or '上年' in clean_name:
                        # 上期数据特殊处理
                        if '营收' in clean_name or '收入' in clean_name or '营业' in clean_name:
                            result['财务指标']['上期营收'] = converted_value
                            print(f"垂直解析找到上期数据 上期营收 = {converted_value} (原始: {indicator_name}={value}, 单位倍数: {unit_multiplier})")
                            matched = True
                        elif '净利' in clean_name:
                            result['财务指标']['上期净利润'] = converted_value
                            print(f"垂直解析找到上期数据 上期净利润 = {converted_value} (原始: {indicator_name}={value}, 单位倍数: {unit_multiplier})")
                            matched = True
                    
                    if not matched:
                        for standard_name, keywords in self.direct_indicator_map.items():
                            # 使用更精确的匹配：清理后的名称必须包含关键词，且要避免部分匹配
                            # 例如"总资产周转率"不应该匹配"总资产"
                            if any(keyword in clean_name for keyword in keywords):
                                # 特殊处理：避免"周转率"指标被匹配到基础财务指标
                                if standard_name in ['总资产', '应收账款', '存货']:
                                    if '周转率' in clean_name:
                                        # 如果清理后的名称包含"周转率"，则跳过基础指标匹配
                                        continue
                                
                                # 判断属于哪一类
                                if standard_name in ['总资产', '总负债', '流动资产', '流动负债', 
                                                      '股东权益', '营业收入', '营业成本', '净利润',
                                                      '经营现金流', '应收账款', '存货']:
                                    result['财务指标'][standard_name] = converted_value
                                    print(f"垂直解析找到财务指标 {standard_name} = {converted_value} (原始: {indicator_name}={value}, 单位倍数: {unit_multiplier})")
                                elif standard_name in ['上期营收', '上期净利润']:
                                    # 上期数据单独存储，不覆盖本期数据
                                    result['财务指标'][standard_name] = converted_value
                                    print(f"垂直解析找到上期数据 {standard_name} = {converted_value} (原始: {indicator_name}={value}, 单位倍数: {unit_multiplier})")
                                elif standard_name in ['流动比率', '速动比率', '资产负债率', '现金流负债比',
                                                       'ROE', 'ROA', '销售毛利率', '销售净利率',
                                                       '总资产周转率', '应收账款周转率', '存货周转率',
                                                       '营收增长率', '利润增长率']:
                                    result['财务指标'][standard_name] = converted_value
                                    print(f"垂直解析找到比率指标 {standard_name} = {converted_value} (原始: {indicator_name}={value})")
                                elif standard_name in ['市值', '市盈率', '市净率', '市销率']:
                                    result['市场数据'][standard_name] = converted_value
                                    print(f"垂直解析找到市场数据 {standard_name} = {converted_value} (原始: {indicator_name}={value}, 单位倍数: {unit_multiplier})")
                                matched = True
                                break
                    
                    # 如果没有匹配到，尝试在关键词映射中查找
                    if not matched:
                        # 检查财务指标关键词
                        for indicator, keywords in self.financial_keywords.items():
                            if any(keyword in clean_name for keyword in keywords):
                                # 特殊处理：避免"上期营收"被匹配到"营业收入"
                                if indicator == '营业收入' and ('上期' in clean_name or '上年' in clean_name):
                                    # 将上期营收存储为单独字段，不覆盖本期营业收入
                                    result['财务指标']['上期营收'] = converted_value
                                    print(f"垂直解析(关键词)找到上期数据 上期营收 = {converted_value} (原始: {indicator_name}={value})")
                                    matched = True
                                    break
                                # 特殊处理：避免"上期净利润"被匹配到"净利润"
                                if indicator == '净利润' and ('上期' in clean_name or '上年' in clean_name):
                                    result['财务指标']['上期净利润'] = converted_value
                                    print(f"垂直解析(关键词)找到上期数据 上期净利润 = {converted_value} (原始: {indicator_name}={value})")
                                    matched = True
                                    break
                                result['财务指标'][indicator] = converted_value
                                print(f"垂直解析(关键词)找到财务指标 {indicator} = {converted_value} (原始: {indicator_name}={value}, 单位倍数: {unit_multiplier})")
                                matched = True
                                break
                        
                        if not matched:
                            # 检查市场数据关键词
                            for indicator, keywords in self.market_keywords.items():
                                if any(keyword in clean_name for keyword in keywords):
                                    result['市场数据'][indicator] = converted_value
                                    print(f"垂直解析(关键词)找到市场数据 {indicator} = {converted_value} (原始: {indicator_name}={value}, 单位倍数: {unit_multiplier})")
                                    matched = True
                                    break
                        
                        if not matched:
                            # 检查经营信息关键词
                            for indicator, keywords in self.business_keywords.items():
                                if any(keyword in clean_name for keyword in keywords):
                                    result['经营信息'][indicator] = converted_value
                                    print(f"垂直解析(关键词)找到经营信息 {indicator} = {converted_value} (原始: {indicator_name}={value})")
                                    matched = True
                                    break
                
                except Exception as e:
                    print(f"垂直解析行 {i} 失败: {e}")
                    continue
            
        except Exception as e:
            print(f"垂直排列解析失败: {e}")
            import traceback
            traceback.print_exc()
        
        return result
    
    def _detect_unit_multiplier(self, name: str) -> float:
        """检测指标名称中的单位，返回转换倍数（统一为亿元，保持数值直观）"""
        import re
        name = str(name)
        
        # 检查是否包含亿元 - 保持原数值不变
        if re.search(r'亿元', name):
            return 1  # 已经是亿元，保持不变
        
        # 检查是否包含亿（但没有元）
        if re.search(r'亿', name) and not re.search(r'亿元', name):
            return 1  # 假设是亿元
        
        # 检查是否包含万元
        if re.search(r'万元', name):
            return 0.0001  # 1万元 = 0.0001亿元
        
        # 检查是否包含万（但没有元）
        if re.search(r'万', name) and not re.search(r'万元', name):
            return 0.0001  # 假设是万元
        
        # 检查是否包含元（没有万或亿）
        if re.search(r'(?<![万亿])元', name):
            return 0.00000001  # 1元 = 0.00000001亿元
        
        # 百分比指标需要除以100转为小数
        if re.search(r'%|％|百分比', name):
            return 0.01  # 5.09% = 0.0509
        
        # 比率指标（如周转率、流动比率）不需要转换
        if re.search(r'周转率', name):
            return 1
        
        # 纯比率指标（名称以率结尾但不含%）
        if re.search(r'率$', name):
            # 检查是否是百分比类指标
            if any(keyword in name for keyword in ['ROE', 'ROA', '毛利率', '净利率', '负债率', '增长率', '收益率', '利润率']):
                return 0.01  # 可能是百分比形式
            return 1
        
        # 默认不转换（假设已经是亿元或标准单位）
        return 1
    
    def _clean_indicator_name(self, name: str) -> str:
        """清理指标名称，去除单位、百分比符号等"""
        import re
        # 去除括号及其内容
        name = re.sub(r'[（(].*?[）)]', '', name)
        # 去除单位文字（亿元、万元、元、%等）
        name = re.sub(r'亿元|万元|元|%|％|‰', '', name)
        # 去除多余空格
        name = name.strip()
        return name
    
    def _get_first_numeric_value(self, series: pd.Series) -> Optional[float]:
        """获取列中的第一个数值"""
        for value in series:
            try:
                num = self.validator.to_float(value)
                if num is not None and not pd.isna(num):
                    return num
            except:
                pass
        return None
    
    def _get_adjacent_value(self, df: pd.DataFrame, row: int, col: int) -> Optional[float]:
        """获取相邻单元格的数值"""
        # 尝试右侧单元格
        if col + 1 < len(df.columns):
            try:
                value = df.iloc[row, col + 1]
                num = self.validator.to_float(value)
                if num is not None and not pd.isna(num):
                    return num
            except (ValueError, IndexError, TypeError):
                pass
        
        # 尝试下方单元格
        if row + 1 < len(df):
            try:
                value = df.iloc[row + 1, col]
                num = self.validator.to_float(value)
                if num is not None and not pd.isna(num):
                    return num
            except (ValueError, IndexError, TypeError):
                pass
        
        # 尝试下方右侧单元格
        if row + 1 < len(df) and col + 1 < len(df.columns):
            try:
                value = df.iloc[row + 1, col + 1]
                num = self.validator.to_float(value)
                if num is not None and not pd.isna(num):
                    return num
            except (ValueError, IndexError, TypeError):
                pass
        
        return None
    
    def _parse_html(self, html_path: str) -> Dict[str, Any]:
        """解析HTML文件"""
        data = {
            '财务指标': {},
            '市场数据': {},
            '经营信息': {}
        }
        
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'html.parser')
            
            # 提取文本
            text = soup.get_text()
            
            # 提取财务指标
            data['财务指标'] = self._extract_financial_data_from_text(text)
            # 提取市场数据
            data['市场数据'] = self._extract_market_data_from_text(text)
            # 提取经营信息
            data['经营信息'] = self._extract_business_info_from_text(text)
            
        except Exception as e:
            print(f"HTML解析失败: {e}")
        
        return data
    
    def _parse_csv(self, csv_path: str) -> Dict[str, Any]:
        """解析CSV文件"""
        data = {
            '财务指标': {},
            '市场数据': {},
            '经营信息': {}
        }
        
        try:
            # 尝试不同编码
            encodings = ['utf-8', 'gbk', 'utf-16']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding)
                    break
                except:
                    continue
            
            if df is not None:
                # 使用智能提取
                csv_data = self._smart_extract_from_dataframe(df)
                data.update(csv_data)
            
        except Exception as e:
            print(f"CSV解析失败: {e}")
        
        return data
    
    def _parse_txt(self, txt_path: str) -> Dict[str, Any]:
        """解析TXT文件"""
        data = {
            '财务指标': {},
            '市场数据': {},
            '经营信息': {}
        }
        
        try:
            # 尝试不同编码
            encodings = ['utf-8', 'gbk', 'utf-16']
            text = ''
            
            for encoding in encodings:
                try:
                    with open(txt_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    break
                except:
                    continue
            
            # 提取财务指标
            data['财务指标'] = self._extract_financial_data_from_text(text)
            # 提取市场数据
            data['市场数据'] = self._extract_market_data_from_text(text)
            # 提取经营信息
            data['经营信息'] = self._extract_business_info_from_text(text)
            
        except Exception as e:
            print(f"TXT解析失败: {e}")
        
        return data
    
    def _extract_financial_data_from_text(self, text: str) -> Dict[str, float]:
        """从文本中提取财务数据"""
        result = {}
        
        for indicator, keywords in self.financial_keywords.items():
            for keyword in keywords:
                # 搜索关键词
                pattern = rf'{keyword}[\s:：]*([\d.,]+)'
                matches = re.findall(pattern, text)
                
                if matches:
                    # 尝试转换为数值
                    for match in matches:
                        value = self.validator.to_float(match)
                        if value is not None:
                            result[indicator] = value
                            break
                    if indicator in result:
                        break
        
        return result
    
    def _extract_market_data_from_text(self, text: str) -> Dict[str, float]:
        """从文本中提取市场数据"""
        result = {}
        
        for indicator, keywords in self.market_keywords.items():
            for keyword in keywords:
                # 搜索关键词
                pattern = rf'{keyword}[\s:：]*([\d.,]+)'
                matches = re.findall(pattern, text)
                
                if matches:
                    # 尝试转换为数值
                    for match in matches:
                        value = self.validator.to_float(match)
                        if value is not None:
                            result[indicator] = value
                            break
                    if indicator in result:
                        break
        
        return result
    
    def _extract_business_info_from_text(self, text: str) -> Dict[str, float]:
        """从文本中提取经营信息"""
        result = {}
        
        for indicator, keywords in self.business_keywords.items():
            for keyword in keywords:
                # 搜索关键词
                pattern = rf'{keyword}[\s:：]*([\d.,]+)'
                matches = re.findall(pattern, text)
                
                if matches:
                    # 尝试转换为数值
                    for match in matches:
                        value = self.validator.to_float(match)
                        if value is not None:
                            result[indicator] = value
                            break
                    if indicator in result:
                        break
        
        return result
    
    def parse_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析表单数据"""
        data = {
            '财务指标': {},
            '市场数据': {},
            '经营信息': {}
        }
        
        # 解析财务指标
        if 'financial_indicators' in form_data:
            data['财务指标'] = form_data['financial_indicators']
        
        # 解析市场数据
        if 'market_data' in form_data:
            data['市场数据'] = form_data['market_data']
        
        # 解析经营信息
        if 'business_info' in form_data:
            data['经营信息'] = form_data['business_info']
        
        return data
