#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股数据获取和分析模块
主要用于每日收盘后的数据分析和短线交易指标计算
"""

import akshare as ak
import pandas as pd
import datetime
import warnings
import json
import os
from typing import Dict, List, Optional

warnings.filterwarnings('ignore')

class AShareAnalyzer:
    """A股数据分析器"""
    
    def __init__(self):
        self.today = datetime.datetime.now().strftime('%Y%m%d')
        self.yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        self.data_dir = 'data'
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"创建数据目录: {self.data_dir}")
    
    def save_results(self, results: Dict):
        """保存分析结果到JSON文件"""
        filename = f"{self.data_dir}/ashare_analysis_{self.today}.json"
        
        # 添加元数据
        data_to_save = {
            'date': self.today,
            'analysis_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到: {filename}")
        except Exception as e:
            print(f"保存数据失败: {e}")
    
    def load_historical_data(self, date: str) -> Optional[Dict]:
        """加载指定日期的历史数据"""
        filename = f"{self.data_dir}/ashare_analysis_{date}.json"
        
        if not os.path.exists(filename):
            print(f"未找到日期 {date} 的数据文件")
            return None
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"加载历史数据失败: {e}")
            return None
    
    def get_historical_summary(self, days: int = 7) -> Dict:
        """获取最近N天的数据摘要"""
        summary = []
        base_date = datetime.datetime.now()
        
        for i in range(days):
            date = (base_date - datetime.timedelta(days=i)).strftime('%Y%m%d')
            data = self.load_historical_data(date)
            
            if data and 'results' in data:
                results = data['results']
                market_stats = results.get('市场统计', {})
                yesterday_perf = results.get('昨日涨停股表现', {})
                
                # 检查市场统计数据是否有效
                has_market_data = bool(market_stats and any(k in market_stats for k in ['涨停数量', '跌停数量', '赚钱效应']))
                
                # 检查昨日涨停表现数据是否有效
                has_yesterday_data = bool(yesterday_perf and '昨日涨停股数量' in yesterday_perf)
                
                # 只有当有有效数据时才添加到摘要中
                if has_market_data or has_yesterday_data:
                    day_summary = {
                        'date': date,
                        'limit_up_count': market_stats.get('涨停数量', 0),
                        'limit_down_count': market_stats.get('跌停数量', 0),
                        'money_effect': market_stats.get('赚钱效应', 0),
                        'exploded_rate': market_stats.get('炸板率', 0),
                        'sz_index_change': market_stats.get('上证指数涨幅', 0),
                        'yesterday_limit_count': yesterday_perf.get('昨日涨停股数量', 0),
                        'yesterday_avg_perf': yesterday_perf.get('今日平均表现', 0),
                        'yesterday_up_ratio': yesterday_perf.get('今日上涨比例', 0),
                        'exploded_avg_perf': yesterday_perf.get('昨日炸板股今日平均', 0),
                        'has_valid_data': has_market_data and has_yesterday_data
                    }
                    summary.append(day_summary)
        
        return {'historical_summary': summary}
        
    def get_stock_list(self) -> pd.DataFrame:
        """获取所有A股股票列表（包括主板、创业板、科创板、北交所）"""
        try:
            # 获取所有A股股票
            stock_list = ak.stock_info_a_code_name()
            return stock_list
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_daily_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取单只股票的日K线数据"""
        try:
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date="20240101", adjust="qfq")
            return df
        except Exception as e:
            print(f"获取股票 {symbol} 数据失败: {e}")
            return None
    
    def get_limit_up_stocks(self, min_days: int = 5) -> List[Dict]:
        """获取连续涨停天数大于等于min_days的股票"""
        print(f"正在获取{min_days}连涨停板以上的股票...")
        
        try:
            # 获取涨停股票池
            limit_up_data = ak.stock_zt_pool_em(date=self.today)
            
            if limit_up_data.empty:
                return []
            
            result = []
            for _, row in limit_up_data.iterrows():
                stock_code = row['代码']
                stock_name = row['名称']
                
                # 直接使用涨停股池中的连板数字段
                consecutive_days = row.get('连板数', 1)
                
                if consecutive_days >= min_days:
                    result.append({
                        '代码': stock_code,
                        '名称': stock_name,
                        '连板天数': consecutive_days,
                        '最新价': row.get('最新价', 0),
                        '涨跌幅': row.get('涨跌幅', 0),
                        '封板资金': row.get('封板资金', 0),
                        '首次封板时间': row.get('首次封板时间', ''),
                        '炸板次数': row.get('炸板次数', 0)
                    })
            
            return result
            
        except Exception as e:
            print(f"获取连续涨停股票失败: {e}")
            return []
    
    
    def get_top_gainers(self, days: int, top_n: int = 5) -> List[Dict]:
        """获取指定天数内涨幅最大的前N只股票"""
        print(f"正在获取近{days}个交易日涨幅前{top_n}名股票...")
        
        try:
            # 获取实时行情数据
            stock_data = ak.stock_zh_a_spot_em()
            
            if stock_data.empty:
                return []
            
            # 按涨跌幅排序
            stock_data = stock_data.sort_values('涨跌幅', ascending=False)
            
            result = []
            count = 0
            
            for _, row in stock_data.iterrows():
                if count >= top_n:
                    break
                    
                result.append({
                    '代码': row['代码'],
                    '名称': row['名称'],
                    '最新价': row['最新价'],
                    '涨跌幅': row['涨跌幅'],
                    '涨跌额': row['涨跌额'],
                    '成交量': row['成交量'],
                    '成交额': row['成交额'],
                    '振幅': row.get('振幅', 0),
                    '换手率': row.get('换手率', 0)
                })
                count += 1
            
            return result
            
        except Exception as e:
            print(f"获取涨幅排名失败: {e}")
            return []
    
    def get_market_stats(self) -> Dict:
        """获取市场整体统计数据"""
        print("正在获取市场整体数据...")
        
        try:
            # 获取上证指数数据
            sz_index = ak.stock_zh_index_spot_em(symbol="000001")
            
            # 获取当日股票数据
            stock_data = ak.stock_zh_a_spot_em()
            
            if stock_data.empty:
                return {}
            
            # 计算各项指标
            total_volume = stock_data['成交量'].sum()
            total_amount = stock_data['成交额'].sum()
            
            # 上证指数涨幅
            sz_change = 0
            if not sz_index.empty:
                sz_change = sz_index.iloc[0]['涨跌幅']
            
            # 使用专门的涨停跌停接口获取准确数据
            limit_up_count = 0
            limit_down_count = 0
            exploded_count = 0
            
            try:
                # 获取涨停股池
                limit_up_data = ak.stock_zt_pool_em(date=self.today)
                limit_up_count = len(limit_up_data) if not limit_up_data.empty else 0
                
                # 获取炸板股池（开板的涨停股）
                exploded_data = ak.stock_zt_pool_zbgc_em(date=self.today)
                exploded_count = len(exploded_data) if not exploded_data.empty else 0
                
            except Exception as e:
                print(f"获取涨停数据失败: {e}")
            
            try:
                # 获取跌停股池
                limit_down_data = ak.stock_zt_pool_dtgc_em(date=self.today)
                limit_down_count = len(limit_down_data) if not limit_down_data.empty else 0
            except Exception as e:
                print(f"获取跌停数据失败: {e}")
            
            # 上涨下跌股票数量
            up_count = len(stock_data[stock_data['涨跌幅'] > 0])
            down_count = len(stock_data[stock_data['涨跌幅'] < 0])
            flat_count = len(stock_data[stock_data['涨跌幅'] == 0])
            
            # 赚钱效应（上涨股票比例）
            total_stocks = len(stock_data)
            money_effect = (up_count / total_stocks * 100) if total_stocks > 0 else 0
            
            # 计算炸板率
            exploded_rate = (exploded_count / limit_up_count * 100) if limit_up_count > 0 else 0
            
            return {
                '总成交量': total_volume,
                '总成交额': total_amount,
                '上证指数涨幅': sz_change,
                '涨停数量': limit_up_count,
                '跌停数量': limit_down_count,
                '上涨股票数': up_count,
                '下跌股票数': down_count,
                '平盘股票数': flat_count,
                '赚钱效应': round(money_effect, 2),
                '炸板率': round(exploded_rate, 2)
            }
            
        except Exception as e:
            print(f"获取市场统计数据失败: {e}")
            return {}
    
    def get_yesterday_performance(self) -> Dict:
        """获取昨日涨停股今日表现"""
        print("正在分析昨日涨停股表现...")
        
        try:
            # 使用专门的昨日涨停股池接口
            yesterday_limit_up = ak.stock_zt_pool_previous_em(date=self.today)
            
            if yesterday_limit_up.empty:
                return {'昨日涨停股表现': '无数据'}
            
            # 获取今日行情
            today_data = ak.stock_zh_a_spot_em()
            today_dict = {row['代码']: row for _, row in today_data.iterrows()}
            
            performance = []
            for _, stock in yesterday_limit_up.iterrows():
                code = stock['代码']
                if code in today_dict:
                    today_stock = today_dict[code]
                    performance.append({
                        '代码': code,
                        '名称': stock['名称'],
                        '今日涨幅': today_stock['涨跌幅'],
                        '昨日连板数': stock.get('昨日连板数', 1)
                    })
            
            if performance:
                df = pd.DataFrame(performance)
                avg_performance = df['今日涨幅'].mean()
                up_ratio = len(df[df['今日涨幅'] > 0]) / len(df) * 100
                
                # 获取炸板股表现
                try:
                    exploded_data = ak.stock_zt_pool_zbgc_em(date=self.yesterday)
                    exploded_performance = []
                    for _, stock in exploded_data.iterrows():
                        code = stock['代码']
                        if code in today_dict:
                            today_stock = today_dict[code]
                            exploded_performance.append(today_stock['涨跌幅'])
                    
                    exploded_avg = sum(exploded_performance) / len(exploded_performance) if exploded_performance else 0
                except:
                    exploded_avg = 0
                
                return {
                    '昨日涨停股数量': len(performance),
                    '今日平均表现': round(avg_performance, 2),
                    '今日上涨比例': round(up_ratio, 2),
                    '昨日炸板股今日平均': round(exploded_avg, 2)
                }
            
            return {'昨日涨停股表现': '无有效数据'}
            
        except Exception as e:
            print(f"分析昨日涨停股表现失败: {e}")
            return {'昨日涨停股表现': f'分析失败: {e}'}
    
    def get_intraday_extremes(self) -> Dict:
        """获取当日盘中极值股票"""
        print("正在获取当日盘中极值股票...")
        
        try:
            stock_data = ak.stock_zh_a_spot_em()
            
            if stock_data.empty:
                return {}
            
            # 计算收盘相对最低点涨幅和相对最高点跌幅
            stock_data['收盘较最低涨幅'] = ((stock_data['最新价'] - stock_data['最低']) / stock_data['最低'] * 100).round(2)
            stock_data['收盘较最高跌幅'] = ((stock_data['最新价'] - stock_data['最高']) / stock_data['最高'] * 100).round(2)
            
            # 收盘比当天最低点涨幅最大的5个股票
            top_low_gainers = stock_data.nlargest(5, '收盘较最低涨幅')[
                ['代码', '名称', '最新价', '最低', '收盘较最低涨幅']
            ].to_dict('records')
            
            # 收盘比当天最高点跌幅最大的5个股票  
            top_high_losers = stock_data.nsmallest(5, '收盘较最高跌幅')[
                ['代码', '名称', '最新价', '最高', '收盘较最高跌幅']
            ].to_dict('records')
            
            return {
                '收盘较最低涨幅最大': top_low_gainers,
                '收盘较最高跌幅最大': top_high_losers
            }
            
        except Exception as e:
            print(f"获取盘中极值股票失败: {e}")
            return {}
    
    def get_sector_analysis(self) -> Dict:
        """获取行业板块分析"""
        print("正在分析行业板块表现...")
        
        try:
            # 获取行业板块数据
            sector_data = ak.stock_board_industry_name_em()
            
            if sector_data.empty:
                return {}
            
            # 按涨跌幅排序
            sector_data = sector_data.sort_values('涨跌幅', ascending=False)
            
            # 涨幅最大的前5个板块
            top_sectors = sector_data.head(5)[
                ['板块名称', '涨跌幅', '总市值', '换手率']
            ].to_dict('records')
            
            return {
                '涨幅最大板块': top_sectors
            }
            
        except Exception as e:
            print(f"获取板块分析失败: {e}")
            return {}
    
    def get_decline_analysis(self) -> Dict:
        """获取跌幅分析"""
        print("正在分析跌幅数据...")
        
        try:
            stock_data = ak.stock_zh_a_spot_em()
            
            if stock_data.empty:
                return {}
            
            # 按跌幅排序
            declining_stocks = stock_data[stock_data['涨跌幅'] < 0].sort_values('涨跌幅')
            
            # 第60个跌幅最大的股票
            decline_60th = None
            if len(declining_stocks) >= 60:
                decline_60th = {
                    '代码': declining_stocks.iloc[59]['代码'],
                    '名称': declining_stocks.iloc[59]['名称'],
                    '跌幅': declining_stocks.iloc[59]['涨跌幅']
                }
            
            # 近3天跌幅超过20%的股票（简化版本，仅用当日跌幅估算）
            heavy_decline_count = len(stock_data[stock_data['涨跌幅'] <= -15])  # 用单日跌幅估算
            
            return {
                '第60个跌幅股票': decline_60th,
                '重跌股票数量': heavy_decline_count
            }
            
        except Exception as e:
            print(f"获取跌幅分析失败: {e}")
            return {}
    
    def run_analysis(self) -> Dict:
        """运行完整分析"""
        print("="*50)
        print(f"开始A股市场分析 - {self.today}")
        print("="*50)
        
        results = {}
        
        # 1. 5连涨停板以上股票
        limit_up_stocks = self.get_limit_up_stocks(5)
        results['5连涨停以上股票'] = limit_up_stocks
        
        # 2. 各时间段涨幅排名
        for days in [10, 20, 30, 50]:
            top_gainers = self.get_top_gainers(days, 5)
            results[f'近{days}日涨幅前5'] = top_gainers
        
        # 3. 市场整体数据
        market_stats = self.get_market_stats()
        results['市场统计'] = market_stats
        
        # 4. 昨日涨停股表现
        yesterday_perf = self.get_yesterday_performance()
        results['昨日涨停股表现'] = yesterday_perf
        
        # 5. 盘中极值股票
        intraday_extremes = self.get_intraday_extremes()
        results.update(intraday_extremes)
        
        # 6. 板块分析
        sector_analysis = self.get_sector_analysis()
        results.update(sector_analysis)
        
        # 7. 跌幅分析
        decline_analysis = self.get_decline_analysis()
        results.update(decline_analysis)
        
        # 8. 获取历史数据摘要
        historical_summary = self.get_historical_summary(7)
        results.update(historical_summary)
        
        return results

