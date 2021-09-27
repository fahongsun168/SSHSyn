import numpy as np
import pandas as pd

# array数据处理
a = np.array([7, 15, 36, 39, 40, 41, 20, 18])  # 不需要从小到大排序

a = np.array([1, 1, 1, 2, 3])

# 方法一：用numpy中的percentile
median_data = np.median(a)  # 中位数
percent_data = np.percentile(a, 75)  # 25%分位数
print(median_data)
print(percent_data)

# 方法二：用pandas中的quantile
b = pd.DataFrame(a)  # 数据转化
median_data1_pd = b.median()  # 中位数
quant_data = b.quantile(0.75)  # 25%分位数
print(median_data1_pd)
print(quant_data)

