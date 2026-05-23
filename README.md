<div align="center">

# 🛡️ InfoSentry-CLI

**Lightweight Open Source Intelligence Aggregation & Analysis Engine**

**轻量级开源情报聚合与智能分析引擎**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Zero-Dependencies-orange)](requirements.txt)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Project Introduction

InfoSentry-CLI is a **zero-dependency**, lightweight open source intelligence (OSINT) aggregation and analysis engine designed for security researchers, system administrators, and intelligence analysts. It aggregates real-time data from multiple sources including earthquakes, aviation, weather, space launches, and cybersecurity vulnerabilities.

**Key Differentiators:**
- 🚀 **Zero Dependencies** - Pure Python standard library implementation
- 🔒 **Privacy First** - No external API keys required for basic functionality
- 🎯 **Intelligent Analysis** - Built-in correlation and pattern recognition
- 📊 **Real-time Dashboard** - Terminal-based TUI with live updates
- 🌍 **Multi-source Intelligence** - 5+ data sources with extensible architecture

### ✨ Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🌍 **Earthquake Monitor** | Real-time USGS earthquake data with magnitude filtering | ✅ |
| ✈️ **Aviation Tracker** | Live aircraft tracking via OpenSky Network | ✅ |
| 🌤️ **Weather Alerts** | Global weather conditions for major cities | ✅ |
| 🚀 **SpaceX Launches** | Upcoming rocket launch schedules | ✅ |
| 🔒 **CVE Database** | Latest cybersecurity vulnerabilities from NVD | ✅ |
| 🔗 **Correlation Engine** | Geographic and temporal event correlation | ✅ |
| 🔍 **Pattern Analysis** | Anomaly detection and trend identification | ✅ |
| 📈 **TUI Dashboard** | Interactive terminal dashboard with live refresh | ✅ |
| 📤 **Multi-format Export** | JSON, CSV, Markdown export support | ✅ |

### 🚀 Quick Start

#### Requirements
- Python 3.8 or higher
- Internet connection for data fetching

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/InfoSentry-CLI.git
cd InfoSentry-CLI

# Install locally
pip install -e .

# Or run directly
python -m infosentry --help
```

#### Basic Usage

```bash
# Fetch all intelligence data
infosentry fetch

# Launch real-time dashboard
infosentry dashboard

# Analyze data for patterns
infosentry analyze --correlations --patterns

# Export to JSON
infosentry export --format json --output report.json

# List available sources
infosentry sources
```

### 📖 Detailed Usage Guide

#### Fetch Command Options

```bash
# Fetch specific source
infosentry fetch --source earthquake

# Filter by severity
infosentry fetch --severity high

# Limit results
infosentry fetch --limit 20

# Bypass cache
infosentry fetch --no-cache
```

#### Dashboard Controls

| Key | Action |
|-----|--------|
| `q` | Quit dashboard |
| `r` | Refresh immediately |
| `s` | Show detailed summary |
| `a` | Show all events |

#### Export Formats

```bash
# JSON export
infosentry export --format json

# CSV export
infosentry export --format csv --output data.csv

# Markdown report
infosentry export --format markdown --output report.md
```

### 💡 Design Philosophy

**Why InfoSentry?**

1. **Zero Dependencies**: Unlike other OSINT tools that require dozens of packages, InfoSentry uses only Python's standard library, making it deployable anywhere.

2. **Privacy by Design**: No tracking, no telemetry, no external API keys required for core functionality.

3. **Modular Architecture**: Easy to add new data sources by extending the `BaseSource` class.

4. **Intelligent Analysis**: Built-in algorithms for geographic clustering, temporal correlation, and anomaly detection.

### 📦 Packaging & Deployment

#### As Python Package

```bash
# Build distribution
python setup.py sdist bdist_wheel

# Install from source
pip install .
```

#### Standalone Script

```bash
# Run without installation
python -m infosentry fetch
```

### 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

InfoSentry-CLI 是一个**零依赖**的轻量级开源情报(OSINT)聚合与分析引擎，专为安全研究人员、系统管理员和情报分析师设计。它聚合来自多个来源的实时数据，包括地震、航空、天气、航天发射和网络安全漏洞。

**核心差异化亮点：**
- 🚀 **零依赖设计** - 纯Python标准库实现
- 🔒 **隐私优先** - 基础功能无需外部API密钥
- 🎯 **智能分析** - 内置关联分析和模式识别
- 📊 **实时监控** - 基于终端的TUI交互式仪表盘
- 🌍 **多源情报** - 5+数据源，可扩展架构

### ✨ 核心特性

| 特性 | 描述 | 状态 |
|------|------|------|
| 🌍 **地震监测** | USGS实时地震数据，支持震级过滤 | ✅ |
| ✈️ **航空追踪** | 通过OpenSky网络实时追踪飞行器 | ✅ |
| 🌤️ **天气预警** | 全球主要城市天气状况 | ✅ |
| 🚀 **SpaceX发射** | upcoming火箭发射时间表 | ✅ |
| 🔒 **CVE数据库** | NVD最新网络安全漏洞 | ✅ |
| 🔗 **关联引擎** | 地理和时间事件关联分析 | ✅ |
| 🔍 **模式分析** | 异常检测和趋势识别 | ✅ |
| 📈 **TUI仪表盘** | 交互式终端仪表盘，实时刷新 | ✅ |
| 📤 **多格式导出** | 支持JSON、CSV、Markdown导出 | ✅ |

### 🚀 快速开始

#### 环境要求
- Python 3.8 或更高版本
- 网络连接用于获取数据

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/InfoSentry-CLI.git
cd InfoSentry-CLI

# 本地安装
pip install -e .

# 或直接运行
python -m infosentry --help
```

#### 基本用法

```bash
# 获取所有情报数据
infosentry fetch

# 启动实时监控仪表盘
infosentry dashboard

# 分析数据模式
infosentry analyze --correlations --patterns

# 导出为JSON
infosentry export --format json --output report.json

# 列出可用数据源
infosentry sources
```

### 📖 详细使用指南

#### Fetch命令选项

```bash
# 获取特定数据源
infosentry fetch --source earthquake

# 按严重程度过滤
infosentry fetch --severity high

# 限制结果数量
infosentry fetch --limit 20

# 绕过缓存
infosentry fetch --no-cache
```

#### 仪表盘控制

| 按键 | 操作 |
|------|------|
| `q` | 退出仪表盘 |
| `r` | 立即刷新 |
| `s` | 显示详细摘要 |
| `a` | 显示所有事件 |

#### 导出格式

```bash
# JSON导出
infosentry export --format json

# CSV导出
infosentry export --format csv --output data.csv

# Markdown报告
infosentry export --format markdown --output report.md
```

### 💡 设计理念

**为什么选择InfoSentry？**

1. **零依赖**: 与其他需要数十个包的OSINT工具不同，InfoSentry仅使用Python标准库，可在任何地方部署。

2. **隐私设计**: 无跟踪、无遥测、核心功能无需外部API密钥。

3. **模块化架构**: 通过扩展`BaseSource`类轻松添加新数据源。

4. **智能分析**: 内置地理聚类、时间关联和异常检测算法。

### 📦 打包与部署

#### 作为Python包

```bash
# 构建分发包
python setup.py sdist bdist_wheel

# 从源码安装
pip install .
```

#### 独立脚本

```bash
# 无需安装直接运行
python -m infosentry fetch
```

### 🤝 贡献指南

欢迎贡献！请遵循以下准则：

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加 amazing 功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

### 📄 开源协议

本项目采用 MIT 协议 - 详见 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🇹
<a name="繁體中文"></a>
## 🇹