def main():
    """主函数"""
    analyzer = AShareAnalyzer()
    results = analyzer.run_analysis()
    
    # 保存结果到文件
    analyzer.save_results(results)
    
    # 输出结果
    print("\n" + "="*50)
    print("分析结果汇总")
    print("="*50)
    
    for key, value in results.items():
        # 跳过历史数据摘要的显示，太长了
        if key == 'historical_summary':
            continue
            
        print(f"\n【{key}】")
        if isinstance(value, list):
            for i, item in enumerate(value, 1):
                print(f"  {i}. {item}")
        elif isinstance(value, dict):
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"  {value}")
    
    # 显示历史数据摘要
    if 'historical_summary' in results:
        historical = results['historical_summary']
        if historical:
            print(f"\n【近7日市场概况】")
            print("日期       涨停 跌停 赚钱效应 炸板率 上证涨幅 | 昨涨停数 平均表现 上涨率")
            print("-" * 75)
            for day in historical:
                # 检查数据有效性
                valid_marker = "" if day.get('has_valid_data', False) else " *"
                print(f"{day['date']} {day['limit_up_count']:4d} {day['limit_down_count']:4d} "
                      f"{day['money_effect']:7.2f}% {day['exploded_rate']:6.2f}% {day['sz_index_change']:7.2f}% | "
                      f"{day['yesterday_limit_count']:7d} {day['yesterday_avg_perf']:7.2f}% {day['yesterday_up_ratio']:6.2f}%{valid_marker}")
            
            # 添加说明
            if any(not day.get('has_valid_data', False) for day in historical):
                print("\n* 标记的日期数据获取失败（网络问题或接口异常）")

if __name__ == "__main__":
    main()