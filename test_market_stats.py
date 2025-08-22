#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试市场统计功能
"""

import akshare as ak
import datetime
import warnings

warnings.filterwarnings('ignore')

def test_market_stats():
    today = datetime.datetime.now().strftime('%Y%m%d')
    
    print(f"测试市场统计功能 - {today}")
    print("="*50)
    
    # 测试涨停数量统计
    try:
        limit_up_data = ak.stock_zt_pool_em(date=today)
        limit_up_count = len(limit_up_data) if not limit_up_data.empty else 0
        print(f"涨停股数量: {limit_up_count}")
    except Exception as e:
        print(f"获取涨停数量失败: {e}")
    
    # 测试跌停数量统计  
    try:
        limit_down_data = ak.stock_zt_pool_dtgc_em(date=today)
        limit_down_count = len(limit_down_data) if not limit_down_data.empty else 0
        print(f"跌停股数量: {limit_down_count}")
    except Exception as e:
        print(f"获取跌停数量失败: {e}")
    
    # 测试炸板数量统计
    try:
        exploded_data = ak.stock_zt_pool_zbgc_em(date=today)
        exploded_count = len(exploded_data) if not exploded_data.empty else 0
        print(f"炸板股数量: {exploded_count}")
        
        # 计算炸板率
        exploded_rate = (exploded_count / limit_up_count * 100) if limit_up_count > 0 else 0
        print(f"炸板率: {exploded_rate:.2f}%")
    except Exception as e:
        print(f"获取炸板数量失败: {e}")
    
    print("\n详细信息:")
    print("-"*30)
    
    # 显示部分涨停股详情
    if limit_up_count > 0:
        print("部分涨停股:")
        print(limit_up_data[['代码', '名称', '连板数', '炸板次数', '封板资金']].head().to_string(index=False))
    
    print()
    
    # 显示跌停股详情
    if limit_down_count > 0:
        print("跌停股:")
        print(limit_down_data[['代码', '名称', '涨跌幅', '最新价']].to_string(index=False))
    
    print()
    
    # 显示炸板股详情
    if exploded_count > 0:
        print("部分炸板股:")
        print(exploded_data[['代码', '名称', '涨跌幅', '最新价']].head().to_string(index=False))

if __name__ == "__main__":
    test_market_stats()