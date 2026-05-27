from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import tempfile
import numpy as np
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_processing.data_parser import DataParser
from data_processing.data_preprocessor import DataPreprocessor
from model.credit_scoring_model import CreditScoringModel
from model.prediction_model import BusinessPredictionModel

# 自定义JSON编码器，处理NumPy类型
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
CORS(app)  # 启用CORS

# 初始化模块
parser = DataParser()
preprocessor = DataPreprocessor()
credit_model = CreditScoringModel()
prediction_model = BusinessPredictionModel()

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件并分析"""
    print('='*50)
    print('收到文件上传请求...')
    print('='*50)
    
    try:
        # 打印请求信息
        print('请求文件:', request.files)
        print('请求表单:', request.form)
        
        # 检查文件是否存在
        if 'file' not in request.files:
            print('错误：没有文件上传')
            return jsonify({'error': '请选择要上传的财务报表文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print('错误：文件名为空')
            return jsonify({'error': '请选择有效的文件'}), 400
        
        print('正在处理文件:', file.filename)
        
        # 保存临时文件
        temp_file_path = None
        try:
            # 获取文件扩展名，处理空扩展名的情况
            file_ext = os.path.splitext(file.filename)[1].lower()
            if not file_ext:
                file_ext = '.xlsx'  # 默认Excel格式
                print('警告：无法确定文件扩展名，默认使用.xlsx')
            
            temp_file = tempfile.NamedTemporaryFile(suffix=file_ext, delete=False)
            temp_file_path = temp_file.name
            file.save(temp_file)
            temp_file.close()
            print('临时文件已保存:', temp_file_path)
            print('文件大小:', os.path.getsize(temp_file_path), 'bytes')
            
            # 解析文件
            print('开始解析文件...')
            raw_data = parser.parse_file(temp_file_path)
            print('文件解析结果:', raw_data)
            
            # 检查解析结果是否有效
            if not raw_data or len(raw_data.get('财务指标', {})) == 0:
                print('警告：未能从文件中提取到财务数据')
                print('将使用表单数据继续处理...')
            
            # 添加补充信息
            company_name = request.form.get('company_name', '未知公司')
            raw_data['公司名称'] = company_name
            raw_data['行业分类'] = request.form.get('industry', '制造业')
            raw_data['报告期'] = request.form.get('report_period', '')
            
            print('公司名称:', raw_data['公司名称'])
            print('行业分类:', raw_data['行业分类'])
            
            # 安全解析JSON数据
            try:
                market_data_str = request.form.get('market_data', '{}')
                if market_data_str:
                    raw_data['市场数据'] = json.loads(market_data_str)
                else:
                    raw_data['市场数据'] = {}
                print('市场数据:', raw_data['市场数据'])
            except Exception as json_error:
                print('解析市场数据JSON失败:', json_error)
                raw_data['市场数据'] = {}
            
            try:
                business_info_str = request.form.get('business_info', '{}')
                if business_info_str:
                    raw_data['经营信息'] = json.loads(business_info_str)
                else:
                    raw_data['经营信息'] = {}
                print('经营信息:', raw_data['经营信息'])
            except Exception as json_error:
                print('解析经营信息JSON失败:', json_error)
                raw_data['经营信息'] = {}
            
            # 预处理数据
            print('开始预处理数据...')
            processed_data = preprocessor.preprocess(raw_data)
            print('数据预处理完成')
            
            # 检查预处理结果
            features = processed_data.get('特征', {})
            if not features:
                print('警告：未提取到有效特征数据')
            
            # 信用评分
            print('开始信用评分...')
            credit_result = credit_model.predict(features)
            print('信用评分完成')
            
            # 未来预测
            historical_data = raw_data.get('历史数据', None)
            print('开始生成预测报告...')
            prediction_report = prediction_model.generate_comprehensive_prediction_report(features, historical_data)
            print('预测报告生成完成')
            
            # 企业特点分析
            company_analysis = credit_model.get_company_analysis(features, processed_data.get('行业分类', '制造业'))
            
            # 构建响应
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
            
        except Exception as inner_error:
            print(f'文件处理过程出错: {inner_error}')
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'文件处理失败: {str(inner_error)}'}), 500
            
        finally:
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    print('临时文件已清理')
                except Exception as cleanup_error:
                    print(f'清理临时文件失败: {cleanup_error}')
                except Exception as cleanup_error:
                    print('清理临时文件失败:', cleanup_error)
                
    except Exception as e:
        print('文件上传处理失败:', e)
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    """直接分析数据"""
    try:
        data = request.json
        
        # 预处理数据
        processed_data = preprocessor.preprocess(data)
        
        # 信用评分
        features = processed_data.get('特征', {})
        credit_result = credit_model.predict(features)
        
        # 未来预测
        historical_data = data.get('历史数据', None)
        prediction_report = prediction_model.generate_comprehensive_prediction_report(features, historical_data)
        
        # 企业特点分析
        company_analysis = credit_model.get_company_analysis(features, processed_data.get('行业分类', '制造业'))
        
        # 构建响应
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

@app.route('/api/credit_score', methods=['POST'])
def credit_score():
    """信用评分接口"""
    try:
        data = request.json
        
        # 预处理数据
        processed_data = preprocessor.preprocess(data)
        
        # 信用评分
        features = processed_data.get('特征', {})
        credit_result = credit_model.predict(features)
        
        return jsonify({
            '公司名称': processed_data.get('公司名称', '未知'),
            '信用评分': credit_result.get('信用评分', 0),
            '信用等级': credit_result.get('信用等级', '未知'),
            '等级描述': credit_model.get_credit_rating_description(credit_result.get('信用等级', '未知')),
            '建议措施': credit_model.get_recommendation(credit_result.get('信用评分', 0))
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/industry_comparison', methods=['POST'])
def industry_comparison():
    """行业对比分析"""
    try:
        data = request.json
        
        # 预处理数据
        processed_data = preprocessor.preprocess(data)
        
        # 获取行业基准
        industry = processed_data.get('行业分类', '制造业')
        benchmarks = preprocessor.industry_benchmarks.get(industry, {})
        
        # 获取企业指标
        features = processed_data.get('特征', {})
        
        # 对比分析
        comparison = {
            '行业分类': industry,
            '企业指标': {
                '资产负债率': round(features.get('资产负债率', 0), 4),
                'ROE': round(features.get('ROE', 0), 4),
                '营收增长率': round(features.get('营收增长率', 0), 4)
            },
            '行业平均': {
                '平均资产负债率': benchmarks.get('平均资产负债率', 0),
                '平均ROE': benchmarks.get('平均ROE', 0),
                '平均营收增长率': benchmarks.get('平均营收增长率', 0)
            },
            '对比结果': {
                '资产负债率对比': '优于行业平均' if features.get('资产负债率', 0) < benchmarks.get('平均资产负债率', 0.6) else '劣于行业平均',
                'ROE对比': '优于行业平均' if features.get('ROE', 0) > benchmarks.get('平均ROE', 0.1) else '劣于行业平均',
                '营收增长率对比': '优于行业平均' if features.get('营收增长率', 0) > benchmarks.get('平均营收增长率', 0.1) else '劣于行业平均'
            }
        }
        
        return jsonify(comparison), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict_future():
    """未来经营状况预测接口"""
    try:
        data = request.json
        
        # 预处理数据
        processed_data = preprocessor.preprocess(data)
        features = processed_data.get('特征', {})
        
        # 获取历史数据
        historical_data = data.get('历史数据', None)
        
        # 生成预测报告
        prediction_report = prediction_model.generate_comprehensive_prediction_report(features, historical_data)
        
        return jsonify(prediction_report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/trends', methods=['POST'])
def predict_trends():
    """基于历史数据的趋势预测"""
    try:
        data = request.json
        historical_data = data.get('历史数据', None)
        
        if not historical_data:
            return jsonify({'error': '请提供历史数据'}), 400
        
        trends = prediction_model.predict_financial_trends(historical_data)
        
        return jsonify(trends), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/model/evaluate', methods=['GET'])
def evaluate_model():
    """评估模型性能"""
    try:
        evaluation = credit_model.evaluate_model()
        return jsonify(evaluation), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/model/feature_importance', methods=['GET'])
def get_feature_importance():
    """获取特征重要性"""
    try:
        importance = credit_model.get_feature_importance()
        return jsonify(importance), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'service': '企业信用评估模型'}), 200

if __name__ == '__main__':
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'development'
    
    # 运行应用
    app.run(host='0.0.0.0', port=8000, debug=True)
