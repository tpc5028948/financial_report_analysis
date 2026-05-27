import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

class RiskAssessmentModel:
    def __init__(self):
        self.model = None
        self.model_path = os.path.join(os.path.dirname(__file__), 'risk_model.joblib')
        self._load_model()
    
    def _load_model(self):
        """加载预训练模型"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print("模型加载成功")
            except:
                print("模型加载失败，将使用默认模型")
                self._create_default_model()
        else:
            print("模型文件不存在，将创建默认模型")
            self._create_default_model()
    
    def _create_default_model(self):
        """创建默认模型"""
        # 生成示例数据
        X, y = self._generate_sample_data()
        
        # 训练随机森林模型
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        # 保存模型
        try:
            joblib.dump(self.model, self.model_path)
            print("默认模型创建并保存成功")
        except:
            print("模型保存失败")
    
    def _generate_sample_data(self):
        """生成示例训练数据"""
        # 生成1000个样本
        n_samples = 1000
        
        # 特征：[是否亏损, 资产负债率, 负面词汇数量, 发布月份, 公司规模(总资产对数)]
        X = []
        y = []  # 0: 低风险, 1: 中等风险, 2: 高风险
        
        for i in range(n_samples):
            is_loss = np.random.randint(0, 2)
            debt_ratio = np.random.uniform(0, 1)
            negative_words = np.random.randint(0, 20)
            release_month = np.random.randint(1, 13)
            asset_log = np.random.uniform(8, 12)  # 总资产对数
            
            # 构建特征向量
            features = [is_loss, debt_ratio, negative_words, release_month, asset_log]
            X.append(features)
            
            # 生成标签
            risk_score = 0
            if is_loss:
                risk_score += 30
            if debt_ratio > 0.7:
                risk_score += 25
            if negative_words > 5:
                risk_score += 15
            if release_month in [1, 4, 7, 10]:
                risk_score += 10
            if asset_log < 9:
                risk_score += 20
            
            if risk_score >= 70:
                y.append(2)  # 高风险
            elif risk_score >= 40:
                y.append(1)  # 中等风险
            else:
                y.append(0)  # 低风险
        
        return np.array(X), np.array(y)
    
    def predict(self, features):
        """预测风险等级"""
        if self.model is None:
            return None
        
        # 准备特征向量
        feature_vector = self._prepare_feature_vector(features)
        
        # 预测
        prediction = self.model.predict([feature_vector])[0]
        probability = self.model.predict_proba([feature_vector])[0]
        
        # 转换为风险等级
        risk_levels = ['低风险', '中等风险', '高风险']
        risk_level = risk_levels[prediction]
        
        # 转换为Python原生类型
        return {
            '风险等级': risk_level,
            '风险概率': {
                '低风险': float(round(probability[0], 3)),
                '中等风险': float(round(probability[1], 3)),
                '高风险': float(round(probability[2], 3))
            },
            '预测结果': int(prediction)
        }
    
    def _prepare_feature_vector(self, features):
        """准备特征向量"""
        # 提取必要特征
        is_loss = features.get('是否亏损', 0)
        debt_ratio = features.get('资产负债率', 0)
        negative_words = features.get('负面词汇数量', 0)
        release_month = features.get('发布月份', 1)
        asset_log = np.log10(features.get('总资产', 1) + 1)
        
        return [is_loss, debt_ratio, negative_words, release_month, asset_log]
    
    def evaluate_model(self):
        """评估模型性能"""
        if self.model is None:
            return None
        
        # 生成测试数据
        X, y = self._generate_sample_data()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 预测
        y_pred = self.model.predict(X_test)
        
        # 评估
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, target_names=['低风险', '中等风险', '高风险'])
        
        # 转换为Python原生类型
        return {
            '准确率': float(accuracy),
            '分类报告': report
        }
    
    def get_feature_importance(self):
        """获取特征重要性"""
        if self.model is None:
            return None
        
        feature_names = ['是否亏损', '资产负债率', '负面词汇数量', '发布月份', '公司规模对数']
        importances = self.model.feature_importances_
        
        # 排序
        indices = np.argsort(importances)[::-1]
        
        # 转换为Python原生类型
        importance_dict = {}
        for i in indices:
            importance_dict[feature_names[i]] = float(importances[i])
        
        return {
            '特征重要性': importance_dict
        }

if __name__ == "__main__":
    model = RiskAssessmentModel()
    
    # 测试预测
    test_features = {
        '是否亏损': 1,
        '资产负债率': 0.8,
        '负面词汇数量': 10,
        '发布月份': 4,
        '总资产': 500000000
    }
    
    result = model.predict(test_features)
    print("预测结果:", result)
    
    # 测试评估
    evaluation = model.evaluate_model()
    print("模型评估:", evaluation)
    
    # 测试特征重要性
    importance = model.get_feature_importance()
    print("特征重要性:", importance)
