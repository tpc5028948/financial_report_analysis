import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime, timedelta

class BusinessPredictionModel:
    """企业经营状况预测模型"""
    
    def __init__(self):
        self.revenue_model = None
        self.profit_model = None
        self.asset_model = None
        self.scaler = StandardScaler()
        self.model_dir = os.path.dirname(__file__)
        self._load_or_create_models()
    
    def _load_or_create_models(self):
        """加载或创建预测模型"""
        revenue_path = os.path.join(self.model_dir, 'revenue_prediction_model.joblib')
        profit_path = os.path.join(self.model_dir, 'profit_prediction_model.joblib')
        asset_path = os.path.join(self.model_dir, 'asset_prediction_model.joblib')
        scaler_path = os.path.join(self.model_dir, 'prediction_scaler.joblib')
        
        try:
            if os.path.exists(revenue_path) and os.path.exists(scaler_path):
                self.revenue_model = joblib.load(revenue_path)
                self.profit_model = joblib.load(profit_path)
                self.asset_model = joblib.load(asset_path)
                self.scaler = joblib.load(scaler_path)
                print("预测模型加载成功")
            else:
                self._create_default_models()
        except:
            print("预测模型加载失败，创建默认模型")
            self._create_default_models()
    
    def _create_default_models(self):
        """创建默认预测模型"""
        # 生成示例数据训练模型
        X, y_revenue, y_profit, y_asset = self._generate_training_data()
        
        # 标准化
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练模型
        self.revenue_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.profit_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.asset_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        
        self.revenue_model.fit(X_scaled, y_revenue)
        self.profit_model.fit(X_scaled, y_profit)
        self.asset_model.fit(X_scaled, y_asset)
        
        # 保存模型
        try:
            joblib.dump(self.revenue_model, os.path.join(self.model_dir, 'revenue_prediction_model.joblib'))
            joblib.dump(self.profit_model, os.path.join(self.model_dir, 'profit_prediction_model.joblib'))
            joblib.dump(self.asset_model, os.path.join(self.model_dir, 'asset_prediction_model.joblib'))
            joblib.dump(self.scaler, os.path.join(self.model_dir, 'prediction_scaler.joblib'))
            print("默认预测模型创建成功")
        except:
            print("预测模型保存失败")
    
    def _generate_training_data(self, n_samples=1000):
        """生成训练数据"""
        np.random.seed(42)
        
        # 特征：当前财务指标 + 时间特征
        X = []
        y_revenue = []
        y_profit = []
        y_asset = []
        
        for _ in range(n_samples):
            # 当前状态
            current_revenue = np.random.uniform(1000, 1000000)  # 万元
            current_profit = current_revenue * np.random.uniform(-0.1, 0.3)
            current_assets = current_revenue * np.random.uniform(0.5, 5)
            debt_ratio = np.random.uniform(0.2, 0.9)
            roe = np.random.uniform(-0.2, 0.3)
            revenue_growth = np.random.uniform(-0.3, 0.5)
            market_cap = current_revenue * np.random.uniform(1, 10)
            years = np.random.uniform(1, 30)
            employees = np.random.uniform(50, 50000)
            
            features = [
                current_revenue,
                current_profit,
                current_assets,
                debt_ratio,
                roe,
                revenue_growth,
                market_cap,
                years,
                employees,
                np.random.uniform(1, 5)  # 预测时间跨度（年）
            ]
            X.append(features)
            
            # 生成目标值（带有一些逻辑关系）
            future_revenue = current_revenue * (1 + revenue_growth * np.random.uniform(0.8, 1.2))
            future_profit = future_revenue * (roe * np.random.uniform(0.8, 1.2))
            future_asset = current_assets * (1 + np.random.uniform(-0.1, 0.3))
            
            y_revenue.append(future_revenue)
            y_profit.append(future_profit)
            y_asset.append(future_asset)
        
        return np.array(X), np.array(y_revenue), np.array(y_profit), np.array(y_asset)
    
    def predict_future_performance(self, current_features, years_ahead=3):
        """预测未来经营状况 - 按月生成，包含波动性"""
        predictions = {
            '预测年份': [],
            '预测营业收入': [],
            '预测净利润': [],
            '预测总资产': [],
            '预测资产负债率': [],
            '预测ROE': [],
            '营收增长率预测': [],
            '风险预警': [],
            '建议措施': []
        }
        
        # 当前值
        current_revenue = current_features.get('营业收入', 0)
        current_profit = current_features.get('净利润', 0)
        current_assets = current_features.get('总资产', 0)
        current_debt_ratio = current_features.get('资产负债率', 0)
        current_roe = current_features.get('ROE', 0)
        current_revenue_growth = current_features.get('营收增长率', 0)
        market_cap = current_features.get('市值', 0)
        years = current_features.get('成立年限', 0)
        employees = current_features.get('员工人数', 0)
        
        # 判断企业当前状况，影响未来趋势
        is_profitable = current_profit > 0
        is_growing = current_revenue_growth > 0
        is_low_debt = current_debt_ratio < 0.5
        
        # 确定趋势方向：基于当前状况，但加入随机性
        # 即使当前好，也可能变差；即使当前差，也可能好转
        trend_probability = {
            'up': 0.4 if is_growing else 0.2,      # 增长概率
            'stable': 0.3,                          # 稳定概率
            'down': 0.3 if is_growing else 0.5     # 下降概率
        }
        
        # 选择趋势方向
        trend = np.random.choice(['up', 'stable', 'down'], p=[trend_probability['up'], trend_probability['stable'], trend_probability['down']])
        
        print(f"预测趋势方向: {trend} (当前增长: {is_growing}, 当前盈利: {is_profitable})")
        
        # 年度基础增长率
        if trend == 'up':
            base_revenue_growth = np.random.uniform(0.05, 0.25)
            base_profit_growth = np.random.uniform(0.03, 0.30)
        elif trend == 'stable':
            base_revenue_growth = np.random.uniform(-0.05, 0.10)
            base_profit_growth = np.random.uniform(-0.10, 0.15)
        else:  # down
            base_revenue_growth = np.random.uniform(-0.20, 0.02)
            base_profit_growth = np.random.uniform(-0.35, 0.05)
        
        for year in range(1, years_ahead + 1):
            # 每年趋势可能变化
            if year > 1 and np.random.random() < 0.3:  # 30%概率趋势变化
                trend = np.random.choice(['up', 'stable', 'down'], p=[0.3, 0.4, 0.3])
                if trend == 'up':
                    base_revenue_growth = np.random.uniform(0.05, 0.25)
                    base_profit_growth = np.random.uniform(0.03, 0.30)
                elif trend == 'stable':
                    base_revenue_growth = np.random.uniform(-0.05, 0.10)
                    base_profit_growth = np.random.uniform(-0.10, 0.15)
                else:
                    base_revenue_growth = np.random.uniform(-0.20, 0.02)
                    base_profit_growth = np.random.uniform(-0.35, 0.05)
            
            # 月度数据生成（更精细）
            monthly_revenues = []
            monthly_profits = []
            
            # 季节性因子
            seasonal_factors = [0.85, 0.90, 1.05, 1.00, 1.02, 1.08, 0.95, 0.98, 1.10, 1.05, 1.15, 1.20]  # 12个月
            
            for month in range(12):
                # 月度波动
                monthly_volatility = np.random.uniform(0.92, 1.08)
                seasonal = seasonal_factors[month]
                
                # 计算月度营收（基于年度增长目标）
                month_revenue = (current_revenue * (1 + base_revenue_growth) / 12) * seasonal * monthly_volatility
                month_profit = month_revenue * (current_profit / current_revenue if current_revenue != 0 else 0.1) * (1 + base_profit_growth) * monthly_volatility
                
                monthly_revenues.append(month_revenue)
                monthly_profits.append(month_profit)
            
            # 年度总计
            pred_revenue = sum(monthly_revenues)
            pred_profit = sum(monthly_profits)
            
            # 资产变化（更现实）
            asset_growth = base_revenue_growth * np.random.uniform(0.5, 1.2)
            pred_asset = current_assets * (1 + asset_growth)
            
            # 计算衍生指标
            pred_revenue_growth = (pred_revenue - current_revenue) / current_revenue if current_revenue > 0 else 0
            pred_debt_ratio = max(0.1, min(0.95, current_debt_ratio * (1 + np.random.uniform(-0.03, 0.05))))
            pred_roe = pred_profit / (pred_asset * (1 - pred_debt_ratio)) if pred_asset > 0 and pred_debt_ratio < 1 else 0
            
            # 风险预警
            risk_warnings = self._generate_risk_warnings(
                pred_revenue, pred_profit, pred_asset, pred_debt_ratio, pred_roe, pred_revenue_growth
            )
            
            # 建议措施
            suggestions = self._generate_suggestions(
                pred_revenue, pred_profit, pred_asset, pred_debt_ratio, pred_roe, pred_revenue_growth, risk_warnings
            )
            
            # 保存预测结果
            future_year = datetime.now().year + year
            predictions['预测年份'].append(str(future_year))
            predictions['预测营业收入'].append(round(pred_revenue, 2))
            predictions['预测净利润'].append(round(pred_profit, 2))
            predictions['预测总资产'].append(round(pred_asset, 2))
            predictions['预测资产负债率'].append(round(pred_debt_ratio, 4))
            predictions['预测ROE'].append(round(pred_roe, 4))
            predictions['营收增长率预测'].append(round(pred_revenue_growth, 4))
            predictions['风险预警'].append(risk_warnings)
            predictions['建议措施'].append(suggestions)
            
            # 保存月度数据用于图表
            predictions[f'{future_year}_月度营收'] = [round(r, 2) for r in monthly_revenues]
            predictions[f'{future_year}_月度利润'] = [round(p, 2) for p in monthly_profits]
            
            # 更新当前值用于下一年预测
            current_revenue = pred_revenue
            current_profit = pred_profit
            current_assets = pred_asset
            current_debt_ratio = pred_debt_ratio
            current_roe = pred_roe
            current_revenue_growth = pred_revenue_growth
        
        return predictions
    
    def _generate_risk_warnings(self, revenue, profit, assets, debt_ratio, roe, revenue_growth):
        """生成风险预警"""
        warnings = []
        
        # 盈利能力风险
        if profit < 0:
            warnings.append('亏损风险：预测净利润为负，企业可能面临经营困难')
        elif profit / revenue < 0.05 if revenue > 0 else True:
            warnings.append('盈利能力下降：预测净利润率较低')
        
        # 偿债能力风险
        if debt_ratio > 0.7:
            warnings.append('高负债风险：预测资产负债率超过70%，偿债压力较大')
        elif debt_ratio > 0.6:
            warnings.append('负债偏高：预测资产负债率超过60%，需关注偿债能力')
        
        # 成长能力风险
        if revenue_growth < -0.1:
            warnings.append('营收下滑风险：预测营业收入大幅下降')
        elif revenue_growth < 0:
            warnings.append('增长停滞：预测营业收入增长率为负')
        
        # 资本回报率风险
        if roe < 0.05:
            warnings.append('资本回报率低：预测ROE低于5%，资本利用效率不高')
        elif roe < 0:
            warnings.append('资本亏损：预测ROE为负，股东权益可能受损')
        
        # 资产规模风险
        if assets <= 0:
            warnings.append('资产异常：预测总资产异常，请检查数据')
        
        if not warnings:
            warnings.append('经营状况良好：预测期内未发现重大风险')
        
        return warnings
    
    def _generate_suggestions(self, revenue, profit, assets, debt_ratio, roe, revenue_growth, warnings):
        """生成经营建议"""
        suggestions = []
        
        # 根据风险生成建议
        for warning in warnings:
            if '亏损' in warning:
                suggestions.append('建议优化成本结构，削减非核心支出，提高运营效率')
                suggestions.append('考虑调整产品定价策略或拓展高毛利业务')
            
            if '负债' in warning:
                suggestions.append('建议优化资本结构，通过股权融资或利润留存降低负债率')
                suggestions.append('加强现金流管理，确保到期债务的偿付能力')
            
            if '营收下滑' in warning or '增长停滞' in warning:
                suggestions.append('建议加大市场开拓力度，开发新产品或进入新市场')
                suggestions.append('优化销售策略，提升客户满意度和复购率')
            
            if '资本回报率' in warning:
                suggestions.append('建议提高资产利用效率，处置闲置资产')
                suggestions.append('优化投资组合，聚焦高回报核心业务')
        
        # 通用建议
        if not suggestions:
            suggestions.append('保持当前良好的经营态势')
            suggestions.append('建议继续加大研发投入，保持技术领先优势')
            suggestions.append('可考虑适度扩张，把握市场机遇')
        
        # 根据具体指标提供建议
        if revenue_growth > 0.3:
            suggestions.append('高速增长期需注意现金流管理，避免过度扩张')
        
        if debt_ratio < 0.4:
            suggestions.append('财务杠杆较低，可适当利用债务融资支持发展')
        
        if roe > 0.2:
            suggestions.append('资本回报优秀，建议通过分红或回购回报股东')
        
        return suggestions
    
    def predict_financial_trends(self, historical_data):
        """基于历史数据预测财务趋势"""
        if not historical_data or len(historical_data.get('年份', [])) < 2:
            return {
                '趋势分析': '历史数据不足，无法进行趋势预测',
                '建议': '请提供至少2年的历史财务数据'
            }
        
        years = historical_data['年份']
        revenues = historical_data['营业收入']
        profits = historical_data['净利润']
        assets = historical_data['总资产']
        
        # 计算历史增长率
        revenue_growth_rates = []
        profit_growth_rates = []
        asset_growth_rates = []
        
        for i in range(1, len(years)):
            if revenues[i-1] > 0:
                revenue_growth_rates.append((revenues[i] - revenues[i-1]) / revenues[i-1])
            if profits[i-1] != 0:
                profit_growth_rates.append((profits[i] - profits[i-1]) / abs(profits[i-1]))
            if assets[i-1] > 0:
                asset_growth_rates.append((assets[i] - assets[i-1]) / assets[i-1])
        
        # 计算平均增长率
        avg_revenue_growth = np.mean(revenue_growth_rates) if revenue_growth_rates else 0
        avg_profit_growth = np.mean(profit_growth_rates) if profit_growth_rates else 0
        avg_asset_growth = np.mean(asset_growth_rates) if asset_growth_rates else 0
        
        # 趋势判断
        revenue_trend = '上升' if avg_revenue_growth > 0.05 else ('下降' if avg_revenue_growth < -0.05 else '平稳')
        profit_trend = '上升' if avg_profit_growth > 0.05 else ('下降' if avg_profit_growth < -0.05 else '平稳')
        asset_trend = '上升' if avg_asset_growth > 0.05 else ('下降' if avg_asset_growth < -0.05 else '平稳')
        
        # 未来3年预测
        last_revenue = revenues[-1]
        last_profit = profits[-1]
        last_asset = assets[-1]
        
        future_predictions = []
        for year in range(1, 4):
            future_year = int(years[-1]) + year
            pred_revenue = last_revenue * (1 + avg_revenue_growth) ** year
            pred_profit = last_profit * (1 + avg_profit_growth) ** year if last_profit > 0 else last_profit
            pred_asset = last_asset * (1 + avg_asset_growth) ** year
            
            future_predictions.append({
                '年份': str(future_year),
                '预测营业收入': round(pred_revenue, 2),
                '预测净利润': round(pred_profit, 2),
                '预测总资产': round(pred_asset, 2)
            })
        
        return {
            '历史平均增长率': {
                '营业收入': round(avg_revenue_growth, 4),
                '净利润': round(avg_profit_growth, 4),
                '总资产': round(avg_asset_growth, 4)
            },
            '趋势判断': {
                '营业收入趋势': revenue_trend,
                '净利润趋势': profit_trend,
                '总资产趋势': asset_trend
            },
            '未来预测': future_predictions,
            '分析建议': self._generate_trend_suggestions(revenue_trend, profit_trend, asset_trend)
        }
    
    def _generate_trend_suggestions(self, revenue_trend, profit_trend, asset_trend):
        """基于趋势生成建议"""
        suggestions = []
        
        if revenue_trend == '上升' and profit_trend == '上升':
            suggestions.append('营收和利润双增长，企业经营状况良好')
            suggestions.append('建议继续加大投入，扩大市场份额')
        elif revenue_trend == '上升' and profit_trend == '下降':
            suggestions.append('增收不增利，需关注成本控制和盈利能力')
            suggestions.append('建议优化产品结构，提高高毛利产品占比')
        elif revenue_trend == '下降' and profit_trend == '下降':
            suggestions.append('营收利润双降，企业面临较大经营压力')
            suggestions.append('建议进行业务转型或战略调整')
        elif revenue_trend == '下降' and profit_trend == '上升':
            suggestions.append('营收下降但利润上升，可能是业务收缩或成本优化结果')
            suggestions.append('需关注营收下滑的持续性风险')
        
        if asset_trend == '上升':
            suggestions.append('资产规模扩张，需关注资产质量和利用效率')
        elif asset_trend == '下降':
            suggestions.append('资产规模收缩，需关注是否影响正常经营')
        
        return suggestions
    
    def generate_comprehensive_prediction_report(self, current_features, historical_data=None):
        """生成综合预测报告"""
        # 未来3年预测
        future_predictions = self.predict_future_performance(current_features, years_ahead=3)
        
        # 趋势分析（如果有历史数据）
        trend_analysis = None
        if historical_data:
            trend_analysis = self.predict_financial_trends(historical_data)
        
        # 综合评估
        overall_assessment = self._generate_overall_assessment(future_predictions, trend_analysis)
        
        return {
            '预测期间': '未来3年',
            '未来预测': future_predictions,
            '趋势分析': trend_analysis,
            '综合评估': overall_assessment,
            '生成时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _generate_overall_assessment(self, future_predictions, trend_analysis):
        """生成综合评估"""
        # 基于最后一年的预测结果进行评估
        last_year_idx = -1
        last_revenue = future_predictions['预测营业收入'][last_year_idx]
        last_profit = future_predictions['预测净利润'][last_year_idx]
        last_debt_ratio = future_predictions['预测资产负债率'][last_year_idx]
        last_roe = future_predictions['预测ROE'][last_year_idx]
        
        # 计算综合得分
        score = 50
        
        if last_profit > 0:
            score += 20
        if last_debt_ratio < 0.6:
            score += 20
        elif last_debt_ratio < 0.7:
            score += 10
        if last_roe > 0.1:
            score += 20
        elif last_roe > 0.05:
            score += 10
        
        # 判断等级
        if score >= 80:
            level = '优秀'
            outlook = '企业未来发展前景良好，建议积极合作'
        elif score >= 60:
            level = '良好'
            outlook = '企业未来发展稳定，可正常合作'
        elif score >= 40:
            level = '一般'
            outlook = '企业未来发展存在不确定性，需谨慎合作'
        else:
            level = '较差'
            outlook = '企业未来发展前景堪忧，建议限制合作'
        
        return {
            '发展前景评级': level,
            '发展前景评分': score,
            '展望': outlook,
            '关键风险点': future_predictions['风险预警'][last_year_idx],
            '核心建议': future_predictions['建议措施'][last_year_idx][:3]  # 取前3条建议
        }

if __name__ == "__main__":
    # 测试预测模型
    model = BusinessPredictionModel()
    
    test_features = {
        '营业收入': 100000,
        '净利润': 15000,
        '总资产': 200000,
        '资产负债率': 0.45,
        'ROE': 0.15,
        '营收增长率': 0.2,
        '市值': 500000,
        '成立年限': 10,
        '员工人数': 1000
    }
    
    # 测试未来预测
    predictions = model.predict_future_performance(test_features)
    print("未来预测结果:")
    for year, revenue, profit, warnings in zip(
        predictions['预测年份'],
        predictions['预测营业收入'],
        predictions['预测净利润'],
        predictions['风险预警']
    ):
        print(f"{year}年: 营收{revenue:.0f}万元, 利润{profit:.0f}万元")
        print(f"  风险: {warnings}")
    
    # 测试历史趋势分析
    historical_data = {
        '年份': ['2020', '2021', '2022', '2023'],
        '营业收入': [80000, 85000, 92000, 100000],
        '净利润': [10000, 11000, 13000, 15000],
        '总资产': [150000, 165000, 180000, 200000]
    }
    
    trends = model.predict_financial_trends(historical_data)
    print("\n趋势分析:")
    print(trends)
