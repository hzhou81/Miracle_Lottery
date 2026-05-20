# -*- coding:utf-8 -*-
"""
Author: BigCat
"""
import argparse
import json
import time
import datetime
import numpy as np
import tensorflow as tf
import pandas as pd
from config import *
from get_data import get_current_number, spider
from loguru import logger

parser = argparse.ArgumentParser()
parser.add_argument('--name', default="ssq", type=str, help="选择训练数据: 双色球/大乐透")
args = parser.parse_args()

# 关闭eager模式
tf.compat.v1.disable_eager_execution()


def load_model(name):
    """ 加载模型 """
    if name == "ssq":
        red_graph = tf.compat.v1.Graph()
        with red_graph.as_default():
            red_saver = tf.compat.v1.train.import_meta_graph(
                "{}red_ball_model.ckpt.meta".format(model_args[args.name]["path"]["red"])
            )
        red_sess = tf.compat.v1.Session(graph=red_graph)
        red_saver.restore(red_sess, "{}red_ball_model.ckpt".format(model_args[args.name]["path"]["red"]))
        logger.info("已加载红球模型！")

        blue_graph = tf.compat.v1.Graph()
        with blue_graph.as_default():
            blue_saver = tf.compat.v1.train.import_meta_graph(
                "{}blue_ball_model.ckpt.meta".format(model_args[args.name]["path"]["blue"])
            )
        blue_sess = tf.compat.v1.Session(graph=blue_graph)
        blue_saver.restore(blue_sess, "{}blue_ball_model.ckpt".format(model_args[args.name]["path"]["blue"]))
        logger.info("已加载蓝球模型！")

        # 加载关键节点名
        with open("{}/{}/{}".format(model_path, args.name, pred_key_name)) as f:
            pred_key_d = json.load(f)

        current_number = get_current_number(args.name)
        logger.info("【{}】最近一期:{}".format(name_path[args.name]["name"], current_number))
        return red_graph, red_sess, blue_graph, blue_sess, pred_key_d, current_number
    else:
        red_graph = tf.compat.v1.Graph()
        with red_graph.as_default():
            red_saver = tf.compat.v1.train.import_meta_graph(
                "{}red_ball_model.ckpt.meta".format(model_args[args.name]["path"]["red"])
            )
        red_sess = tf.compat.v1.Session(graph=red_graph)
        red_saver.restore(red_sess, "{}red_ball_model.ckpt".format(model_args[args.name]["path"]["red"]))
        logger.info("已加载红球模型！")

        blue_graph = tf.compat.v1.Graph()
        with blue_graph.as_default():
            blue_saver = tf.compat.v1.train.import_meta_graph(
                "{}blue_ball_model.ckpt.meta".format(model_args[args.name]["path"]["blue"])
            )
        blue_sess = tf.compat.v1.Session(graph=blue_graph)
        blue_saver.restore(blue_sess, "{}blue_ball_model.ckpt".format(model_args[args.name]["path"]["blue"]))
        logger.info("已加载蓝球模型！")

        # 加载关键节点名
        with open("{}/{}/{}".format(model_path,args.name , pred_key_name)) as f:
            pred_key_d = json.load(f)

        current_number = get_current_number(args.name)
        logger.info("【{}】最近一期:{}".format(name_path[args.name]["name"], current_number))
        return red_graph, red_sess, blue_graph, blue_sess, pred_key_d, current_number


def get_year():
    """ 截取年份
    eg：2020-->20, 2021-->21
    :return:
    """
    return int(str(datetime.datetime.now().year)[-2:])


def number_to_circled(num):
    """ 将数字转换为带圈数字（1-35）
    """
    circled_numbers = [
        "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩",
        "⑪", "⑫", "⑬", "⑭", "⑮", "⑯", "⑰", "⑱", "⑲", "⑳",
        "㉑", "㉒", "㉓", "㉔", "㉕", "㉖", "㉗", "㉘", "㉙", "㉚",
        "㉛", "㉜", "㉝", "㉞", "㉟"
    ]
    if 1 <= num <= 35:
        return circled_numbers[num - 1]
    return str(num)


