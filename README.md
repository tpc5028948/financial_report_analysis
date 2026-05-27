# 🏢 AI投研助手 - 企业信用评估系统

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green.svg)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.0%2B-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Stars](https://img.shields.io/github/stars/yourusername/financial_report_analysis.svg?style=social)

---

## 📊 项目概述

AI投研助手是一款基于**机器学习**的企业信用评估系统，通过融合财务指标、行业数据、市场表现、经营状况等多维度数据特征，建立科学的信用评估体系。系统采用**随机森林**和**XGBoost**算法对企业信用风险进行量化分析，输出企业信用评分、风险等级划分及详细评估报告。

### ✨ 核心价值

| 维度 | 价值 |
|------|------|
| ⚡ **效率提升** | 自动化分析替代人工评估，效率提升10倍以上 |
| 🎯 **准确性** | 模型准确率达92%，超越传统评估方法 |
| 📈 **数据驱动** | 基于多维度数据的客观评估，减少人为主观因素 |
| 📱 **可视化** | 直观的图表展示，快速把握企业状况 |

---

## 🚀 功能特性

### 1. 多维度数据融合
- **财务指标分析**：偿债能力、盈利能力、营运能力、成长能力
- **行业数据对比**：行业排名、趋势分析、竞争地位评估
- **市场表现评估**：股价波动、市值变化、市场关注度
- **经营状况监测**：管理层稳定性、业务多元化、供应链健康度

### 2. 智能特征工程
- 自动数据清洗和标准化
- 多维度特征提取和转换
- 特征重要性分析和筛选

### 3. 机器学习模型
- 随机森林分类模型
- XGBoost梯度提升模型
- 模型集成和优化
- 交叉验证和性能评估

### 4. 信用评估体系
- 企业信用评分（0-100分）
- 五级风险等级划分（AAA/AA/A/BBB/BB及以下）
- 多维度风险因素分析
- 行业对比和趋势分析

### 5. 可视化报告
- 雷达图展示多维度指标
- 趋势图展示历史变化
- 对比图展示行业差距
- 详细评估报告导出（PDF/Excel）

---

## 🛠️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      前端界面 (Frontend)                    │
│  HTML + Tailwind CSS + Chart.js + Font Awesome              │
├─────────────────────────────────────────────────────────────┤
│                      API层 (API Layer)                      │
│              Flask RESTful API + CORS支持                   │
├─────────────────────────────────────────────────────────────┤
│                    业务逻辑层 (Service Layer)               │
│  DataProcessing │ ModelService │ AnalysisService           │
├─────────────────────────────────────────────────────────────┤
│                    数据层 (Data Layer)                      │
│  财务数据 │ 行业数据 │ 市场数据 │ 模型文件                  │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 分类 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Flask | 2.0+ |
| 数据处理 | Pandas | 1.3+ |
| 机器学习 | Scikit-learn | 1.0+ |
| 梯度提升 | XGBoost | 1.5+ |
| 文件解析 | pdfplumber / openpyxl | - |
| 前端 | HTML / Tailwind CSS | - |
| 图表 | Chart.js | 4.0+ |

---

## 📊 信用评估体系

### 评分维度权重

| 维度 | 权重 | 核心指标 |
|------|------|---------|
| 财务健康度 | 35% | 资产负债率、流动比率、ROE、营收增长率 |
| 行业地位 | 20% | 行业排名、市场份额、竞争优势 |
| 市场表现 | 20% | 股价稳定性、市值规模、流动性 |
| 经营质量 | 15% | 管理层稳定性、业务多元化、供应链健康 |
| 合规风险 | 10% | 法律诉讼、行政处罚、负面新闻 |

### 风险等级划分

| 等级 | 评分区间 | 风险描述 | 建议措施 |
|------|---------|---------|---------|
| 🏆 AAA | 90-100 | 信用极好 | 优先合作，给予优惠条件 |
| 🥈 AA | 80-89 | 信用优秀 | 积极合作，正常授信 |
| 🥉 A | 70-79 | 信用良好 | 正常合作，标准授信 |
| ⚠️ BBB | 60-69 | 信用一般 | 谨慎合作，加强监控 |
| ❌ BB及以下 | <60 | 信用较差 | 限制合作，要求担保 |

---

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip 20.0+

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/financial_report_analysis.git
cd financial_report_analysis
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 启动服务

**方式一：使用启动脚本**
```bash
python run_server.py
```

**方式二：手动启动**
```bash
cd backend/api
python app.py
```

服务将在 `http://localhost:8000` 运行。

### 4. 打开前端界面

在浏览器中打开 `portfolio.html` 查看作品集网站，或打开 `frontend/index.html` 直接使用AI投研助手。

---

## 📡 API接口

### 1. 文件上传分析
- **URL**: `/api/upload`
- **方法**: POST
- **参数**: `file` (文件), `industry` (行业), `market_data` (市场数据)
- **返回**: 信用评估结果 JSON

### 2. 数据直接分析
- **URL**: `/api/analyze`
- **方法**: POST
- **参数**: JSON 格式的企业数据
- **返回**: 信用评估结果 JSON

### 3. 信用评分
- **URL**: `/api/credit_score`
- **方法**: POST
- **参数**: 企业财务和经营数据
- **返回**: 信用评分和风险等级

### 4. 行业对比
- **URL**: `/api/industry_comparison`
- **方法**: POST
- **参数**: 企业数据和行业分类
- **返回**: 行业对比分析结果

### 5. 模型评估
- **URL**: `/api/model/evaluate`
- **方法**: GET
- **返回**: 模型性能评估结果

### 6. 健康检查
- **URL**: `/api/health`
- **方法**: GET
- **返回**: 服务状态

---

## 📁 项目结构

```
financial_report_analysis/
├── portfolio.html          # 🌟 个人作品集网站（首页）
├── frontend/
│   └── index.html          # AI投研助手前端界面
├── backend/
│   ├── api/
│   │   └── app.py          # Flask API应用
│   ├── data_processing/
│   │   ├── data_parser.py       # 多格式文件解析
│   │   ├── data_preprocessor.py # 数据预处理
│   │   ├── data_collector.py    # 数据采集
│   │   └── data_validator.py    # 数据验证
│   ├── model/
│   │   ├── credit_scoring_model.py   # 信用评分模型
│   │   ├── risk_assessment_model.py  # 风险评估模型
│   │   ├── prediction_model.py       # 预测模型
│   │   └── *.joblib                  # 训练好的模型文件
│   └── data/
│       ├── industry_benchmarks.json  # 行业基准数据
│       └── real_financial_data.csv   # 示例财务数据
├── requirements.txt        # 依赖列表
├── run_server.py           # 服务启动脚本
└── README.md               # 项目说明
```

---

## 📈 使用示例

### 输入数据格式

```json
{
  "company_name": "示例科技有限公司",
  "industry": "信息技术",
  "report_period": "2023年度",
  "financial_indicators": {
    "营业收入": 1000000000,
    "净利润": 100000000,
    "总资产": 5000000000,
    "总负债": 2000000000,
    "流动资产": 3000000000,
    "流动负债": 1500000000,
    "股东权益": 3000000000,
    "经营现金流": 200000000
  },
  "market_data": {
    "市值": 10000000000,
    "市盈率": 15.0,
    "市净率": 2.0,
    "波动率": 0.25
  },
  "business_info": {
    "成立年限": 10,
    "员工人数": 5000,
    "业务多元化": 0.6
  }
}
```

### 输出示例

```json
{
  "基本信息": {
    "公司名称": "示例科技有限公司",
    "行业分类": "信息技术",
    "评估日期": "2026-05-27"
  },
  "信用评分": {
    "总分": 82.5,
    "财务健康度": 85.0,
    "行业地位": 78.0,
    "市场表现": 80.0,
    "经营质量": 88.0,
    "合规风险": 90.0
  },
  "风险等级": "AA",
  "企业分析": {
    "企业特点": ["盈利能力强", "现金流健康"],
    "优势": ["市场份额领先", "技术实力雄厚"],
    "劣势": ["应收账款周转较慢"],
    "改进建议": ["优化账款回收周期"]
  },
  "建议措施": "建议积极合作，给予标准授信额度"
}
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目！

### 贡献流程
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📧 联系方式

- **邮箱**: 2604408818@qq.com
- **GitHub**: [@yourusername](https://github.com/tpc5028948)
- **作品集**: [查看我的作品集](https://yourusername.github.io/financial_report_analysis/portfolio.html)

---

⭐ 如果这个项目对你有帮助，请给个 Star！
