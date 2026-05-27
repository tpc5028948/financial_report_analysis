# GitHub Pages 部署指南

## 快速部署步骤

### 1. 创建 GitHub 仓库

首先在 GitHub 上创建一个新的仓库，仓库名称建议使用：`your-portfolio` 或其他你喜欢的名称。

### 2. 初始化 Git 仓库

在本地项目文件夹中执行：

```bash
git init
git add .
git commit -m "Initial commit: Personal portfolio website"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

### 3. 启用 GitHub Pages

1. 进入你的 GitHub 仓库
2. 点击 `Settings`（设置）
3. 在左侧菜单中找到 `Pages`（页面）
4. 在 `Build and deployment` 部分：
   - Source（源代码）选择：`Deploy from a branch`
   - Branch（分支）选择：`main`
   - 文件夹选择：`/ (root)`
5. 点击 `Save` 保存

### 4. 访问你的网站

等待几分钟后，你的网站将可以通过以下地址访问：

```
https://你的用户名.github.io/你的仓库名/
```

## 自定义域名（可选）

如果你有自己的域名：

1. 在仓库根目录创建 `CNAME` 文件
2. 在文件中写入你的域名（如：`portfolio.example.com`）
3. 在你的 DNS 服务商处添加 CNAME 记录，指向 `你的用户名.github.io`
4. 在 GitHub Pages 设置中启用 HTTPS

## 常用命令

### 推送更新

```bash
git add .
git commit -m "Update website content"
git push
```

### 查看状态

```bash
git status
```

### 查看远程仓库

```bash
git remote -v
```

## 常见问题

### Q: 网站显示 404？

A: 确保：
1. 你已经将代码推送到 GitHub
2. GitHub Pages 已正确启用
3. 等待 5-10 分钟让 GitHub 部署完成

### Q: 如何修改个人信息？

A: 直接编辑 `portfolio.html` 文件，修改相关内容后重新提交即可。

### Q: 可以修改配色吗？

A: 可以，在 `portfolio.html` 的 `<style>` 标签中修改颜色配置。

## 项目结构说明

```
.
├── portfolio.html          # 作品集主页（主文件）
├── index.html              # 入口文件（自动跳转到 portfolio.html）
├── README.md               # 项目说明
├── DEPLOY.md               # 部署说明（本文件）
├── frontend/
│   └── index.html          # AI投研助手演示页面
└── ...其他项目文件
```

## 更新内容建议

在发布前，记得更新以下信息：

1. **个人信息**：在 `portfolio.html` 中修改姓名、邮箱、电话等
2. **GitHub 链接**：将模板中的链接替换为你的实际链接
3. **项目内容**：根据实际情况更新项目描述和成果
4. **联系方式**：确保留下准确的邮箱和电话

祝你拥有一个出色的个人作品集网站！
