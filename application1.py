#-*-encoding:utf-8-*-
"""
date: 2020-02-06
topic: 分析预测结果
"""

from EpidemicLimited import *

aa = ELModel()
"""
date:	20200122
exposed:	3469.1
infectious_unknown:	544.25
infectious_unknown_new	502.25
infections_conform:	437.0
sigma:	0.139285714286
kappa:	0.1445
beta_list:	0.53	0.45	0.51
"""
data_dict = {}
data_dict["date"] = "20200122"
data_dict["exposed"] = 3469
data_dict["infections_unknown"] = 544
data_dict["infections_conform"] = 437
data_dict["infectious_unknown_new"] = 502
data_dict["sigma"] = 0.139285714286
data_dict["kappa"] = 0.1445
data_dict["beta1"] = 0.53
data_dict["beta2"] = 0.45
data_dict["beta3"] = 0.51




aa.decode_data(data_dict)
# # a_class: 人群的种类 infections_conform， infectious_unknown_new，exposed， infections_unknown
day_num = 20
tuple_list_expose = aa.predict("exposed",day_num)
tuple_list_infectious_unknown = aa.predict("infections_unknown",day_num)
tuple_list_infectious_unknown_new = aa.predict("infectious_unknown_new",day_num)
tuple_list_infections_conform = aa.predict("infections_conform",day_num)
all_list = []
for i_day in range(0, len(tuple_list_expose)):
    a = []
    date = tuple_list_expose[i_day][0]
    expose = tuple_list_expose[i_day][1]
    infectious_unknown = tuple_list_infectious_unknown[i_day][1]
    infectious_unknown_new = tuple_list_infectious_unknown_new[i_day][1]
    infections_conform = tuple_list_infections_conform[i_day][1]
    all_list.append((date, expose,infectious_unknown, infectious_unknown_new,infections_conform))

for t in all_list:
    print("\t".join([t[0], str(int(t[1])), str(int(t[2])), str(int(t[3])), str(int(t[4]))]))