def format_prediction_result(pred_result, name):
    """ 格式化预测结果为中文数字格式
    例如：双色球1注:{①③⑰㉔㉕㉖：⑮}，金额2元
    """
    lottery_name = name_path[name]["name"]

    if name == "ssq":
        # 双色球：6个红球 + 1个蓝球
        red_balls = [pred_result[f"红球_{i}"] for i in range(1, 7)]
        blue_ball = pred_result["蓝球"]

        red_circled = "".join([number_to_circled(num) for num in red_balls])
        blue_circled = number_to_circled(blue_ball)

        return f"{lottery_name}1注:{{{red_circled}：{blue_circled}}}，金额2元"
    else:
        # 大乐透：5个红球 + 2个蓝球
        red_balls = [pred_result[f"红球_{i}"] for i in range(1, 6)]
        blue_balls = [pred_result[f"蓝球_{i}"] for i in range(1, 3)]

        red_circled = "".join([number_to_circled(num) for num in red_balls])
        blue_circled = "".join([number_to_circled(num) for num in blue_balls])

        return f"{lottery_name}1注:{{{red_circled}：{blue_circled}}}，金额2元"


def get_top_numbers_from_probs(probs, n_class, top_n, sequence_len=1):
    """ 从概率分布中获取前N个号码
    :param probs: 概率数组
    :param n_class: 号码总数
    :param top_n: 需要获取的前N个号码
    :param sequence_len: 序列长度（红球为6，蓝球为1）
    :return: 排序后的号码列表（从1开始）
    """
    # 提取概率 - 处理不同形状的概率数组
    prob_list = []

    if sequence_len > 1:
        # 红球：形状为 (1, sequence_len, n_class)
        # 对每个位置取平均概率，然后取前N个号码
        # probs[0] 形状为 (sequence_len, n_class)
        avg_probs = np.mean(probs[0], axis=0)  # 形状 (n_class,)
        for i in range(n_class):
            prob = avg_probs[i]
            if hasattr(prob, 'item'):
                prob = prob.item()
            prob_list.append((i + 1, prob))  # 号码从1开始
    else:
        # 蓝球：形状可能是 (1, n_class) 或 (n_class,)
        for i in range(n_class):
            if len(probs.shape) > 1:
                prob = probs[0][i]
            else:
                prob = probs[i]
            if hasattr(prob, 'item'):
                prob = prob.item()
            prob_list.append((i + 1, prob))  # 号码从1开始

    # 按概率降序排序
    prob_list.sort(key=lambda x: x[1], reverse=True)

    # 返回前N个号码
    return [num for num, _ in prob_list[:top_n]]


def format_complex_prediction(red_balls, blue_balls, lottery_name, ticket_count, amount):
    """ 格式化复式预测结果
    :param red_balls: 红球列表
    :param blue_balls: 蓝球列表
    :param lottery_name: 彩票名称
    :param ticket_count: 注数
    :param amount: 金额
    :return: 格式化字符串
    """
    red_circled = "".join([number_to_circled(num) for num in sorted(red_balls)])
    blue_circled = "".join([number_to_circled(num) for num in sorted(blue_balls)])

    return f"{lottery_name}{ticket_count}注:{{{red_circled}：{blue_circled}}}，金额{amount}元"


def try_error(mode, name, predict_features, windows_size):
    """ 处理异常
    """
    if mode:
        return predict_features
    else:
        if len(predict_features) != windows_size:
            logger.warning("期号出现跳期，期号不连续！开始查找最近上一期期号！本期预测时间较久！")
            last_current_year = (get_year() - 1) * 1000
            max_times = 160
            while len(predict_features) != 3:
                predict_features = spider(name, last_current_year + max_times, get_current_number(name), "predict")[[x[0] for x in ball_name]]
                time.sleep(np.random.random(1).tolist()[0])
                max_times -= 1
            return predict_features
        return predict_features


def get_red_ball_predict_result(red_graph, red_sess, pred_key_d, predict_features, sequence_len, windows_size):
    """ 获取红球预测结果
    """
    name_list = [(ball_name[0], i + 1) for i in range(sequence_len)]
    data = predict_features[["{}_{}".format(name[0], i) for name, i in name_list]].values.astype(int) - 1
    with red_graph.as_default():
        reverse_sequence = tf.compat.v1.get_default_graph().get_tensor_by_name(pred_key_d[ball_name[0][0]])
        pred = red_sess.run(reverse_sequence, feed_dict={
            "inputs:0": data.reshape(1, windows_size, sequence_len),
            "sequence_length:0": np.array([sequence_len] * 1)
        })
    return pred, name_list


