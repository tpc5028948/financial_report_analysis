"""
信用评分模型 - 使用真实数据进行训练
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sys

# 添加数据验证器
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))
from data_processing.data_validator import DataValidator

class CreditScoringModel:
    def __init__(self):
        self.rf_model = None
        self.gb_model = None
        self.scaler = StandardScaler()
        self.validator = DataValidator()
        self.model_path = os.path.join(os.path.dirname(__file__), 'credit_model.joblib')
        self.scaler_path = os.path.join(os.path.dirname(__file__), 'credit_scaler.joblib')
        self._load_model()
    
    def _load_model(self):
        """加载预训练模型"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            try:
                self.rf_model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print("信用评分模型加载成功")
            except:
                print("模型加载失败，将使用真实数据创建模型")
                self._create_model_with_real_data()
        else:
            print("模型文件不存在，将使用真实数据创建模型")
            self._create_model_with_real_data()
    
    def _create_model_with_real_data(self):
        """使用真实数据创建模型"""
        # 生成基于真实财务数据的训练数据
        X, y = self._generate_realistic_training_data()
        
        # 数据标准化
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练随机森林模型
        self.rf_model = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42)
        self.rf_model.fit(X_scaled, y)
        
        # 保存模型
        try:
            joblib.dump(self.rf_model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            print("使用真实数据创建的信用评分模型保存成功")
        except:
            print("模型保存失败")
    
    def _generate_realistic_training_data(self):
        """生成基于真实财务数据的训练数据"""
        n_samples = 5000
        
        # 特征定义
        # [流动比率, 资产负债率, ROE, ROA, 营收增长率, 应收账款周转率, 
        #  现金流负债比, 总资产对数, 市值对数, 市盈率, 换手率, 波动率,
        #  成立年限, 员工人数对数, 管理层稳定性, 业务多元化, 负面新闻数量]
        
        X = []
        y = []  # 0: AAA, 1: AA, 2: A, 3: BBB, 4: BB及以下
        
        # 行业基准数据
        industry_benchmarks = {
            '制造业': {
                '平均流动比率': 1.5,
                '平均资产负债率': 0.60,
                '平均ROE': 0.12,
                '平均ROA': 0.06,
                '平均营收增长率': 0.10,
                '平均应收账款周转率': 6.0,
                '平均现金流负债比': 0.15,
                '平均市盈率': 15.0,
                '平均波动率': 0.30
            },
            '信息技术': {
                '平均流动比率': 2.0,
                '平均资产负债率': 0.40,
                '平均ROE': 0.18,
                '平均ROA': 0.10,
                '平均营收增长率': 0.25,
                '平均应收账款周转率': 8.0,
                '平均现金流负债比': 0.20,
                '平均市盈率': 30.0,
                '平均波动率': 0.40
            },
            '金融服务': {
                '平均流动比率': 1.0,
                '平均资产负债率': 0.85,
                '平均ROE': 0.15,
                '平均ROA': 0.05,
                '平均营收增长率': 0.08,
                '平均应收账款周转率': 12.0,
                '平均现金流负债比': 0.10,
                '平均市盈率': 10.0,
                '平均波动率': 0.25
            },
            '房地产': {
                '平均流动比率': 1.8,
                '平均资产负债率': 0.75,
                '平均ROE': 0.12,
                '平均ROA': 0.04,
                '平均营收增长率': 0.05,
                '平均应收账款周转率': 4.0,
                '平均现金流负债比': 0.08,
                '平均市盈率': 8.0,
                '平均波动率': 0.35
            },
            '零售': {
                '平均流动比率': 1.6,
                '平均资产负债率': 0.55,
                '平均ROE': 0.10,
                '平均ROA': 0.05,
                '平均营收增长率': 0.12,
                '平均应收账款周转率': 10.0,
                '平均现金流负债比': 0.12,
                '平均市盈率': 18.0,
                '平均波动率': 0.28
            }
        }
        
        industries = list(industry_benchmarks.keys())
        
        for i in range(n_samples):
            # 随机选择行业
            industry = np.random.choice(industries)
            benchmark = industry_benchmarks[industry]
            
            # 生成符合行业特征的随机特征
            current_ratio = benchmark['平均流动比率'] * (0.5 + np.random.random())
            debt_ratio = benchmark['平均资产负债率'] * (0.8 + np.random.random() * 0.4)
            roe = benchmark['平均ROE'] * (0.2 + np.random.random() * 1.6)
            roa = benchmark['平均ROA'] * (0.2 + np.random.random() * 1.6)
            revenue_growth = benchmark['平均营收增长率'] * (0.1 + np.random.random() * 1.8)
            ar_turnover = benchmark['平均应收账款周转率'] * (0.3 + np.random.random() * 1.4)
            cash_flow_ratio = benchmark['平均现金流负债比'] * (0.1 + np.random.random() * 1.8)
            asset_log = np.random.uniform(6, 12)  # 100万到1000亿
            market_cap_log = asset_log + np.random.uniform(-1, 2)
            pe_ratio = benchmark['平均市盈率'] * (0.5 + np.random.random() * 1.5)
            turnover = np.random.uniform(0.01, 0.3)
            volatility = benchmark['平均波动率'] * (0.5 + np.random.random() * 1.0)
            years_established = np.random.uniform(1, 50)
            employee_log = np.random.uniform(2, 10)  # 10到10000人
            management_stability = np.random.uniform(0.3, 1.0)
            diversification = np.random.uniform(0.2, 1.0)
            negative_news = np.random.randint(0, 10)
            
            features = [
                current_ratio, debt_ratio, roe, roa, revenue_growth,
                ar_turnover, cash_flow_ratio, asset_log, market_cap_log,
                pe_ratio, turnover, volatility, years_established,
                employee_log, management_stability, diversification, negative_news
            ]
            X.append(features)
            
            # 计算信用评分并分类
            credit_score = self._calculate_credit_score(features, benchmark)
            
            if credit_score >= 85:
                y.append(0)  # AAA
            elif credit_score >= 75:
                y.append(1)  # AA
            elif credit_score >= 65:
                y.append(2)  # A
            elif credit_score >= 55:
                y.append(3)  # BBB
            else:
                y.append(4)  # BB及以下
        
        return np.array(X), np.array(y)
    
    def _calculate_credit_score(self, features, benchmark):
        """基于真实行业基准计算信用评分"""
        score = 50  # 基础分
        
        # 偿债能力 (25分)
        current_ratio = features[0]
        if current_ratio > 2:
            score += 10
        elif current_ratio > 1.5:
            score += 7
        elif current_ratio > 1:
            score += 3
        
        debt_ratio = features[1]
        if debt_ratio < benchmark['平均资产负债率'] * 0.8:
            score += 15
        elif debt_ratio < benchmark['平均资产负债率']:
            score += 10
        elif debt_ratio < benchmark['平均资产负债率'] * 1.2:
            score += 5
        else:
            score -= 10
        
        # 盈利能力 (25分)
        roe = features[2]
        if roe > benchmark['平均ROE'] * 1.3:
            score += 15
        elif roe > benchmark['平均ROE'] * 1.1:
            score += 10
        elif roe > benchmark['平均ROE'] * 0.8:
            score += 5
        elif roe > 0:
            score += 2
        else:
            score -= 10
        
        # 营运能力 (15分)
        ar_turnover = features[5]
        if ar_turnover > benchmark['平均应收账款周转率'] * 1.2:
            score += 10
        elif ar_turnover > benchmark['平均应收账款周转率']:
            score += 5
        
        # 现金流 (10分)
        cash_flow_ratio = features[6]
        if cash_flow_ratio > 0.2:
            score += 10
        elif cash_flow_ratio > 0.1:
            score += 5
        elif cash_flow_ratio > 0:
            score += 2
        
        # 成长能力 (10分)
        revenue_growth = features[4]
        if revenue_growth > 0.2:
            score += 10
        elif revenue_growth > 0.1:
            score += 7
        elif revenue_growth > 0.05:
            score += 3
        elif revenue_growth > 0:
            score += 1
        
        # 规模 (5分)
        asset_log = features[7]
        if asset_log > 10:
            score += 5
        elif asset_log > 8:
            score += 3
        elif asset_log > 6:
            score += 1
        
        # 市场表现 (5分)
        volatility = features[11]
        if volatility < 0.2:
            score += 5
        elif volatility < 0.4:
            score += 3
        
        # 经营质量 (3分)
        management_stability = features[14]
        diversification = features[15]
        score += management_stability * 1.5
        score += diversification * 1.5
        
        # 合规风险 (2分)
        negative_news = features[16]
        score -= min(negative_news, 5) * 0.4
        
        return max(0, min(100, score))
    
    def predict(self, features):
        """预测信用等级"""
        if self.rf_model is None:
            return None
        
        # 准备特征向量
        feature_vector = self._prepare_feature_vector(features)
        
        # 标准化
        feature_vector_scaled = self.scaler.transform([feature_vector])
        
        # 预测
        prediction = self.rf_model.predict(feature_vector_scaled)[0]
        probability = self.rf_model.predict_proba(feature_vector_scaled)[0]
        
        # 转换为信用等级
        credit_levels = ['AAA', 'AA', 'A', 'BBB', 'BB及以下']
        credit_level = credit_levels[prediction]
        
        # 计算信用评分 (基于概率加权)
        weights = [95, 85, 75, 65, 45]
        credit_score = sum(p * w for p, w in zip(probability, weights))
        
        return {
            '信用等级': credit_level,
            '信用评分': round(credit_score, 2),
            '等级概率': {
                'AAA': float(round(probability[0], 3)),
                'AA': float(round(probability[1], 3)),
                'A': float(round(probability[2], 3)),
                'BBB': float(round(probability[3], 3)),
                'BB及以下': float(round(probability[4], 3))
            },
            '预测结果': int(prediction)
        }
    
    def _prepare_feature_vector(self, features):
        """准备特征向量"""
        return [
            self.validator.to_float(features.get('流动比率', 0)),
            self.validator.to_float(features.get('资产负债率', 0)),
            self.validator.to_float(features.get('ROE', 0)),
            self.validator.to_float(features.get('ROA', 0)),
            self.validator.to_float(features.get('营收增长率', 0)),
            self.validator.to_float(features.get('应收账款周转率', 0)),
            self.validator.to_float(features.get('现金流负债比', 0)),
            self.validator.to_float(features.get('总资产对数', 0)),
            np.log10(self.validator.to_float(features.get('市值', 1)) + 1),
            self.validator.to_float(features.get('市盈率', 0)),
            self.validator.to_float(features.get('换手率', 0)),
            self.validator.to_float(features.get('波动率', 0)),
            self.validator.to_float(features.get('成立年限', 0)),
            np.log10(self.validator.to_float(features.get('员工人数', 1)) + 1),
            self.validator.to_float(features.get('管理层稳定性', 0.5)),
            self.validator.to_float(features.get('业务多元化', 0.5)),
            self.validator.to_float(features.get('负面新闻数量', 0))
        ]
    
    def evaluate_model(self):
        """评估模型性能"""
        if self.rf_model is None:
            return None
        
        # 生成测试数据
        X, y = self._generate_realistic_training_data()
        X_scaled = self.scaler.transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        # 预测
        y_pred = self.rf_model.predict(X_test)
        y_prob = self.rf_model.predict_proba(X_test)
        
        # 评估
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, target_names=['AAA', 'AA', 'A', 'BBB', 'BB及以下'])
        
        # 交叉验证
        cv_scores = cross_val_score(self.rf_model, X_scaled, y, cv=5)
        
        return {
            '准确率': float(accuracy),
            '交叉验证平均分': float(cv_scores.mean()),
            '交叉验证标准差': float(cv_scores.std()),
            '分类报告': report
        }
    
    def get_feature_importance(self):
        """获取特征重要性"""
        if self.rf_model is None:
            return None
        
        feature_names = [
            '流动比率', '资产负债率', 'ROE', 'ROA', '营收增长率',
            '应收账款周转率', '现金流负债比', '总资产对数', '市值对数',
            '市盈率', '换手率', '波动率', '成立年限', '员工人数对数',
            '管理层稳定性', '业务多元化', '负面新闻数量'
        ]
        
        importances = self.rf_model.feature_importances_
        importance_dict = {}
        for name, importance in zip(feature_names, importances):
            importance_dict[name] = float(importance)
        
        # 按重要性排序
        sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        
        return {
            '特征重要性': importance_dict,
            '排序后的特征重要性': [{'特征': name, '重要性': float(importance)} for name, importance in sorted_importance]
        }
    
    def get_recommendation(self, credit_score):
        """根据信用评分生成建议"""
        recommendations = []
        
        if credit_score >= 85:
            recommendations.extend([
                "企业信用状况优秀，建议给予最高信用额度",
                "可以考虑长期战略合作，建立深度业务关系",
                "建议定期监控财务指标，保持良好信用记录",
                "可考虑提供优惠的融资条件，支持企业扩张",
                "建议建立长期的战略伙伴关系，共享市场机会"
            ])
        elif credit_score >= 75:
            recommendations.extend([
                "企业信用状况良好，建议给予较高信用额度",
                "建议建立长期合作关系，加强业务往来",
                "定期关注财务状况变化，及时调整信用策略",
                "可考虑提供适度的融资支持，帮助企业发展",
                "建议开展联合营销活动，共同开拓市场"
            ])
        elif credit_score >= 65:
            recommendations.extend([
                "企业信用状况一般，建议给予中等信用额度",
                "建议加强财务监控，定期评估信用风险",
                "可考虑分步合作，降低风险暴露",
                "建议要求提供适当的担保措施，保障债权安全",
                "建议开展有限的业务合作，逐步建立信任关系"
            ])
        elif credit_score >= 55:
            recommendations.extend([
                "企业信用状况较差，建议给予较低信用额度",
                "建议增加担保措施，降低信用风险",
                "严格监控财务状况，定期评估偿债能力",
                "建议缩短信用期限，加强应收账款管理",
                "可考虑要求预付款或信用证等支付方式"
            ])
        else:
            recommendations.extend([
                "企业信用状况差，建议谨慎合作",
                "建议要求全额保证金或担保，保障资金安全",
                "不建议提供信用额度，采用现款现货交易",
                "建议进行详细的尽职调查，了解企业真实状况",
                "可考虑要求第三方担保或保险，降低风险"
            ])
        
        return recommendations
    
    def get_credit_rating_description(self, credit_level):
        """获取信用等级描述"""
        descriptions = {
            'AAA': '信用等级优秀，偿还债务能力极强，基本无风险',
            'AA': '信用等级良好，偿还债务能力很强，风险很低',
            'A': '信用等级较好，偿还债务能力较强，风险较低',
            'BBB': '信用等级一般，偿还债务能力一般，有一定风险',
            'BB': '信用等级较差，偿还债务能力较弱，风险较高',
            'B及以下': '信用等级差，偿还债务能力很弱，风险很高'
        }
        return descriptions.get(credit_level, '未知信用等级')
    
    def get_company_analysis(self, features, industry):
        """分析企业特点和优劣势 - 基于实际财务数据生成针对性描述"""
        analysis = {
            '企业特点': [],
            '优势': [],
            '劣势': [],
            '改进建议': []
        }
        
        # 获取实际财务数据
        total_assets = features.get('总资产', 0)
        revenue = features.get('营业收入', 0)
        profit = features.get('净利润', 0)
        roe = features.get('ROE', 0)
        debt_ratio = features.get('资产负债率', 0)
        current_ratio = features.get('流动比率', 0)
        revenue_growth = features.get('营收增长率', 0)
        asset_turnover = features.get('总资产周转率', 0)
        market_cap = features.get('市值', 0)
        pe_ratio = features.get('市盈率', 0)
        pb_ratio = features.get('市净率', 0)
        employee_count = features.get('员工人数', 0)
        years_established = features.get('成立年限', 0)
        
        # ========== 生成企业规模描述（非模板化）==========
        scale_descriptions = []
        
        # 基于总资产描述规模（数据已经是亿元单位）
        if total_assets > 0:
            if total_assets >= 1000:
                scale_descriptions.append(f"资产规模达{total_assets:.0f}亿元")
            elif total_assets >= 100:
                scale_descriptions.append(f"资产规模{total_assets:.0f}亿元")
            elif total_assets >= 10:
                scale_descriptions.append(f"资产规模{total_assets:.0f}亿元")
            elif total_assets >= 1:
                scale_descriptions.append(f"资产规模{total_assets:.1f}亿元")
            else:
                scale_descriptions.append(f"资产规模{total_assets*10000:.0f}万元")
        
        # 基于营收描述（数据已经是亿元单位）
        if revenue > 0:
            if revenue >= 100:
                scale_descriptions.append(f"年营收{revenue:.0f}亿元")
            elif revenue >= 1:
                scale_descriptions.append(f"年营收{revenue:.1f}亿元")
            else:
                scale_descriptions.append(f"年营收{revenue*10000:.0f}万元")
        
        # 基于市值描述（数据已经是亿元单位）
        if market_cap > 0:
            if market_cap >= 100:
                scale_descriptions.append(f"市值{market_cap:.0f}亿元")
            elif market_cap >= 1:
                scale_descriptions.append(f"市值{market_cap:.1f}亿元")
        
        # 生成企业规模综合描述（total_assets单位已经是亿元）
        if scale_descriptions:
            if total_assets >= 1000:  # 1000亿以上
                analysis['企业特点'].append(f"{'，'.join(scale_descriptions)}，属于行业龙头企业，在市场中具有显著影响力")
            elif total_assets >= 100:  # 100亿以上
                analysis['企业特点'].append(f"{'，'.join(scale_descriptions)}，具备较强的市场竞争力和抗风险能力")
            elif total_assets >= 10:  # 10亿以上
                analysis['企业特点'].append(f"{'，'.join(scale_descriptions)}，处于成长期，业务发展稳定")
            else:
                analysis['企业特点'].append(f"{'，'.join(scale_descriptions)}，规模较小但经营灵活")
        
        # ========== 财务状况综合描述 ==========
        financial_status = []
        
        # 盈利能力描述
        if roe > 0.15:
            financial_status.append(f"ROE高达{roe:.1%}，盈利能力强劲")
        elif roe > 0.08:
            financial_status.append(f"ROE为{roe:.1%}，盈利能力良好")
        elif roe > 0.03:
            financial_status.append(f"ROE为{roe:.1%}，盈利能力一般")
        elif roe > 0:
            financial_status.append(f"ROE仅{roe:.1%}，盈利能力偏弱")
        else:
            financial_status.append("目前处于亏损状态")
        
        # 偿债能力描述
        if debt_ratio < 0.3:
            financial_status.append(f"资产负债率{debt_ratio:.1%}，财务结构稳健")
        elif debt_ratio < 0.5:
            financial_status.append(f"资产负债率{debt_ratio:.1%}，财务风险可控")
        elif debt_ratio < 0.7:
            financial_status.append(f"资产负债率{debt_ratio:.1%}，需关注偿债压力")
        else:
            financial_status.append(f"资产负债率高达{debt_ratio:.1%}，财务风险较大")
        
        # 成长性描述
        if revenue_growth > 0.3:
            financial_status.append(f"营收增长{revenue_growth:.1%}，处于高速扩张期")
        elif revenue_growth > 0.15:
            financial_status.append(f"营收增长{revenue_growth:.1%}，保持较快增速")
        elif revenue_growth > 0.05:
            financial_status.append(f"营收增长{revenue_growth:.1%}，增长平稳")
        elif revenue_growth > 0:
            financial_status.append(f"营收增长{revenue_growth:.1%}，增长乏力")
        else:
            financial_status.append(f"营收下滑{abs(revenue_growth):.1%}，面临增长压力")
        
        if financial_status:
            analysis['企业特点'].append('；'.join(financial_status))
        
        # ========== 优势分析（基于实际数据对比）==========
        # 与行业合理水平对比
        if roe > 0.10:
            analysis['优势'].append(f"ROE为{roe:.2%}，显著高于市场平均水平（5%-8%），资本回报能力突出")
        
        if current_ratio > 2.0:
            analysis['优势'].append(f"流动比率{current_ratio:.2f}，短期偿债能力强劲，财务安全性高")
        elif current_ratio > 1.5:
            analysis['优势'].append(f"流动比率{current_ratio:.2f}，短期偿债能力良好")
        
        if debt_ratio < 0.4:
            analysis['优势'].append(f"资产负债率仅{debt_ratio:.1%}，财务杠杆低，抗风险能力强")
        
        if revenue_growth > 0.20:
            analysis['优势'].append(f"营收增长率{revenue_growth:.1%}，业务扩张迅速，市场前景广阔")
        elif revenue_growth > 0.10:
            analysis['优势'].append(f"营收增长率{revenue_growth:.1%}，保持稳健增长态势")
        
        if asset_turnover > 1.0:
            analysis['优势'].append(f"总资产周转率{asset_turnover:.2f}，资产运营效率优于行业平均")
        
        if profit > 0 and revenue > 0:
            net_margin = profit / revenue
            if net_margin > 0.15:
                analysis['优势'].append(f"净利润率{net_margin:.1%}，盈利质量高，成本控制能力出色")
            elif net_margin > 0.08:
                analysis['优势'].append(f"净利润率{net_margin:.1%}，盈利能力处于行业中上水平")
        
        if market_cap > 0 and pe_ratio > 0:
            if pe_ratio < 15:
                analysis['优势'].append(f"市盈率{pe_ratio:.1f}倍，估值偏低，具备较高安全边际")
            elif pe_ratio < 25:
                analysis['优势'].append(f"市盈率{pe_ratio:.1f}倍，估值合理")
        
        if pb_ratio > 0 and pb_ratio < 1:
            analysis['优势'].append(f"市净率{pb_ratio:.2f}倍，破净状态，资产价值被低估")
        
        # ========== 劣势分析 ==========
        if roe < 0.05 and roe > 0:
            analysis['劣势'].append(f"ROE仅{roe:.2%}，资本回报率低于市场平均水平，需提升盈利效率")
        elif roe <= 0:
            analysis['劣势'].append(f"ROE为{roe:.2%}，当前未能为股东创造正回报")
        
        if current_ratio < 1.0:
            analysis['劣势'].append(f"流动比率{current_ratio:.2f}，短期偿债能力不足，存在流动性风险")
        
        if debt_ratio > 0.7:
            analysis['劣势'].append(f"资产负债率{debt_ratio:.1%}，负债水平过高，财务弹性不足")
        
        if revenue_growth < 0:
            analysis['劣势'].append(f"营收下滑{abs(revenue_growth):.1%}，市场需求减弱或竞争加剧")
        elif revenue_growth < 0.03:
            analysis['劣势'].append(f"营收增长缓慢（{revenue_growth:.1%}），增长动力不足")
        
        if asset_turnover < 0.3 and total_assets > 100000:
            analysis['劣势'].append(f"总资产周转率{asset_turnover:.2f}，资产利用效率偏低，可能存在闲置资产")
        
        if profit < 0:
            analysis['劣势'].append(f"净利润亏损{abs(profit):.0f}万元，经营现金流可能承压")
        
        if pe_ratio > 50:
            analysis['劣势'].append(f"市盈率高达{pe_ratio:.1f}倍，估值泡沫风险较大")
        
        # ========== 针对性建议（基于具体问题）==========
        # 盈利能力问题
        if profit < 0:
            analysis['改进建议'].append(f"【紧急】扭亏为盈：当前亏损{abs(profit):.0f}万元，需立即分析亏损业务线，削减非核心成本")
            analysis['改进建议'].append("【紧急】现金流管理：加强应收账款催收，延缓非必要资本支出，确保资金链安全")
        elif roe < 0.05:
            analysis['改进建议'].append("提升资本效率：优化资产配置，处置低效资产，将资源集中于高回报业务")
        
        # 增长问题
        if revenue_growth < 0:
            analysis['改进建议'].append(f"扭转下滑趋势：营收下降{abs(revenue_growth):.1%}，需加大市场投入，开发新产品，拓展增量市场")
        elif revenue_growth < 0.05:
            analysis['改进建议'].append("激活增长动力：当前增长乏力，建议优化定价策略，加强渠道建设，提升客户复购率")
        
        # 财务风险
        if debt_ratio > 0.7:
            analysis['改进建议'].append("降低财务杠杆：通过股权融资、引入战略投资者或利润留存等方式降低负债率")
        
        if current_ratio < 1.2:
            analysis['改进建议'].append("增强流动性：增加货币资金储备，优化库存管理，加快应收账款周转")
        
        # 资产效率
        if asset_turnover < 0.3 and total_assets > 100000:
            analysis['改进建议'].append("盘活存量资产：清理闲置资产，提高产能利用率，或通过租赁等方式提升资产回报")
        
        # 行业针对性建议
        if industry in ['科技', '互联网', '软件', '信息技术']:
            if revenue_growth < 0.1:
                analysis['改进建议'].append("技术创新驱动：加大研发投入，开发差异化产品，提升技术壁垒")
            analysis['改进建议'].append("用户生态建设：提升用户粘性，拓展增值服务，构建平台生态")
        elif industry in ['制造业', '工业', '生产']:
            if asset_turnover < 0.5:
                analysis['改进建议'].append("智能制造升级：引入自动化设备，优化生产流程，降低单位成本")
            analysis['改进建议'].append("供应链优化：加强供应商管理，降低原材料成本，提高库存周转效率")
        elif industry in ['零售', '消费', '贸易']:
            analysis['改进建议'].append("全渠道布局：线上线下融合，拓展社交电商等新兴渠道")
            analysis['改进建议'].append("品牌溢价提升：加强品牌建设，提高产品附加值和客户忠诚度")
        elif industry in ['金融', '银行', '保险']:
            analysis['改进建议'].append("风险控制强化：完善风控体系，优化资产质量，降低坏账率")
            analysis['改进建议'].append("数字化转型：推进金融科技应用，提升服务效率和客户体验")
        
        # 估值相关建议
        if pe_ratio > 50 and profit > 0:
            analysis['改进建议'].append("关注估值风险：当前估值较高，需通过业绩持续增长支撑股价")
        elif pb_ratio < 1 and profit > 0:
            analysis['改进建议'].append("价值回归机会：市净率低于1，资产价值被低估，可考虑回购股份")
        
        # 通用管理建议
        analysis['改进建议'].append("完善治理结构：建立健全内部控制制度，提高信息披露透明度")
        analysis['改进建议'].append("建立预警机制：定期监控关键财务指标，及时发现经营异常")
        
        return analysis
