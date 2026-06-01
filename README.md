# 双色球+大乐透彩票AI预测
本项目现在支持通过GitHub Actions每天自动运行预测！

### 自动运行配置
- **运行时间**: 每天凌晨2点 (UTC时间)
- **自动执行脚本**:
  1. `get_data.py` - 爬取最新的开奖数据
  2. `run_train_model.py` - 重新训练模型
  3. `run_predict.py` - 生成预测结果
- **预测类型**: 双色球(SSQ)和大乐透(DLT)
- **结果保存**: 预测结果会自动上传到GitHub Artifacts


### 手动触发工作流
你也可以手动触发工作流：
1. 进入 GitHub 仓库的 "Actions" 标签页
2. 选择 "Daily Lottery Prediction" 工作流
3. 点击 "Run workflow" 按钮


### 查看预测结果
每次运行后，你可以在以下位置找到预测结果：
- **GitHub Actions Artifacts**: 下载 `lottery-predictions` artifact
- **控制台输出**: 在 Actions 页面查看详细日志


## 本地运行

如果你想在本地运行，请按照以下步骤：

### 安装依赖

* step1，安装anaconda(可参考https://zhuanlan.zhihu.com/p/32925500)；

* step2，创建一个conda环境，conda create -n your_env_name python=3.6；
       
* step3，进入创建conda的环境 conda activate your_env_name，然后执行pip install -r requirements.txt；
       
* step4，按照Getting Started执行即可，推荐使用PyCharm

## Getting Started

## Getting Started

### 本地运行

```python
python get_data.py  --name ssq  # 执行获取双色球训练数据
```
如果出现解析错误，应该看看网页 http://datachart.500.com/ssq/history/newinc/history.php 是否可以正常访问
若要大乐透，替换参数 --name dlt 即可

```python
python run_train_model.py --name ssq --train_test_split 0.8  # 执行训练双色球模型
```
开始模型训练，先训练红球模型，再训练蓝球模型，模型参数和超参数在 config.py 文件中自行配置
具体训练时间消耗与模型参数和超参数相关。

```python
python run_predict.py  --name ssq # 执行双色球模型预测
```
预测结果会打印在控制台


### 自动化运行 (推荐)

本项目已配置GitHub Actions自动运行：
- **每日自动更新**: 每天凌晨2点自动爬取最新数据并重新训练模型
- **双彩种支持**: 同时预测双色球和大乐透
- **结果归档**: 每次运行的预测结果都会保存到Artifacts中

要启用自动运行：
1. 将代码推送到GitHub仓库
2. GitHub Actions会自动检测并运行工作流
3. 在Actions页面查看运行历史和下载预测结果

## Update

* 新增模型预测评估，可以自行调整训练集和测试集比例，建议训练集采样比例高于0.5

* 修复大乐透蓝球号码预测超出取值范围问题，修复训练传参数导致数据维度不匹配问题

* 有盆友反馈想要个大乐透的预测玩法，加入对大乐透的数据爬取，模型训练，模型预测等功能，通过传入执行参数 --name dlt即可。

* 为了降低本项目的使用门槛，废弃docker模式和微服务，按照Getting Started执行脚本，即可获取预测结果。

* 非常开心有更多的同志们关注项目，并且提出了很多宝贵的问题，但是由于工作较忙，没有给大家比较完善的解答，再次说句抱歉，
大部分问题都是安装依赖问题，我更新了requirements.txt中相关库版本，应该可以解决。

* 之前有issue反应，因为不同红球模型预测会有重复号码出现，所以将红球序列整体作为一个序列模型看待，推翻之前红球之间相互独立设定，
因为序列模型预测要引入crf层，相关API必须在 tf.compat.v1.disable_eager_execution()下，故整个模型采用 1.x 构建和训练模式，
在 2.x 的tensorflow中 tf.compat.v1.XXX 保留了 1.x 的接口方式。

欢迎大家在QQ群中讨论和提出宝贵建议
![avatar](img/qq.jpg)

如果这个程序帮你赚到了钱，请扫码支持一下开发者，开发不易

![avatar](img/alipay.png)


## 🚀 自动运行设置
=== Lottery Prediction Summary ===
Date: Tue May 26 10:39:01 CST 2026

SSQ (双色球) Prediction Results:
================================
[32m2026-05-26 02:39:01.327[0m | [1mINFO    [0m | [36m__main__[0m:[36mrun[0m:[36m439[0m - [1m预测结果：大乐透1注:{⑦⑲㉛㉜㉝：①⑥}，金额2元[0m

DLT (大乐透) Prediction Results:
===============================
[32m2026-05-26 02:39:01.327[0m | [1mINFO    [0m | [36m__main__[0m:[36mrun[0m:[36m439[0m - [1m预测结果：大乐透1注:{⑦⑲㉛㉜㉝：①⑥}，金额2元[0m

=== Lottery Prediction Summary ===
Date: Wed May 27 12:17:12 CST 2026

SSQ (双色球) Prediction Results:
================================
[32m2026-05-27 04:17:12.282[0m | [1mINFO    [0m | [36m__main__[0m:[36mrun[0m:[36m439[0m - [1m预测结果：大乐透1注:{⑦⑧㉚㉝㉞：①②}，金额2元[0m

DLT (大乐透) Prediction Results:
===============================
[32m2026-05-27 04:17:12.282[0m | [1mINFO    [0m | [36m__main__[0m:[36mrun[0m:[36m439[0m - [1m预测结果：大乐透1注:{⑦⑧㉚㉝㉞：①②}，金额2元[0m

=== Lottery Prediction Summary ===
Date: Thu May 28 10:24:18 CST 2026

SSQ (双色球) Prediction Results:
================================
[32m2026-05-28 02:24:17.902[0m | [1mINFO    [0m | [36m__main__[0m:[36mrun[0m:[36m439[0m - [1m预测结果：大乐透1注:{⑥㉒㉙㉜㉝：③⑩}，金额2元[0m

DLT (大乐透) Prediction Results:
===============================
[32m2026-05-28 02:24:17.902[0m | [1mINFO    [0m | [36m__main__[0m:[36mrun[0m:[36m439[0m - [1m预测结果：大乐透1注:{⑥㉒㉙㉜㉝：③⑩}，金额2元[0m

=== Lottery Prediction Summary ===
Date: Sun May 31 13:42:23 CST 2026

SSQ (双色球) Prediction Results:
================================
[32m2026-05-31 05:42:23.492[0m | [1mINFO    [0m | [36m__main__[0m:[36mrun[0m:[36m439[0m - [1m预测结果：大乐透1注:{①②㉘㉛㉝：①②}，金额2元[0m

DLT (大乐透) Prediction Results:
===============================
[32m2026-05-31 05:42:23.492[0m | [1mINFO    [0m | [36m__main__[0m:[36mrun[0m:[36m439[0m - [1m预测结果：大乐透1注:{①②㉘㉛㉝：①②}，金额2元[0m

=== Lottery Prediction Summary ===
Date: Mon Jun  1 12:30:51 CST 2026

SSQ (双色球) Prediction Results:
================================
[32m2026-06-01 04:30:51.122[0m | [1mINFO    [0m | [36m__main__[0m:[36mrun[0m:[36m439[0m - [1m预测结果：大乐透1注:{③㉓㉙㉜㉝：①⑥}，金额2元[0m

DLT (大乐透) Prediction Results:
===============================
[32m2026-06-01 04:30:51.122[0m | [1mINFO    [0m | [36m__main__[0m:[36mrun[0m:[36m439[0m - [1m预测结果：大乐透1注:{③㉓㉙㉜㉝：①⑥}，金额2元[0m

