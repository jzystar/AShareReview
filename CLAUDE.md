# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project named "ashare" that uses the `akshare` library for financial data analysis. The project is configured to use Python 3.12+ and uses `uv` as the package manager.

这个项目是用来通过akshare这个库来获取a股数据，主要用于每天定时盘后数据获取并且进行分析，这些数据主要用于短线交易

akshare是一个开源财经数据接口库，github地址是https://github.com/akfamily/akshare，文档地址是https://akshare.akfamily.xyz/，提供的接口可以在这里查看https://akshare.akfamily.xyz/tutorial.html
## Development Commands

- **Install dependencies**: `uv sync`
- **Run the main application**: `python fetch_data.py` or `uv run python fetch_data.py`
- **Add new dependencies**: `uv add <package-name>`
- **Update dependencies**: `uv sync --upgrade`

## Project Structure

- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Locked dependency versions managed by uv
- `.python-version` - Specifies Python 3.12 for the project

## Key Dependencies

- `akshare>=1.17.35` - Chinese financial data interface library for accessing stock market data, financial indicators, and economic data

## Notes

- This project uses `uv` instead of pip/poetry for dependency management
- The codebase is currently minimal with just a basic main function
- Virtual environment is managed in `.venv/` directory

## Requirements
1. 通过调用akshare的接口来获取a股的数据，包括创业板，科创板和北交所股票，对于akshare不支持的功能，可以去使用其他的可行方案。
2. 这些数据主要用于收盘之后的每日复盘，通过分析进行短线交易。
3. 你作为一个优秀的a股短线交易者，除了Features中要求的功能，也请提供一些你认为重要的数据，并进行获取和计算。

## Features
1. 获取5连涨停板以上的股票
2. 分别获取近10，20，30和50个交易日的最大涨幅前5名的股票
3. 获取并计算当天总成交量，量比和上证指数的涨幅
5. 获取并计算当天的涨停数量和跌停数量
4. 获取并计算当天的赚钱效应，炸板率
6. 获取并计算昨日涨停表现，昨日炸板股表现，昨日连板表现
7. 获取当天收盘比当天最低点涨幅最大的5个股票
8. 获取当天收盘比当天最高点跌幅最大的5个股票
9. 获取当天涨停数量，加上未涨停但是涨幅大于10%的股票数量最多的3个题材板块 
10. 获取当天涨幅最大的前5个题材板块，结果跟9的结果合并在一起
11. 获取近3天跌幅超过20%的股票的数量
12. 获取当天跌幅最大的第60个股票的跌幅
13. 把获得的数据保存起来，以便后面复盘使用。