def get_blue_ball_predict_result(blue_graph, blue_sess, pred_key_d, name, predict_features, sequence_len, windows_size):
    """ 获取蓝球预测结果
    """
    if name == "ssq":
        data = predict_features[[ball_name[1][0]]].values.astype(int) - 1
        with blue_graph.as_default():
            # 修正：使用 pred_label 而不是 softmax，因为训练时保存的是 pred_label 的名称
            pred_label = tf.compat.v1.get_default_graph().get_tensor_by_name(pred_key_d[ball_name[1][0]])
            pred = blue_sess.run(pred_label, feed_dict={
                "inputs:0": data.reshape(1, windows_size)
            })
        return pred
    else:
        name_list = [(ball_name[1], i + 1) for i in range(sequence_len)]
        data = predict_features[["{}_{}".format(name[0], i) for name, i in name_list]].values.astype(int) - 1
        with blue_graph.as_default():
            reverse_sequence = tf.compat.v1.get_default_graph().get_tensor_by_name(pred_key_d[ball_name[1][0]])
            pred = blue_sess.run(reverse_sequence, feed_dict={
                "inputs:0": data.reshape(1, windows_size, sequence_len),
                "sequence_length:0": np.array([sequence_len] * 1)
            })
        return pred, name_list


def get_red_ball_probabilities(red_graph, red_sess, predict_features, sequence_len, windows_size):
    """ 获取红球每个号码的命中概率
    """
    name_list = [(ball_name[0], i + 1) for i in range(sequence_len)]
    data = predict_features[["{}_{}".format(name[0], i) for name, i in name_list]].values.astype(int) - 1
    with red_graph.as_default():
        # 获取logits输出（dense/BiasAdd:0）
        logits = tf.compat.v1.get_default_graph().get_tensor_by_name("dense/BiasAdd:0")
        logits_result = red_sess.run(logits, feed_dict={
            "inputs:0": data.reshape(1, windows_size, sequence_len),
            "sequence_length:0": np.array([sequence_len] * 1)
        })
        # 计算softmax概率
        probs = tf.nn.softmax(logits_result, axis=-1)
        with tf.compat.v1.Session() as temp_sess:
            probs_result = temp_sess.run(probs)
    return probs_result, name_list


def get_blue_ball_probabilities(blue_graph, blue_sess, name, predict_features, sequence_len, windows_size):
    """ 获取蓝球每个号码的命中概率
    """
    if name == "ssq":
        data = predict_features[[ball_name[1][0]]].values.astype(int) - 1
        with blue_graph.as_default():
            # 获取softmax概率输出
            softmax_probs = tf.compat.v1.get_default_graph().get_tensor_by_name("dense/Softmax:0")
            probs = blue_sess.run(softmax_probs, feed_dict={
                "inputs:0": data.reshape(1, windows_size)
            })
        return probs
    else:
        name_list = [(ball_name[1], i + 1) for i in range(sequence_len)]
        data = predict_features[["{}_{}".format(name[0], i) for name, i in name_list]].values.astype(int) - 1
        with blue_graph.as_default():
            # DLT蓝球使用CRF模型，获取logits
            logits = tf.compat.v1.get_default_graph().get_tensor_by_name("dense/BiasAdd:0")
            logits_result = blue_sess.run(logits, feed_dict={
                "inputs:0": data.reshape(1, windows_size, sequence_len),
                "sequence_length:0": np.array([sequence_len] * 1)
            })
            # 计算softmax概率
            probs = tf.nn.softmax(logits_result, axis=-1)
            with tf.compat.v1.Session() as temp_sess:
                probs_result = temp_sess.run(probs)
        return probs_result, name_list


def get_final_result(red_graph, red_sess, blue_graph, blue_sess, pred_key_d, name, predict_features, windows_size, mode=0):
    """" 最终预测函数
    """
    m_args = model_args[name]["model_args"]
    if name == "ssq":
        red_pred, red_name_list = get_red_ball_predict_result(
            red_graph, red_sess, pred_key_d,
            predict_features, m_args["sequence_len"], windows_size
        )
        blue_pred = get_blue_ball_predict_result(
            blue_graph, blue_sess, pred_key_d,
            name, predict_features, 0, windows_size
        )
        ball_name_list = ["{}_{}".format(name[mode], i) for name, i in red_name_list] + [ball_name[1][mode]]
        # 修正：blue_pred 是形状 (1,) 的数组，需要取第一个元素
        pred_result_list = red_pred[0].tolist() + [int(blue_pred[0])]
        return {
            b_name: int(res) + 1 for b_name, res in zip(ball_name_list, pred_result_list)
        }
    else:
        red_pred, red_name_list = get_red_ball_predict_result(
            red_graph, red_sess, pred_key_d,
            predict_features, m_args["red_sequence_len"], windows_size
        )
        blue_pred, blue_name_list = get_blue_ball_predict_result(
            blue_graph, blue_sess, pred_key_d,
            name, predict_features, m_args["blue_sequence_len"], windows_size
        )
        ball_name_list = ["{}_{}".format(name[mode], i) for name, i in red_name_list] + ["{}_{}".format(name[mode], i) for name, i in blue_name_list]
        pred_result_list = red_pred[0].tolist() + blue_pred[0].tolist()
        return {
            b_name: int(res) + 1 for b_name, res in zip(ball_name_list, pred_result_list)
        }


