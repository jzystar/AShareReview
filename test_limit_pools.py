#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试涨停跌停池接口
"""

import akshare as ak
import datetime
import warnings

warnings.filterwarnings('ignore')

def test_limit_pools():
    today = datetime.datetime.now().strftime('%Y%m%d')
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    
    print(f"测试日期: {today}")
    print("="*50)
    
    # 测试涨停股池
    try:
        print("1. 测试涨停股池 (stock_zt_pool_em)")
        limit_up_data = ak.stock_zt_pool_em(date=today)
        print(f"涨停股数量: {len(limit_up_data)}")
        if not limit_up_data.empty:
            print("前5只涨停股:")
            print(limit_up_data.head()[['代码', '名称', '涨跌幅', '最新价', '连续涨停']].to_string())
    except Exception as e:
        print(f"获取涨停股池失败: {e}")
    
    print("\n")
    
    # 测试跌停股池
    try:
        print("2. 测试跌停股池 (stock_zt_pool_dtgc_em)")
        limit_down_data = ak.stock_zt_pool_dtgc_em(date=today)
        print(f"跌停股数量: {len(limit_down_data)}")
        if not limit_down_data.empty:
            print("前5只跌停股:")
            print(limit_down_data.head()[['代码', '名称', '涨跌幅', '最新价']].to_string())
    except Exception as e:
        print(f"获取跌停股池失败: {e}")
    
    print("\n")
    
    # 测试炸板股池
    try:
        print("3. 测试炸板股池 (stock_zt_pool_zbgc_em)")
        exploded_data = ak.stock_zt_pool_zbgc_em(date=today)
        print(f"炸板股数量: {len(exploded_data)}")
        if not exploded_data.empty:
            print("前5只炸板股:")
            print(exploded_data.head()[['代码', '名称', '涨跌幅', '最新价']].to_string())
    except Exception as e:
        print(f"获取炸板股池失败: {e}")
    
    print("\n")
    
    # 测试昨日涨停股池
    try:
        print("4. 测试昨日涨停股池 (stock_zt_pool_previous_em)")
        previous_data = ak.stock_zt_pool_previous_em(date=today)
        print(f"昨日涨停股数量: {len(previous_data)}")
        if not previous_data.empty:
            print("前5只昨日涨停股:")
            print(previous_data.head()[['代码', '名称', '涨跌幅', '最新价']].to_string())
    except Exception as e:
        print(f"获取昨日涨停股池失败: {e}")

if __name__ == "__main__":
    test_limit_pools()