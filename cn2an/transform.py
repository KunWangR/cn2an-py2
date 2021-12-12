# -*- coding: UTF-8 -*-
import re

from . import utils
from .cn2an import Cn2An
from .an2cn import An2Cn


class Transform(object):
    def __init__(self):
        self.conf = utils.get_default_conf()
        self.all_num = u"零一二三四五六七八九"
        self.all_unit = u"".join(list(self.conf[u"unit_cn2an"].keys()))
        self.cn2an = Cn2An().cn2an
        self.an2cn = An2Cn().an2cn
        self.cn_pattern = u"负?([{}{}]+点)?[{}{}]+".format(self.all_num, self.all_unit, self.all_num, self.all_unit)
        self.smart_cn_pattern = u"-?([0-9]+.)?[0-9]+[{}]+".format(self.all_unit)

    def transform(self, inputs, method=u"cn2an"):
        if not isinstance(inputs, unicode):
            inputs = self.__number_to_string(inputs)
        inputs = inputs.replace(u"廿", u"二十").replace(u"半", u"0.5").replace(u"两", u"2")

        if method == u"cn2an":
            # date
            inputs = re.sub(u"((({})|({}))年)?([{}十]+月)?([{}十]+日)?".format(self.smart_cn_pattern, self.cn_pattern, self.all_num, self.all_num),
                            lambda x: self.__sub_util(x.group(), u"cn2an", u"date"), inputs)
            # fraction
            inputs = re.sub(u"{}分之{}".format(self.cn_pattern, self.cn_pattern),
                            lambda x: self.__sub_util(x.group(), u"cn2an", u"fraction"), inputs)
            # percent
            inputs = re.sub(u"百分之{}".format(self.cn_pattern),
                            lambda x: self.__sub_util(x.group(), u"cn2an", u"percent"), inputs)
            # celsius
            inputs = re.sub(u"{}摄氏度".format(self.cn_pattern),
                            lambda x: self.__sub_util(x.group(), u"cn2an", u"celsius"), inputs)
            # number
            output = re.sub(self.cn_pattern,
                            lambda x: self.__sub_util(x.group(), u"cn2an", u"number"), inputs)

        elif method == u"an2cn":
            # date
            inputs = re.sub(u"(\d{2,4}年)?(\d{1,2}月)?(\d{1,2}日)?",
                            lambda x: self.__sub_util(x.group(), u"an2cn", u"date"), inputs)
            # fraction
            inputs = re.sub(u"\d+/\d+",
                            lambda x: self.__sub_util(x.group(), u"an2cn", u"fraction"), inputs)
            # percent
            inputs = re.sub(u"-?(\d+\.)?\d+%",
                            lambda x: self.__sub_util(x.group(), u"an2cn", u"percent"), inputs)
            # celsius
            inputs = re.sub(u"\d+℃",
                            lambda x: self.__sub_util(x.group(), u"an2cn", u"celsius"), inputs)
            # number
            output = re.sub(u"-?(\d+\.)?\d+",
                            lambda x: self.__sub_util(x.group(), u"an2cn", u"number"), inputs)
        else:
            raise ValueError(u"error method: {}, only support 'cn2an' and 'an2cn'!".format(method))

        return output

    def __sub_util(self, inputs, method= u"cn2an", sub_mode= u"number"):
        try:
            if inputs:
                if method == u"cn2an":
                    if sub_mode == u"date":
                        return re.sub(u"(({})|({}))".format(self.smart_cn_pattern, self.cn_pattern),
                                      lambda x: str(self.cn2an(x.group(), u"smart")), inputs)
                    elif sub_mode == u"fraction":
                        if inputs[0] != u"百":
                            frac_result = re.sub(self.cn_pattern,
                                                 lambda x: str(self.cn2an(x.group(), u"smart")), inputs)
                            numerator, denominator = frac_result.split(u"分之")
                            return u"{}/{}".format(denominator, numerator)
                        else:
                            return inputs
                    elif sub_mode == u"percent":
                        return re.sub(u"(?<=百分之){}".format(self.cn_pattern),
                                      lambda x: str(self.cn2an(x.group(), u"smart")), inputs).replace(u"百分之", u"") + u"%"
                    elif sub_mode == u"celsius":
                        return re.sub(u"{}(?=摄氏度)".format(self.cn_pattern),
                                      lambda x: str(self.cn2an(x.group(), u"smart")), inputs).replace(u"摄氏度", u"℃")
                    elif sub_mode == u"number":
                        return str(self.cn2an(inputs, u"smart"))
                    else:
                        raise Exception(u"error sub_mode: {} !".format(sub_mode))
                else:
                    if sub_mode == u"date":
                        inputs = re.sub(u"\d+(?=年)",
                                        lambda x: self.an2cn(x.group(), u"direct"), inputs)
                        return re.sub(u"\d+",
                                      lambda x: self.an2cn(x.group(), u"low"), inputs)
                    elif sub_mode == u"fraction":
                        frac_result = re.sub(u"\d+", lambda x: self.an2cn(x.group(), u"low"), inputs)
                        numerator, denominator = frac_result.split(u"/")
                        return u"{}分之{}".format(denominator, numerator)
                    elif sub_mode == u"celsius":
                        return self.an2cn(inputs[:-1], u"low") + u"摄氏度"
                    elif sub_mode == u"percent":
                        return u"百分之" + self.an2cn(inputs[:-1], u"low")
                    elif sub_mode == u"number":
                        return self.an2cn(inputs, u"low")
                    else:
                        raise Exception(u"error sub_mode: {} !".format(sub_mode))
        except Exception as e:
            print(u"WARN: {}".format(str(e)))
            return inputs

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