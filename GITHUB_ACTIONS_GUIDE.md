# GitHub Actions 自动运行指南

## 🎯 功能概述

本项目配置了GitHub Actions工作流，可以自动每天运行彩票预测脚本，包括：

- **数据爬取**: 自动获取最新的双色球和大乐透开奖数据
- **模型训练**: 基于最新数据重新训练预测模型
- **预测分析**: 生成下一期的号码预测结果
- **结果归档**: 保存所有运行结果到GitHub Artifacts

## ⚙️ 工作流配置

### 触发条件
- **定时执行**: 每天凌晨2点 (UTC时间) 自动运行
- **手动触发**: 可以在Actions页面手动启动工作流

### 执行流程
1. 检查代码仓库
2. 设置Python 3.6环境
3. 安装项目依赖
4. 创建必要的目录结构
5. 执行双色球(SSQ)数据爬取、训练和预测
6. 执行大乐透(DLT)数据爬取、训练和预测
7. 保存预测结果到文件
8. 上传结果到GitHub Artifacts
9. 在控制台显示摘要信息

## 📁 输出文件

每次运行后，以下文件会被生成并保存：

- `prediction_results.txt` - 完整的预测结果文本
- `data/ssq/data.csv` - 双色球历史数据
- `data/dlt/data.csv` - 大乐透历史数据

## 🔍 查看运行结果

### 方法1: GitHub Actions页面
1. 访问你的GitHub仓库
2. 点击 "Actions" 标签页
3. 选择 "Daily Lottery Prediction" 工作流
4. 点击具体的运行记录
5. 在 "Artifacts" 部分下载 `lottery-predictions`

### 方法2: 控制台输出
在工作流的日志中查看实时的预测结果摘要。

## 🛠️ 自定义配置

### 修改运行时间
编辑 `.github/workflows/daily_prediction.yml` 文件中的cron表达式：

```yaml
on:
  schedule:
    # cron格式: 分钟 小时 日期 月份 星期
    # 0 2 * * * = 每天凌晨2点
    - cron: '0 2 * * *'
```

常用cron模式：
- `0 9 * * *` - 每天早上9点
- `0 14 * * *` - 每天下午2点
- `0 */6 * * *` - 每6小时一次
- `0 0 * * 1` - 每周一午夜

### 调整训练参数
修改 `run_train_model.py` 的调用参数：

```yaml
- name: Run run_train_model.py for SSQ (双色球)
  run: |
    python run_train_model.py --name ssq --train_test_split 0.8
```

- `--train_test_split`: 训练集比例 (建议 > 0.5)

## 🐛 故障排除

### 常见问题和解决方案

#### 1. 依赖安装失败
确保 `requirements.txt` 中的所有包版本兼容。如果遇到TensorFlow相关错误，可能需要更新依赖版本。

#### 2. 数据爬取失败
- 检查网络连接是否正常
- 确认目标网站 `datachart.500.com` 是否可访问
- 可能需要调整请求头或重试机制

#### 3. 模型训练失败
- 检查是否有足够的内存和计算资源
- 确认数据格式正确
- 检查模型配置文件 `config.py`

#### 4. 工作流不触发
- 确认GitHub Actions已启用
- 检查cron表达式是否正确
- 尝试手动触发测试

## 📊 监控和维护

### 监控指标
- 工作流运行状态 (成功/失败)
- 数据更新时间
- 模型训练耗时
- 预测结果质量

### 维护建议
1. **定期更新依赖**：保持 `requirements.txt` 中的包版本最新
2. **监控网站变化**：如果目标网站改版，需要调整爬虫逻辑
3. **优化模型性能**：根据预测准确率调整模型参数
4. **备份重要数据**：定期保存历史预测结果

---

*最后更新: 2026年*
*作者: GitHub Actions 配置助手*

⚠️ **注意**: 使用 `actions/upload-artifact@v4` 而不是已弃用的 v3 版本