def format_probabilities(probs, ball_type, n_class, sequence_len=1):
    """ 格式化概率输出
    :param probs: 概率数组
    :param ball_type: '红球' 或 '蓝球'
    :param n_class: 号码数量
    :param sequence_len: 序列长度（红球为6，蓝球为1）
    :return: 格式化字符串
    """
    # 带圈数字映射表（1-35，支持大乐透的35个红球）
    circled_numbers = [
        "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩",
        "⑪", "⑫", "⑬", "⑭", "⑮", "⑯", "⑰", "⑱", "⑲", "⑳",
        "㉑", "㉒", "㉓", "㉔", "㉕", "㉖", "㉗", "㉘", "㉙", "㉚",
        "㉛", "㉜", "㉝", "㉞", "㉟"
    ]

    result = []
    if sequence_len > 1:
        # 红球：每个位置输出概率，只显示概率最高的前10个号码
        for pos in range(sequence_len):
            pos_probs = []
            for i in range(n_class):
                prob = probs[0][pos][i]
                if hasattr(prob, 'item'):
                    prob = prob.item()
                pos_probs.append((i+1, prob*100))
            # 按概率降序排序，取前10个
            pos_probs.sort(key=lambda x: x[1], reverse=True)
            top_probs = ["{}：{:.1f}%".format(circled_numbers[num-1], p) for num, p in pos_probs[:10]]
            result.append("位置{}: {}".format(pos+1, "  ".join(top_probs)))
    else:
        # 蓝球：单个位置，按概率从大到小显示所有号码概率
        blue_probs = []
        for i in range(n_class):
            prob = probs[0][i] if len(probs.shape) > 1 else probs[i]
            if hasattr(prob, 'item'):
                prob = prob.item()
            blue_probs.append((i, prob*100))
        # 按概率降序排序
        blue_probs.sort(key=lambda x: x[1], reverse=True)
        for i, prob in blue_probs:
            result.append("{}：{:.2f}%".format(circled_numbers[i], prob))
    return "\n".join(result)


def get_windows_size_from_model(graph):
    """ 从模型中获取windows_size """
    try:
        inputs_tensor = graph.get_tensor_by_name('inputs:0')
        return inputs_tensor.shape[1]
    except:
        return model_args[args.name]["model_args"]["windows_size"]


