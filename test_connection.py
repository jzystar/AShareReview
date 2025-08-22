#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试网络连接和基础数据获取
"""

import akshare as ak
import datetime
import warnings

warnings.filterwarnings('ignore')

def test_basic_connections():
    """测试基础连接"""
    today = datetime.datetime.now().strftime('%Y%m%d')
    
    print("测试网络连接和基础数据获取")
    print("="*50)
    
    # 测试1: 涨停股池（通常比较稳定）
    try:
        print("1. 测试涨停股池...")
        limit_up_data = ak.stock_zt_pool_em(date=today)
        print(f"   ✓ 成功获取涨停股数量: {len(limit_up_data)}")
        if not limit_up_data.empty:
            print(f"   前3只: {limit_up_data[['代码', '名称', '连板数']].head(3).to_string(index=False)}")
    except Exception as e:
        print(f"   ✗ 涨停股池失败: {e}")
    
    print()
    
    # 测试2: 跌停股池
    try:
        print("2. 测试跌停股池...")
        limit_down_data = ak.stock_zt_pool_dtgc_em(date=today)
        print(f"   ✓ 成功获取跌停股数量: {len(limit_down_data)}")
    except Exception as e:
        print(f"   ✗ 跌停股池失败: {e}")
    
    print()
    
    # 测试3: 昨日涨停股池
    try:
        print("3. 测试昨日涨停股池...")
        previous_data = ak.stock_zt_pool_previous_em(date=today)
        print(f"   ✓ 成功获取昨日涨停股数量: {len(previous_data)}")
    except Exception as e:
        print(f"   ✗ 昨日涨停股池失败: {e}")
    
    print()
    
    # 测试4: 股票实时数据（这个经常有网络问题）
    try:
        print("4. 测试股票实时数据...")
        stock_data = ak.stock_zh_a_spot_em()
        print(f"   ✓ 成功获取股票数量: {len(stock_data)}")
    except Exception as e:
        print(f"   ✗ 股票实时数据失败: {e}")
    
    print()
    print("="*50)
    print("如果出现网络错误，可能的解决方案:")
    print("1. 检查网络连接是否正常")
    print("2. 尝试重新运行（有时是临时网络问题）")
    print("3. 在交易时间内运行效果更好")
    print("4. 检查是否需要配置网络代理")

if __name__ == "__main__":
    test_basic_connections()