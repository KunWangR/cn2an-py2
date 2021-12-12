# -*- coding: UTF-8 -*-
from typing import Union

from . import utils


class An2Cn(object):
    def __init__(self):
        self.conf = utils.get_default_conf()
        self.all_num = u"0123456789"
        self.number_low = self.conf[u"number_low_an2cn"]
        self.number_up = self.conf[u"number_up_an2cn"]
        self.mode_list = [u"low", u"up", u"rmb", u"direct"]

    def an2cn(self, inputs=None, mode=u"low"):
        """阿拉伯数字转中文数字

        :param inputs: 阿拉伯数字
        :param mode: low 小写数字，up 大写数字，rmb 人民币大写，direct 直接转化
        :return: 中文数字
        """
        if inputs is not None and inputs != u"":
            if mode not in self.mode_list:
                raise ValueError(u"mode 仅支持 {} ！".format(str(self.mode_list)))

            # 将数字转化为字符串，这里会有Python会自动做转化
            # 1. -> 1.0 1.00 -> 1.0 -0 -> 0
            if not isinstance(inputs, str):
                inputs = self.__number_to_string(inputs)

            # 将全角数字和符号转化为半角
            inputs = utils.full_to_half(inputs)

            # 检查数据是否有效
            self.__check_inputs_is_valid(inputs)

            # 判断正负
            if inputs[0] == u"-":
                sign = u"负"
                inputs = inputs[1:]
            else:
                sign = u""

            if mode == u"direct":
                output = self.__direct_convert(inputs)
            else:
                # 切割整数部分和小数部分
                split_result = inputs.split(u".")
                len_split_result = len(split_result)
                if len_split_result == 1:
                    # 不包含小数的输入
                    integer_data = split_result[0]
                    if mode == u"rmb":
                        output = self.__integer_convert(integer_data, u"up") + u"元整"
                    else:
                        output = self.__integer_convert(integer_data, mode)
                elif len_split_result == 2:
                    # 包含小数的输入
                    integer_data, decimal_data = split_result
                    if mode == u"rmb":
                        int_data = self.__integer_convert(integer_data, u"up")
                        dec_data = self.__decimal_convert(decimal_data, u"up")
                        len_dec_data = len(dec_data)

                        if len_dec_data == 0:
                            output = int_data + u"元整"
                        elif len_dec_data == 1:
                            raise ValueError(u"异常输出：{}".format(dec_data))
                        elif len_dec_data == 2:
                            if dec_data[1] != u"零":
                                if int_data == u"零":
                                    output = dec_data[1] + u"角"
                                else:
                                    output = int_data + u"元" + dec_data[1] + u"角"
                            else:
                                output = int_data + u"元整"
                        else:
                            if dec_data[1] != u"零":
                                if dec_data[2] != u"零":
                                    if int_data == u"零":
                                        output = dec_data[1] + u"角" + dec_data[2] + u"分"
                                    else:
                                        output = int_data + u"元" + dec_data[1] + u"角" + dec_data[2] + u"分"
                                else:
                                    if int_data == u"零":
                                        output = dec_data[1] + u"角"
                                    else:
                                        output = int_data + u"元" + dec_data[1] + u"角"
                            else:
                                if dec_data[2] != u"零":
                                    if int_data == u"零":
                                        output = dec_data[2] + u"分"
                                    else:
                                        output = int_data + u"元" + u"零" + dec_data[2] + u"分"
                                else:
                                    output = int_data + u"元整"
                    else:
                        output = self.__integer_convert(integer_data, mode) + self.__decimal_convert(decimal_data, mode)
                else:
                    raise ValueError(u"输入格式错误：{}！".format(inputs))
        else:
            raise ValueError(u"输入数据为空！")

        return sign + output

    def __direct_convert(self, inputs):
        _output = u""
        for d in inputs:
            if d == u".":
                _output += u"点"
            else:
                _output += self.number_low[int(d)]
        return _output

    @staticmethod
    def __number_to_string(number_data):
        # 小数处理：python 会自动把 0.00005 转化成 5e-05，因此 str(0.00005) != "0.00005"
        string_data = str(number_data)
        if u"e" in string_data:
            string_data_list = string_data.split(u"e")
            string_key = string_data_list[0]
            string_value = string_data_list[1]
            if string_value[0] == u"-":
                string_data = u"0." + u"0" * (int(string_value[1:]) - 1) + string_key
            else:
                string_data = string_key + u"0" * int(string_value)
        return string_data

    def __check_inputs_is_valid(self, check_data):
        # 检查输入数据是否在规定的字典中
        all_check_keys = self.all_num + u".-"
        for data in check_data:
            if data not in all_check_keys:
                raise ValueError(u"输入的数据不在转化范围内：{}！".format(data))

    def __integer_convert(self, integer_data, mode):
        numeral_list = self.conf[u"number_{}_an2cn".format(mode)]
        unit_list = self.conf[u"unit_{}_order_an2cn".format(mode)]

        # 去除前面的 0，比如 007 => 7
        integer_data = str(int(integer_data))

        len_integer_data = len(integer_data)
        if len_integer_data > len(unit_list):
            raise ValueError(u"超出数据范围，最长支持 {} 位".format(len(unit_list)))

        output_an = u""
        for i, d in enumerate(integer_data):
            if int(d):
                output_an += numeral_list[int(d)] + unit_list[len_integer_data - i - 1]
            else:
                if not (len_integer_data - i - 1) % 4:
                    output_an += numeral_list[int(d)] + unit_list[len_integer_data - i - 1]

                if i > 0 and not output_an[-1] == u"零":
                    output_an += numeral_list[int(d)]

        output_an = output_an.replace(u"零零", u"零").replace(u"零万", u"万").replace(u"零亿", u"亿").replace(u"亿万", u"亿") \
            .strip(u"零")

        # 解决「一十几」问题
        if output_an[:2] in [u"一十"]:
            output_an = output_an[1:]

        # 0 - 1 之间的小数
        if not output_an:
            output_an = u"零"

        return output_an

    def __decimal_convert(self, decimal_data, o_mode):
        len_decimal_data = len(decimal_data)

        if len_decimal_data > 16:
            print(u"注意：小数部分长度为 {} ，将自动截取前 16 位有效精度！".format(len_decimal_data))
            decimal_data = decimal_data[:16]

        if len_decimal_data:
            output_an = u"点"
        else:
            output_an = u""
        numeral_list = self.conf[u"number_{}_an2cn".format(o_mode)]

        for data in decimal_data:
            output_an += numeral_list[int(data)]
        return output_an