def run(name):
    """ 执行预测 """
    try:
        red_graph, red_sess, blue_graph, blue_sess, pred_key_d, current_number = load_model(name)
        # 从模型中获取实际的windows_size
        windows_size = get_windows_size_from_model(red_graph)
        data = spider(name, 1, current_number, "predict")
        logger.info("【{}】预测期号：{}".format(name_path[name]["name"], int(current_number) + 1))

        # Ensure we have enough data for the window size
        if len(data) < windows_size:
            logger.warning(f"Data has only {len(data)} records, need {windows_size}. Using all available data.")

        # For prediction, we need exactly windows_size records
        # If we don't have enough, duplicate the available data or pad
        if len(data) < windows_size:
            # Pad with the first available record repeated
            padding_needed = windows_size - len(data)
            padding_df = pd.DataFrame([data.iloc[0].values] * padding_needed, columns=data.columns)
            data = pd.concat([padding_df, data], ignore_index=True)

        predict_features_ = try_error(1, name, data.iloc[-windows_size:], windows_size)
        
        # 获取并输出概率分布
        m_args = model_args[name]["model_args"]
        if name == "ssq":
            # 红球概率
            red_probs, red_name_list = get_red_ball_probabilities(
                red_graph, red_sess, predict_features_,
                m_args["sequence_len"], windows_size
            )
            # 蓝球概率
            blue_probs = get_blue_ball_probabilities(
                blue_graph, blue_sess, name, predict_features_,
                0, windows_size
            )

            logger.info("=== 红球命中概率 ===")
            logger.info(format_probabilities(red_probs, "红球", m_args["red_n_class"], m_args["sequence_len"]))
            logger.info("=== 蓝球命中概率 ===")
            logger.info(format_probabilities(blue_probs, "蓝球", m_args["blue_n_class"], 1))
        else:
            # DLT红球概率
            red_probs, red_name_list = get_red_ball_probabilities(
                red_graph, red_sess, predict_features_,
                m_args["red_sequence_len"], windows_size
            )
            # DLT蓝球概率
            blue_probs, blue_name_list = get_blue_ball_probabilities(
                blue_graph, blue_sess, name, predict_features_,
                m_args["blue_sequence_len"], windows_size
            )

            logger.info("=== 红球命中概率 ===")
            logger.info(format_probabilities(red_probs, "红球", m_args["red_n_class"], m_args["red_sequence_len"]))
            logger.info("=== 蓝球命中概率 ===")
            logger.info(format_probabilities(blue_probs, "蓝球", m_args["blue_n_class"], m_args["blue_sequence_len"]))

        # 获取预测结果
        pred_result = get_final_result(
            red_graph, red_sess, blue_graph, blue_sess, pred_key_d, name, predict_features_, windows_size
        )
        # 格式化为中文数字格式
        formatted_result = format_prediction_result(pred_result, name)
        logger.info("预测结果：{}".format(formatted_result))

        # 复式预测
        if name == "ssq":
            # 双色球复式预测
            logger.info("=== 复式预测 ===")

            # 获取红球和蓝球的前N个高概率号码
            red_top_7 = get_top_numbers_from_probs(red_probs, m_args["red_n_class"], 7, m_args["sequence_len"])
            blue_top_16 = get_top_numbers_from_probs(blue_probs, m_args["blue_n_class"], 16, 1)

            # 1. 篮球复式2注：6个红球 + 2个蓝球，金额4元
            # 从预测结果中取6个红球，从概率中取前2个蓝球
            red_balls_6 = [pred_result[f"红球_{i}"] for i in range(1, 7)]
            blue_balls_2 = blue_top_16[:2]
            complex_1 = format_complex_prediction(red_balls_6, blue_balls_2, name_path[name]["name"], 2, 4)
            logger.info("篮球复式2注：{}".format(complex_1))

            # 2. 全蓝复式16注：6个红球 + 16个蓝球，金额32元
            # 从预测结果中取6个红球，从概率中取前16个蓝球
            red_balls_6_blue = [pred_result[f"红球_{i}"] for i in range(1, 7)]
            blue_balls_16 = blue_top_16[:16]
            complex_2 = format_complex_prediction(red_balls_6_blue, blue_balls_16, name_path[name]["name"], 16, 32)
            logger.info("全蓝复式16注：{}".format(complex_2))

        elif name == "dlt":
            # 大乐透复式预测
            logger.info("=== 复式预测 ===")

            # 获取红球和蓝球的前N个高概率号码
            # 大乐透：35个红球，12个蓝球
            red_top_7 = get_top_numbers_from_probs(red_probs, m_args["red_n_class"], 7, m_args["red_sequence_len"])
            blue_top_4 = get_top_numbers_from_probs(blue_probs, m_args["blue_n_class"], 4, m_args["blue_sequence_len"])

            # 1. 后区复式(5+3)3注：5个红球 + 3个蓝球，金额6元
            # 从预测结果中取5个红球，从概率中取前3个蓝球
            red_balls_5 = [pred_result[f"红球_{i}"] for i in range(1, 6)]
            blue_balls_3 = blue_top_4[:3]
            complex_1 = format_complex_prediction(red_balls_5, blue_balls_3, name_path[name]["name"], 3, 6)
            logger.info("后区复式(5+3)3注：{}".format(complex_1))

            # 2. 后区复式(5+4)6注：5个红球 + 4个蓝球，金额12元
            # 从预测结果中取5个红球，从概率中取前4个蓝球
            red_balls_5_2 = [pred_result[f"红球_{i}"] for i in range(1, 6)]
            blue_balls_4 = blue_top_4[:4]
            complex_2 = format_complex_prediction(red_balls_5_2, blue_balls_4, name_path[name]["name"], 6, 12)
            logger.info("后区复式(5+4)6注：{}".format(complex_2))

    except Exception as e:
        logger.info("模型加载失败，检查模型是否训练，错误：{}".format(e))


if __name__ == '__main__':
    if not args.name:
        raise Exception("玩法名称不能为空！")
    else:
        run(args.name)
