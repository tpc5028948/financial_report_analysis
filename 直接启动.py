#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接启动后端服务
"""
import os
import sys

print("="*60)
print("企业信用评估模型 - 后端服务")
print("="*60)

# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print(f"工作目录: {os.getcwd()}")
print("="*60)
print()

try:
    # 导入所有必要模块
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    import tempfile
    import numpy as np
    import json
    
    print("正在初始化数据模块...")
    from data_processing.data_parser import DataParser
    from data_processing.data_preprocessor import DataPreprocessor
    from model.credit_scoring_model import CreditScoringModel
    from model.prediction_model import BusinessPredictionModel
    
    print("正在创建Flask应用...")
    
    # 自定义JSON编码器
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return super(NumpyEncoder, self).default(obj)
    
    app = Flask(__name__)
    app.json_encoder = NumpyEncoder
    CORS(app)
    
    # 初始化模块
    print("正在初始化模型...")
    parser = DataParser()
    preprocessor = DataPreprocessor()
    credit_model = CreditScoringModel()
    prediction_model = BusinessPredictionModel()
    
    print("="*60)
    print("服务启动成功！")
    print("="*60)
    print()
    print("服务地址: http://localhost:8000")
    print("健康检查: http://localhost:8000/api/health")
    print()
    print("现在可以在浏览器中打开 frontend/index.html")
    print()
    print("按 CTRL+C 可以停止服务")
    print("="*60)
    print()
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'service': '企业信用评估模型'}), 200
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        print("="*60)
        print("收到文件上传请求...")
        print("="*60)
        try:
            if 'file' not in request.files:
                print('错误：没有文件上传')
                return jsonify({'error': '请选择要上传的财务报表文件'}), 400
            
            file = request.files['file']
            if file.filename == '':
                print('错误：文件名为空')
                return jsonify({'error': '请选择有效的文件'}), 400
            
            print(f'正在处理文件: {file.filename}')
            
            temp_file_path = None
            try:
                file_ext = os.path.splitext(file.filename)[1].lower()
                if not file_ext:
                    file_ext = '.xlsx'
                    print('警告：无法确定文件扩展名，默认使用.xlsx')
                
                temp_file = tempfile.NamedTemporaryFile(suffix=file_ext, delete=False)
                temp_file_path = temp_file.name
                file.save(temp_file)
                temp_file.close()
                print(f'临时文件已保存: {temp_file_path}')
                print(f'文件大小: {os.path.getsize(temp_file_path)} 字节')
                
                print('开始解析文件...')
                raw_data = parser.parse_file(temp_file_path)
                print(f'文件解析结果: {raw_data}')
                
                if not raw_data or len(raw_data.get('财务指标', {})) == 0:
                    print('警告：未能从文件中提取到财务数据')
                
                company_name = request.form.get('company_name', '未知公司')
                raw_data['公司名称'] = company_name
                raw_data['行业分类'] = request.form.get('industry', '制造业')
                raw_data['报告期'] = request.form.get('report_period', '')
                
                print(f'公司名称: {raw_data["公司名称"]}')
                print(f'行业分类: {raw_data["行业分类"]}')
                
                try:
                    market_data_str = request.form.get('market_data', '{}')
                    if market_data_str:
                        raw_data['市场数据'] = json.loads(market_data_str)
                    else:
                        raw_data['市场数据'] = {}
                except Exception as e:
                    print(f'解析市场数据JSON失败: {e}')
                    raw_data['市场数据'] = {}
                
                try:
                    business_info_str = request.form.get('business_info', '{}')
                    if business_info_str:
                        raw_data['经营信息'] = json.loads(business_info_str)
                    else:
                        raw_data['经营信息'] = {}
                except Exception as e:
                    print(f'解析经营信息JSON失败: {e}')
                    raw_data['经营信息'] = {}
                
                print('开始预处理数据...')
                processed_data = preprocessor.preprocess(raw_data)
                print('数据预处理完成')
                
                features = processed_data.get('特征', {})
                if not features:
                    print('警告：未提取到有效特征数据')
                
                print('开始信用评分...')
                credit_result = credit_model.predict(features)
                print('信用评分完成')
                
                historical_data = raw_data.get('历史数据', None)
                print('开始生成预测报告...')
                prediction_report = prediction_model.generate_comprehensive_prediction_report(features, historical_data)
                print('预测报告生成完成')
                
                company_analysis = credit_model.get_company_analysis(features, processed_data.get('行业分类', '制造业'))
                
                response = {
                    '基本信息': {
                        '公司名称': processed_data.get('公司名称', company_name),
                        '行业分类': processed_data.get('行业分类', '未知'),
                        '评估日期': processed_data.get('评估日期', '未知')
                    },
                    '信用评分': processed_data.get('信用评估指标', {}),
                    '信用评估': credit_result,
                    '特征': features,
                    '行业对比': processed_data.get('行业对比', {}),
                    '企业分析': company_analysis,
                    '建议措施': credit_model.get_recommendation(credit_result.get('信用评分', 0)),
                    '未来预测': prediction_report
                }
                
                print('成功生成评估结果')
                return jsonify(response), 200
                
            finally:
                if temp_file_path and os.path.exists(temp_file_path):
                    try:
                        os.unlink(temp_file_path)
                        print('临时文件已清理')
                    except Exception as e:
                        print(f'清理临时文件失败: {e}')
                    
        except Exception as e:
            print(f'文件处理过程出错: {e}')
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'文件处理失败: {str(e)}'}), 500
    
    @app.route('/api/analyze', methods=['POST'])
    def analyze_data():
        try:
            data = request.json
            
            processed_data = preprocessor.preprocess(data)
            features = processed_data.get('特征', {})
            credit_result = credit_model.predict(features)
            
            historical_data = data.get('历史数据', None)
            prediction_report = prediction_model.generate_comprehensive_prediction_report(features, historical_data)
            
            company_analysis = credit_model.get_company_analysis(features, processed_data.get('行业分类', '制造业'))
            
            response = {
                '基本信息': {
                    '公司名称': processed_data.get('公司名称', '未知'),
                    '行业分类': processed_data.get('行业分类', '未知'),
                    '评估日期': processed_data.get('评估日期', '未知')
                },
                '信用评分': processed_data.get('信用评估指标', {}),
                '信用评估': credit_result,
                '特征': features,
                '行业对比': processed_data.get('行业对比', {}),
                '企业分析': company_analysis,
                '建议措施': credit_model.get_recommendation(credit_result.get('信用评分', 0)),
                '未来预测': prediction_report
            }
            
            return jsonify(response), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    app.run(host='0.0.0.0', port=8000, debug=True)
    
except Exception as e:
    print(f"\n启动失败: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*60)
    input("\n按回车键退出...")
