#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看历史数据工具
"""

import argparse
from fetch_data import AShareAnalyzer

def view_historical_data(date: str):
    """查看指定日期的历史数据"""
    analyzer = AShareAnalyzer()
    data = analyzer.load_historical_data(date)
    
    if not data:
        return
    
    print(f"="*50)
    print(f"A股分析数据 - {date}")
    print(f"分析时间: {data.get('analysis_time', '未知')}")
    print(f"="*50)
    
    results = data.get('results', {})
    
    # 显示主要指标
    market_stats = results.get('市场统计', {})
    if market_stats:
        print(f"\n【市场统计】")
        for k, v in market_stats.items():
            print(f"  {k}: {v}")
    
    # 显示连板股
    limit_up_stocks = results.get('5连涨停以上股票', [])
    if limit_up_stocks:
        print(f"\n【5连涨停以上股票】")
        for i, stock in enumerate(limit_up_stocks, 1):
            print(f"  {i}. {stock}")
    
    # 显示昨日涨停股表现
    yesterday_perf = results.get('昨日涨停股表现', {})
    if yesterday_perf:
        print(f"\n【昨日涨停股表现】")
        for k, v in yesterday_perf.items():
            print(f"  {k}: {v}")

def view_summary(days: int = 7):
    """查看最近N天的数据摘要"""
    analyzer = AShareAnalyzer()
    # 对于view_history.py，我们不传入current_results，让它读取所有历史文件（包括今天的）
    summary_data = analyzer.get_historical_summary(days, current_results=None)
    
    historical = summary_data.get('historical_summary', [])
    if not historical:
        print("未找到历史数据")
        return
    
    print(f"\n【近{len(historical)}日市场概况】")
    print("日期       涨停 跌停 涨跌停比          成交额 上证涨幅   量比  赚钱效应 炸板率 | 昨涨停数 涨停表现  上涨率 炸板表现")
    print("-" * 130)
    
    for day in historical:
        # 检查数据有效性
        valid_marker = "" if day.get('has_valid_data', False) else " *"
        up_down_ratio = str(day.get('up_down_ratio', 'N/A'))
        if len(up_down_ratio) > 18:
            up_down_ratio = up_down_ratio[:16] + ".."
        
        print(f"{day['date']} {day['limit_up_count']:4d} {day['limit_down_count']:4d} "
              f"{up_down_ratio:18s} {day['total_amount']:6.0f}亿 {day['sz_index_change']:7.2f}% {day['sz_amount_rate']:5.2f} "
              f"{day['money_effect']:7.2f}% {day['exploded_rate']:6.2f}%  | "
              f"{day['yesterday_limit_count']:7d} {day['yesterday_avg_perf']:8.2f}% {day['yesterday_up_ratio']:6.2f}% {day['exploded_avg_perf']:7.2f}%{valid_marker}")
    
    # 添加说明
    if any(not day.get('has_valid_data', False) for day in historical):
        print("\n* 标记的日期数据不完整")
        
    # 添加字段说明
    print("\n字段说明:")
    print("涨跌停比=涨停(主板外)+涨幅>10%非涨停:跌停(主板外)+跌幅>10%非跌停")
    print("炸板表现=昨日炸板股今日平均表现")

def main():
    parser = argparse.ArgumentParser(description='查看A股历史分析数据')
    parser.add_argument('--date', type=str, help='查看指定日期的数据 (格式: YYYYMMDD)')
    parser.add_argument('--summary', type=int, default=7, help='查看最近N天的数据摘要')
    
    args = parser.parse_args()
    
    if args.date:
        view_historical_data(args.date)
    else:
        view_summary(args.summary)

if __name__ == "__main__":
    main()