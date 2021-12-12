# -*- coding: UTF-8 -*-
import regex as re
from typing import Union

from . import utils
from .an2cn import An2Cn


class Cn2An(object):
    def __init__(self):
        self.conf = utils.get_default_conf()
        self.all_num = u"".join(list(self.conf["number_cn2an"].keys()))
        self.all_unit = u"".join(list(self.conf["unit_cn2an"].keys()))
        self.strict_cn_number = self.conf[u"strict_cn_number"]
        self.normal_cn_number = self.conf[u"normal_cn_number"]
        self.check_key_dict = {
            u"strict": u"".join(self.strict_cn_number.values()) + u"点负",
            u"normal": u"".join(self.normal_cn_number.values()) + u"点负",
            u"smart": u"".join(self.normal_cn_number.values()) + u"点负" + u"01234567890.-"
        }
        self.pattern_dict = self.__get_pattern()
        self.ac = An2Cn()
        self.mode_list = [u"strict", u"normal", u"smart"]

    def cn2an(self, inputs=None, mode=u"strict"):
        """中文数字转阿拉伯数字

        :param inputs: 中文数字、阿拉伯数字、中文数字和阿拉伯数字
        :param mode: strict 严格，normal 正常，smart 智能
        :return: 阿拉伯数字
        """
        if inputs is not None or inputs == u"":
            if mode not in self.mode_list:
                raise ValueError(u"mode 仅支持 {} ！".format(str(self.mode_list)))

            # 将数字转化为字符串
            if not isinstance(inputs, unicode):
                inputs = unicode(inputs)

            # 将全角数字和符号转化为半角
            inputs = utils.full_to_half(inputs)

            # 特殊转化 廿
            inputs = inputs.replace(u"廿", u"二十")

            # 检查输入数据是否有效
            sign, integer_data, decimal_data, is_all_num = self.__check_input_data_is_valid(inputs, mode)

            # smart 下的特殊情况
            if sign == 0:
                return integer_data
            else:
                if not is_all_num:
                    if decimal_data is None:
                        output = self.__integer_convert(integer_data)
                    else:
                        output = self.__integer_convert(integer_data) + self.__decimal_convert(decimal_data)
                        # fix 1 + 0.57 = 1.5699999999999998
                        output = round(output, len(decimal_data))
                else:
                    if decimal_data is None:
                        output = self.__direct_convert(integer_data)
                    else:
                        output = self.__direct_convert(integer_data) + self.__decimal_convert(decimal_data)
                        # fix 1 + 0.57 = 1.5699999999999998
                        output = round(output, len(decimal_data))
        else:
            raise ValueError(u"输入数据为空！")

        return sign * output

    def __get_pattern(self):
        # 整数严格检查
        _0 = u"[零]"
        _1_9 = u"[一二三四五六七八九]"
        _10_99 = u"{}?[十]{}?".format(_1_9, _1_9)
        _1_99 = u"({}|{})".format(_10_99, _1_9)
        _100_999 = u"({}[百]([零]{})?|{}[百]{})".format(_1_9, _1_9, _1_9, _10_99)
        _1_999 = u"({}|{})".format(_100_999, _1_99)
        _1000_9999 = u"({}[千]([零]{})?|{}[千]{})".format(_1_9, _1_99, _1_9, _100_999)
        _1_9999 = u"({}|{})".format(_1000_9999, _1_999)
        _10000_99999999 = u"({}[万]([零]{})?|{}[万]{})".format(_1_9999, _1_999, _1_9999, _1000_9999)
        _1_99999999 = u"({}|{})".format(_10000_99999999, _1_9999)
        _100000000_9999999999999999 = u"({}[亿]([零]{})?|{}[亿]{})".format(_1_99999999, _1_99999999, _1_99999999, _10000_99999999)
        _1_9999999999999999 = u"({}|{})".format(_100000000_9999999999999999, _1_99999999)
        str_int_pattern = u"^({}|{})$".format(_0, _1_9999999999999999)
        nor_int_pattern = u"^({}|{})$".format(_0, _1_9999999999999999)

        str_dec_pattern = u"^[零一二三四五六七八九]{0,15}[一二三四五六七八九]$"
        nor_dec_pattern = u"^[零一二三四五六七八九]{0,16}$"

        for str_num in self.strict_cn_number.keys():
            str_int_pattern = str_int_pattern.replace(str_num, self.strict_cn_number[str_num])
            str_dec_pattern = str_dec_pattern.replace(str_num, self.strict_cn_number[str_num])
        for nor_num in self.normal_cn_number.keys():
            nor_int_pattern = nor_int_pattern.replace(nor_num, self.normal_cn_number[nor_num])
            nor_dec_pattern = nor_dec_pattern.replace(nor_num, self.normal_cn_number[nor_num])

        pattern_dict = {
            u"strict": {
                u"int": str_int_pattern,
                u"dec": str_dec_pattern
            },
            u"normal": {
                u"int": nor_int_pattern,
                u"dec": nor_dec_pattern
            }
        }
        return pattern_dict

    def __copy_num(self, num):
        cn_num = u""
        for n in num:
            cn_num += self.conf[u"number_low_an2cn"][int(n)]
        return cn_num

    def __check_input_data_is_valid(self, check_data, mode):
        # 去除 元整、圆整、元正、圆正
        stop_words = [u"元整", u"圆整", u"元正", u"圆正"]
        for word in stop_words:
            if check_data[-2:] == word:
                check_data = check_data[:-2]

        # 去除 元、圆
        if mode != u"strict":
            normal_stop_words = [u"圆", u"元"]
            for word in normal_stop_words:
                if check_data[-1] == word:
                    check_data = check_data[:-1]

        # 处理元角分
        yjf_pattern = re.compile(u"^.*?[元圆][{}]角([{}]分)?$".format(self.all_num, self.all_num))
        result = yjf_pattern.search(check_data)
        if result:
            check_data = check_data.replace(u"元", u"点").replace(u"角", u"").replace(u"分", u"")

        # 处理特殊问法：一千零十一 一万零百一十一
        if u"零十" in check_data:
            check_data = check_data.replace(u"零十", u"零一十")
        if u"零百" in check_data:
            check_data = check_data.replace(u"零百", u"零一百")

        for data in check_data:
            if data not in self.check_key_dict[mode]:
                raise ValueError(u"当前为{}模式，输入的数据不在转化范围内：{}！".format(mode, data))

        # 确定正负号
        if check_data[0] == u"负":
            check_data = check_data[1:]
            sign = -1
        else:
            sign = 1

        if u"点" in check_data:
            split_data = check_data.split(u"点")
            if len(split_data) == 2:
                integer_data, decimal_data = split_data
                # 将 smart 模式中的阿拉伯数字转化成中文数字
                if mode == "smart":
                    integer_data = re.sub(u"\d+", lambda x: self.ac.an2cn(x.group()), integer_data)
                    decimal_data = re.sub(u"\d+", lambda x: self.__copy_num(x.group()), decimal_data)
                    mode = u"normal"
            else:
                raise ValueError(u"数据中包含不止一个点！")
        else:
            integer_data = check_data
            decimal_data = None
            # 将 smart 模式中的阿拉伯数字转化成中文数字
            if mode == u"smart":
                # 10.1万 10.1
                pattern1 = re.compile(u"^-?\d+(\.\d+)?[{}]?$".format(self.all_unit))
                result1 = pattern1.search(integer_data)
                if result1:
                    if result1.group() == integer_data:
                        if integer_data[-1] in self.conf[u"unit_cn2an"].keys():
                            output = int(float(integer_data[:-1]) * self.conf[u"unit_cn2an"][integer_data[-1]])
                        else:
                            output = float(integer_data)
                        return 0, output, None, None

                integer_data = re.sub(u"\d+", lambda x: self.ac.an2cn(x.group()), integer_data)
                mode = u"normal"

        result_int = re.compile(self.pattern_dict[mode][u"int"]).search(integer_data)
        if result_int:
            if result_int.group() == integer_data:
                if decimal_data is not None:
                    result_dec = re.compile(self.pattern_dict[mode][u"dec"]).search(decimal_data)
                    if result_dec:
                        if result_dec.group() == decimal_data:
                            return sign, integer_data, decimal_data, False
                else:
                    return sign, integer_data, decimal_data, False
        else:
            if mode == u"strict":
                raise ValueError(u"不符合格式的数据：{}".format(integer_data))
            elif mode == "normal":
                # 纯数模式：一二三
                ptn_all_num = re.compile(u"^[{}]+$".format(self.all_num))
                result_all_num = ptn_all_num.search(integer_data)
                if result_all_num:
                    if result_all_num.group() == integer_data:
                        if decimal_data is not None:
                            result_dec = re.compile(self.pattern_dict[mode][u"dec"]).search(decimal_data)
                            if result_dec:
                                if result_dec.group() == decimal_data:
                                    return sign, integer_data, decimal_data, True
                        else:
                            return sign, integer_data, decimal_data, True

                # 口语模式：一万二，两千三，三百四
                ptn_speaking_mode = re.compile(u"^[{}][{}][{}]$".format(self.all_num, self.all_unit, self.all_num))
                result_speaking_mode = ptn_speaking_mode.search(integer_data)
                if result_speaking_mode:
                    if result_speaking_mode.group() == integer_data:
                        _unit = self.conf[u"unit_low_an2cn"][self.conf[u"unit_cn2an"][integer_data[1]]//10]
                        integer_data = integer_data + _unit
                        if decimal_data is not None:
                            result_dec = re.compile(self.pattern_dict[mode][u"dec"]).search(decimal_data)
                            if result_dec:
                                if result_dec.group() == decimal_data:
                                    return sign, integer_data, decimal_data, False
                        else:
                            return sign, integer_data, decimal_data, False

        raise ValueError(u"不符合格式的数据：{}".format(check_data))

    def __integer_convert(self, integer_data):
        # 核心
        output_integer = 0
        unit = 1
        ten_thousand_unit = 1
        for index, cn_num in enumerate(reversed(integer_data)):
            # 数值
            if cn_num in self.conf[u"number_cn2an"]:
                num = self.conf[u"number_cn2an"][cn_num]
                output_integer += num * unit
            # 单位
            elif cn_num in self.conf[u"unit_cn2an"]:
                unit = self.conf[u"unit_cn2an"][cn_num]
                # 判断出万、亿、万亿
                if unit % 10000 == 0:
                    # 万 亿
                    if unit > ten_thousand_unit:
                        ten_thousand_unit = unit
                    # 万亿
                    else:
                        ten_thousand_unit = unit * ten_thousand_unit
                        unit = ten_thousand_unit

                if unit < ten_thousand_unit:
                    unit = unit * ten_thousand_unit

                if index == len(integer_data) - 1:
                    output_integer += unit
            else:
                raise ValueError(u"{} 不在转化范围内".format(cn_num))

        return int(output_integer)

    def __decimal_convert(self, decimal_data):
        len_decimal_data = len(decimal_data)

        if len_decimal_data > 16:
            print(u"注意：小数部分长度为 {} ，将自动截取前 16 位有效精度！".format(len_decimal_data))
            decimal_data = decimal_data[:16]
            len_decimal_data = 16

        output_decimal = 0
        for index in range(len(decimal_data) - 1, -1, -1):
            unit_key = self.conf[u"number_cn2an"][decimal_data[index]]
            output_decimal += unit_key * 10 ** -(index + 1)

        # 处理精度溢出问题
        output_decimal = round(output_decimal, len_decimal_data)

        return output_decimal

    def __direct_convert(self, data):
        output_data = 0
        for index in range(len(data) - 1, -1, -1):
            unit_key = self.conf[u"number_cn2an"][data[index]]
            output_data += unit_key * 10 ** (len(data) - index - 1)

        return output_data
