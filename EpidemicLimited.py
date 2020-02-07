#-*-encoding:utf-8-*-
"""
date: 2020-02-06
topic: 根据数据模拟武汉疫情发展
"""
import datetime
import os
import random

def next_date(day_0):
    date0 = datetime.datetime.strptime(day_0, '%Y%m%d')
    return (date0 + datetime.timedelta(days=1)).strftime("%Y%m%d")


class ELModel:

    def __init__(self):
        self.date_zero = '20200122'
        self.exposed_base = 2260.0  # 我们初始化1月22日的潜伏期人数为7天后1月29日的确诊人数
        self.infectious_unknown_base = 350.0  # 我们初始化为7天后的新增患者数 356
        self.infectious_conform_base = 437.0  # 1月22日确诊437例 为已知量
        self.infectious_unknown_new = 350.0 # 我们初始化为7天后的新增患者数 356
        self.beta_list =  [2.0 ] * 3
        self.sigma = 1.0/7                     #  我们初始化为7天
        self.kappa = 1.0/10                     #  初步假设发症到确诊为3天
        self.step = 0.005        # 修正步长
        self.train_data = []
        self.date_list = []

    def read_data(self,file_name='wuhan.txt',skip_first=True):
        file_path=os.path.join(os.getcwd(),"dataCollection",file_name)
        with open(file_path) as f:
            for line in f:
                date, province, city, confirm_num = line.strip("\n").split("\t")
                if date>self.date_zero :
                    if skip_first:
                        skip_first = False
                        continue
                    self.date_list.append(date)
                    self.train_data.append(int(confirm_num))

    def next_day_epidermic(self,data_dict):
        """

        :param data_dict: exposed,infections_unknown, infections_conform, infectious_unknown_new,sigma,kappa
        :return: data_dict of one day after
        """
        data_dict_next = {}
        data_dict_next["exposed"] = data_dict["exposed"] + data_dict["beta1"]*data_dict["infectious_unknown_new"]\
                                    + data_dict["beta2"] * data_dict["infections_unknown"] \
                                    + data_dict["beta3"] * data_dict["infections_conform"]
        data_dict_next["infections_unknown"] = data_dict["infections_unknown"] \
                                              + data_dict["sigma"] * data_dict["exposed"]  \
                                              - 2 * data_dict["kappa"] * data_dict["infections_unknown"]

        data_dict_next["infections_conform"] = data_dict["infections_conform"] \
                                              + 2 * data_dict["kappa"] * data_dict["infections_unknown"] \
                                              - 2 * data_dict["kappa"] * data_dict["infections_conform"]
        data_dict_next["infectious_unknown_new"] = data_dict["sigma"] * data_dict["exposed"]
        data_dict_next["sigma"] = data_dict["sigma"]
        data_dict_next["kappa"] = data_dict["kappa"]
        data_dict_next["beta1"] = data_dict["beta1"]
        data_dict_next["beta2"] = data_dict["beta2"]
        data_dict_next["beta3"] = data_dict["beta3"]
        return data_dict_next

    def encode_data(self):
        """
        把相关初始化设置 整合到字典中
        :return: data_dict
        """
        data_dict = {}
        data_dict["exposed"] = self.exposed_base
        data_dict["infections_unknown"] = self.infectious_unknown_base
        data_dict["infections_conform"] = self.infectious_conform_base
        data_dict["infectious_unknown_new"] = self.infectious_unknown_new
        data_dict["sigma"] = self.sigma
        data_dict["kappa"] = self.kappa
        data_dict["beta1"] = self.beta_list[0]
        data_dict["beta2"] = self.beta_list[1]
        data_dict["beta3"] = self.beta_list[2]
        return data_dict


    def decode_data(self, data_dict):
        """
        把数据字典中的数据解析到变量中
        :return:
        """
        self.exposed_base = data_dict["exposed"]
        self.infectious_unknown_base = data_dict["infections_unknown"]
        self.infectious_conform_base = data_dict["infections_conform"]
        self.infectious_unknown_new = data_dict["infectious_unknown_new"]
        self.sigma = data_dict["sigma"]
        self.kappa = data_dict["kappa"]
        self.beta_list[0] = data_dict["beta1"]
        self.beta_list[1] = data_dict["beta2"]
        self.beta_list[2] = data_dict["beta3"]


    def cal_err(self, base_data_dict):
        """

        :param base_data_dict: 1月22日的数据参数
        :return:
        """
        dict_list = []
        data_dict = base_data_dict
        for i in range(0, len(self.train_data)):
            data_dict = self.next_day_epidermic(data_dict)
            dict_list.append(data_dict)
        error_sum = 0
        for i in range(0, len(self.train_data)):
            error_sum += (self.train_data[i] / dict_list[i]["infections_conform"]-1)**2
        infectious_unknown_new = dict_list[0]["infectious_unknown_new"]**2/dict_list[1]["infectious_unknown_new"]
        error_sum += (1- base_data_dict["infectious_unknown_new"]/infectious_unknown_new)**2
        return error_sum

    def cal_err2(self, base_data_dict):
        """

        :param base_data_dict: 1月22日的数据参数
        :return:
        """
        dict_list = []
        data_dict = base_data_dict
        for i in range(0, len(self.train_data)):
            data_dict = self.next_day_epidermic(data_dict)
            dict_list.append(data_dict)
        error_sum = 0
        for i in range(0, len(self.train_data)):
            error_sum += (self.train_data[i] / dict_list[i]["infections_conform"]-1)**2
        infectious_unknown_new = dict_list[0]["infectious_unknown_new"]**2/dict_list[1]["infectious_unknown_new"]
        error_sum += (1- base_data_dict["infectious_unknown_new"]/infectious_unknown_new)**2
        return error_sum

    def optimizationBCD(self):
        origin_dict = self.encode_data()  # 初始化的参数
        pre_dict = self.encode_data()
        pre_err = self.cal_err(pre_dict)
        i = 0
        fresh_mark = True
        key_list = list(origin_dict.keys())
        key_list.remove("infections_conform")  # 22日的确诊人数为已知参数
        while i<50000 and fresh_mark:
            i+=1
            fresh_mark = False
            random.shuffle(key_list)
            for a_key  in key_list:
                ## 修正假设值
                new_dict = pre_dict
                new_dict[a_key] +=   self.step * origin_dict[a_key] # 增加一步
                new_err = self.cal_err(new_dict)
                if new_err<pre_err:
                    pre_dict = new_dict
                    pre_err = new_err
                    fresh_mark = True
                else:
                    new_dict[a_key] -= 2* self.step * origin_dict[a_key]  # 减少两步
                    new_err = self.cal_err(new_dict)
                    if new_err<pre_err:
                        pre_dict = new_dict
                        pre_err = new_err
                        fresh_mark = True
        self.decode_data(pre_dict)
        print i

    def predict(self, a_class= "infections_conform", num=-1):
        """

        :param a_class:  人群的种类 infections_conform， infectious_unknown_new，exposed， infections_unknown
        :param num: 从20200122开始的天数
        :return:
        """
        tuple_list = []
        day0 = self.date_zero
        data_dict = self.encode_data()
        # tuple_list.append((day0, data_dict[a_class]))
        if num == -1:
            num = len(self.train_data)
        for i in range(0, num):
            day0 = next_date(day0)
            data_dict = self.next_day_epidermic(data_dict)
            tuple_list.append((day0, data_dict[a_class]))
        return tuple_list

if __name__ == "__main__":
    aa = ELModel()
    aa.read_data()
    aa.optimizationBCD()  # 拟合历史数据
    tuple_list = aa.predict()
    for i in range(0, len(tuple_list)):
        t = tuple_list[i]
        str0 = t[0]+"\t"+str(int(t[1]))+"\t"+str(aa.train_data[i])+"\t"+str(round(aa.train_data[i]/t[1],4))
        print(str0)