# 双色球+大乐透+七乐彩彩票AI预测

基于 LSTM+CRF 序列模型的彩票预测工具，支持双色球(SSQ)、大乐透(DLT)和七乐彩(QLC)的数据获取、模型训练和结果预测。

---

## 项目概述

本项目的核心是基于**双向LSTM+CRF**的序列模型：
- 将红球序列整体作为一个序列模型看待，引入 CRF 层保证预测号码不重复且符合序列依赖关系
- 蓝球使用单层LSTM（双色球）或LSTM+CRF（大乐透）进行预测
- 使用 `tf.compat.v1` 接口在 TensorFlow 2.x 中以 1.x 模式运行

---

## 特性

- **多彩种支持**: 双色球(SSQ)、大乐透(DLT)、七乐彩(QLC)
- **概率输出**: 预测时输出每个号码的命中概率分布
- **复式预测**: 自动生成多种复式投注方案
- **模型评估**: 训练时自动评估模型在测试集上的命中准确率
- **GitHub Actions 自动化**: 按开奖日自动运行

---

## 安装依赖

1. 安装 Anaconda（参考 [知乎教程](https://zhuanlan.zhihu.com/p/32925500)）

2. 创建 conda 环境：
   ```
   conda create -n lottery python=3.8
   conda activate lottery
   ```

3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

---

## 使用说明

### 1. 获取数据

```
python get_data.py --name ssq   # 双色球
python get_data.py --name dlt   # 大乐透
python get_data.py --name qlc   # 七乐彩
```

数据来源：
- 双色球：http://datachart.500.com/ssq/history/newinc/history.php
- 大乐透：http://datachart.500.com/dlt/history/newinc/history.php
- 七乐彩：http://datachart.500.com/qlc/history/newinc/history.php

### 2. 训练模型

```
python run_train_model.py --name ssq --train_test_split 0.8
python run_train_model.py --name dlt --train_test_split 0.8
python run_train_model.py --name qlc --train_test_split 0.8
```

- 先训练红球模型（LSTM+CRF），再训练蓝球模型
- 模型参数和超参数在 `config.py` 中配置
- 训练完成后自动在测试集上进行评估，输出每期命中球数分布

### 3. 预测

```
python run_predict.py --name ssq   # 双色球
python run_predict.py --name dlt   # 大乐透
python run_predict.py --name qlc   # 七乐彩
```

预测输出包括：
- ✅ **单注预测**: 标准 1 注号码
- 📊 **概率分布**: 每个位置上各号码的命中概率
- 🎯 **复式方案**:
  - 双色球：篮球复式2注、全蓝复式16注
  - 大乐透：后区复式(5+3)3注、(5+4)6注
  - 七乐彩：基本号8码复式、全复式(8+2)

---

## GitHub Actions 自动运行

本项目配置了自动工作流 `.github/workflows/daily_prediction.yml`，按开奖日自动运行：

- **双色球** (SSQ): 每周**二、四、日** 23:59 UTC 触发
- **大乐透** (DLT): 每周**一、三、六** 23:59 UTC 触发
- **七乐彩** (QLC): 每周**一、三、五** 23:59 UTC 触发
- **手动触发**: 进入 Actions → "Daily Lottery Prediction" → Run workflow

预测结果会：
- 更新到 `README.md` 底部
- 上传为 GitHub Artifacts（`lottery-predictions`）

---

## 项目结构

```
Miracle_Lottery/
├── config.py              # 模型参数和路径配置
├── get_data.py            # 数据爬取
├── modeling.py            # LSTM+CRF / LSTM 模型定义
├── run_train_model.py     # 模型训练与评估
├── run_predict.py         # 预测执行（含概率输出和复式方案）
├── requirements.txt       # Python 依赖
├── data/
│   ├── ssq/               # 双色球训练数据
│   ├── dlt/               # 大乐透训练数据
│   └── qlc/               # 七乐彩训练数据
├── model/                 # 训练好的模型文件
└── .github/workflows/     # GitHub Actions 工作流
```

---

## 配置说明

所有模型参数集中在 `config.py`：

| 参数 | 双色球 | 大乐透 | 七乐彩 | 说明 |
|------|--------|--------|--------|------|
| 红球范围 | 1-33 | 1-35 | 1-30 | |
| 蓝球范围 | 1-16 | 1-12 | 1-30 | |
| 红球序列长度 | 6 | 5 | 7 | |
| 蓝球序列长度 | 1 | 2 | 1 | |
| 窗口大小 | 5 | 5 | 5 | 用最近 N 期预测下一期 |

---

## 致谢

欢迎加入QQ群讨论
![avatar](img/qq.jpg)

如果这个程序帮你赚到了钱，请扫码支持一下开发者
![avatar](img/alipay.png)


## Latest Prediction Results

QLC (七乐彩) Prediction Results:
===============================
2026-10-13 04:52:53.952 | INFO     | __main__:run:349 - 【七乐彩】预测期号：26118
2026-10-13 04:52:55.511 | INFO     | __main__:run:420 - 预测结果：七乐彩1注:{①②⑲⑳㉕㉖㉗：⑨}，金额2元

=== Lottery Prediction Summary ===
Date: Tue Oct 13 13:38:15 CST 2026

SSQ (双色球) Prediction Results:
================================
2026-10-13 05:38:01.387 | INFO     | __main__:run:349 - 【双色球】预测期号：26117
2026-10-13 05:38:02.455 | INFO     | __main__:run:420 - 预测结果：双色球1注:{①⑳㉒㉖㉘㉚：⑮}，金额2元

DLT (大乐透) Prediction Results:
===============================
2026-10-13 05:38:08.058 | INFO     | __main__:run:349 - 【大乐透】预测期号：26117
2026-10-13 05:38:09.414 | INFO     | __main__:run:420 - 预测结果：大乐透1注:{③㉙㉚㉝㉟：①⑩}，金额2元

QLC (七乐彩) Prediction Results:
===============================
2026-10-13 05:38:14.388 | INFO     | __main__:run:349 - 【七乐彩】预测期号：26118
2026-10-13 05:38:15.511 | INFO     | __main__:run:420 - 预测结果：七乐彩1注:{②④⑥⑦㉔㉕㉙：㉑}，金额2元

=== Lottery Prediction Summary ===
Date: Wed Oct 14 12:08:34 CST 2026

SSQ (双色球) Prediction Results:
================================
2026-10-14 04:06:07.441 | INFO     | __main__:run:349 - 【双色球】预测期号：26118
2026-10-14 04:06:08.328 | INFO     | __main__:run:420 - 预测结果：双色球1注:{①⑳㉔㉖㉙㉚：⑮}，金额2元

DLT (大乐透) Prediction Results:
===============================
2026-10-14 04:06:13.604 | INFO     | __main__:run:349 - 【大乐透】预测期号：26117
2026-10-14 04:06:14.704 | INFO     | __main__:run:420 - 预测结果：大乐透1注:{①⑪㉛㉜㉝：③⑫}，金额2元

QLC (七乐彩) Prediction Results:
===============================
2026-10-14 04:08:33.511 | INFO     | __main__:run:349 - 【七乐彩】预测期号：26118
2026-10-14 04:08:34.366 | INFO     | __main__:run:420 - 预测结果：七乐彩1注:{②⑤⑥⑩㉕㉖㉗：⑨}，金额2元

=== Lottery Prediction Summary ===
Date: Thu Oct 15 10:44:11 CST 2026

SSQ (双色球) Prediction Results:
================================
2026-10-15 02:39:23.770 | INFO     | __main__:run:349 - 【双色球】预测期号：26118
2026-10-15 02:39:24.834 | INFO     | __main__:run:420 - 预测结果：双色球1注:{①②㉒㉖㉙㉚：①}，金额2元

DLT (大乐透) Prediction Results:
===============================
2026-10-15 02:41:47.204 | INFO     | __main__:run:349 - 【大乐透】预测期号：26118
2026-10-15 02:41:48.421 | INFO     | __main__:run:420 - 预测结果：大乐透1注:{⑦⑧㉚㉝㉟：③⑩}，金额2元

QLC (七乐彩) Prediction Results:
===============================
2026-10-15 02:44:10.032 | INFO     | __main__:run:349 - 【七乐彩】预测期号：26119
2026-10-15 02:44:11.166 | INFO     | __main__:run:420 - 预测结果：七乐彩1注:{②④⑤⑲⑳㉑㉕：㉙}，金额2元

=== Lottery Prediction Summary ===
Date: Thu Oct 15 11:23:59 CST 2026

SSQ (双色球) Prediction Results:
================================
2026-10-15 03:16:58.515 | INFO     | __main__:run:349 - 【双色球】预测期号：26118
2026-10-15 03:16:59.555 | INFO     | __main__:run:420 - 预测结果：双色球1注:{①⑳㉒㉖㉙㉚：⑮}，金额2元

DLT (大乐透) Prediction Results:
===============================
2026-10-15 03:21:34.721 | INFO     | __main__:run:349 - 【大乐透】预测期号：26118
2026-10-15 03:21:35.949 | INFO     | __main__:run:420 - 预测结果：大乐透1注:{③㉓㉙㉜㉝：①②}，金额2元

QLC (七乐彩) Prediction Results:
===============================
2026-10-15 03:23:57.649 | INFO     | __main__:run:349 - 【七乐彩】预测期号：26119
2026-10-15 03:23:58.720 | INFO     | __main__:run:420 - 预测结果：七乐彩1注:{②④⑤⑥⑱⑳㉕：㉑}，金额2元

=== Lottery Prediction Summary ===
Date: Fri Oct 16 11:46:04 CST 2026

SSQ (双色球) Prediction Results:
================================
2026-10-16 03:45:46.585 | INFO     | __main__:run:349 - 【双色球】预测期号：26119
2026-10-16 03:45:47.835 | INFO     | __main__:run:420 - 预测结果：双色球1注:{①⑳㉒㉓㉗㉚：⑮}，金额2元

DLT (大乐透) Prediction Results:
===============================
2026-10-16 03:45:54.776 | INFO     | __main__:run:349 - 【大乐透】预测期号：26118
2026-10-16 03:45:56.335 | INFO     | __main__:run:420 - 预测结果：大乐透1注:{③㉕㉛㉜㉝：③⑩}，金额2元

QLC (七乐彩) Prediction Results:
===============================
2026-10-16 03:46:02.354 | INFO     | __main__:run:349 - 【七乐彩】预测期号：26119
2026-10-16 03:46:03.719 | INFO     | __main__:run:420 - 预测结果：七乐彩1注:{②③⑥⑱⑳㉑㉙：⑨}，金额2元

=== Lottery Prediction Summary ===
Date: Sat Oct 17 11:09:26 CST 2026

SSQ (双色球) Prediction Results:
================================
2026-10-17 03:06:58.926 | INFO     | __main__:run:349 - 【双色球】预测期号：26119
2026-10-17 03:06:59.924 | INFO     | __main__:run:420 - 预测结果：双色球1注:{①⑦⑱㉓㉗㉚：②}，金额2元

DLT (大乐透) Prediction Results:
===============================
2026-10-17 03:09:18.585 | INFO     | __main__:run:349 - 【大乐透】预测期号：26118
2026-10-17 03:09:19.745 | INFO     | __main__:run:420 - 预测结果：大乐透1注:{②③㉛㉜㉝：①⑩}，金额2元

QLC (七乐彩) Prediction Results:
===============================
2026-10-17 03:09:24.971 | INFO     | __main__:run:349 - 【七乐彩】预测期号：26120
2026-10-17 03:09:26.025 | INFO     | __main__:run:420 - 预测结果：七乐彩1注:{②④⑤⑥⑱㉑㉙：⑨}，金额2元

=== Lottery Prediction Summary ===
Date: Sun Oct 18 10:23:25 CST 2026

SSQ (双色球) Prediction Results:
================================
2026-10-18 02:23:07.889 | INFO     | __main__:run:349 - 【双色球】预测期号：26119
2026-10-18 02:23:09.151 | INFO     | __main__:run:420 - 预测结果：双色球1注:{①②㉒㉖㉗㉚：②}，金额2元

DLT (大乐透) Prediction Results:
===============================
2026-10-18 02:23:16.324 | INFO     | __main__:run:349 - 【大乐透】预测期号：26119
2026-10-18 02:23:17.799 | INFO     | __main__:run:420 - 预测结果：大乐透1注:{③⑳㉙㉜㉝：③⑩}，金额2元

QLC (七乐彩) Prediction Results:
===============================
2026-10-18 02:23:23.991 | INFO     | __main__:run:349 - 【七乐彩】预测期号：26120
2026-10-18 02:23:25.307 | INFO     | __main__:run:420 - 预测结果：七乐彩1注:{②⑤⑥⑬⑭㉔㉗：⑫}，金额2元

=== Lottery Prediction Summary ===
Date: Mon Oct 19 11:58:12 CST 2026

SSQ (双色球) Prediction Results:
================================
2026-10-19 03:55:38.853 | INFO     | __main__:run:349 - 【双色球】预测期号：26120
2026-10-19 03:55:40.142 | INFO     | __main__:run:420 - 预测结果：双色球1注:{①②㉒㉖㉙㉚：⑥}，金额2元

DLT (大乐透) Prediction Results:
===============================
2026-10-19 03:58:02.422 | INFO     | __main__:run:349 - 【大乐透】预测期号：26119
2026-10-19 03:58:03.973 | INFO     | __main__:run:420 - 预测结果：大乐透1注:{⑥⑰㉚㉝㉟：①⑦}，金额2元

QLC (七乐彩) Prediction Results:
===============================
2026-10-19 03:58:10.609 | INFO     | __main__:run:349 - 【七乐彩】预测期号：26120
2026-10-19 03:58:11.974 | INFO     | __main__:run:420 - 预测结果：七乐彩1注:{②③⑱⑳㉕㉖㉗：㉙}，金额2元

