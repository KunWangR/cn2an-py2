# -*- coding: UTF-8 -*-
import time
import pathlib
import logging
from pkg_resources import resource_stream

import yaml


def get_default_conf(stream_args=None):
    if stream_args is None:
        stream_args = ["cn2an", "config.yaml"]

    with resource_stream(*stream_args) as stream:
        return yaml.load(stream, Loader=yaml.FullLoader)


def get_logger(name= "cn2an", level="info"):
    logger = logging.getLogger(name)

    level_dict = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    logger.setLevel(level_dict[level])

    if not logger.handlers:
        log_path = log_path_util()
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.INFO)
        fh_fmt = logging.Formatter("%(asctime)-15s %(filename)s %(levelname)s %(lineno)d: %(message)s")
        fh.setFormatter(fh_fmt)

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console_fmt = logging.Formatter("%(filename)s %(levelname)s %(lineno)d: %(message)s")
        console.setFormatter(console_fmt)

        logger.addHandler(fh)
        logger.addHandler(console)

    return logger


def log_path_util(name="cn2an"):
    day = time.strftime("%Y-%m-%d", time.localtime())
    log_path = pathlib.Path("./log/{}".format(day))
    if not log_path.exists():
        log_path.mkdir(parents=True)
    return "{}/{}.log".format(str(log_path), name)


def full_to_half(inputs):
    # 全角转半角
    full_data = ""
    for uchar in inputs:
        inside_code = ord(uchar)
        # 全角空格直接转换
        if inside_code == 12288:
            full_data += chr(32)
        # 全角字符（除空格）根据关系转化
        elif 65281 <= inside_code <= 65374:
            full_data += chr(inside_code - 65248)
        else:
            full_data += uchar
    return full_data
