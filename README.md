# Research Database Crawler

一个用于爬取原子层沉积(ALD)数据库的Python工具，能够从 https://www.atomiclimits.com/alddatabase/ 网站提取ALD工艺和参考文献信息。

## 功能特性

- **API直接访问**: 快速获取完整数据库内容（2272条工艺记录）
- **网页爬取**: 备用的Selenium WebDriver方式
- **多格式输出**: 同时支持JSON和Excel格式
- **参考文献链接**: 自动生成DOI对应的URL链接
- **数据统计**: 生成详细的统计分析报告
- **格式转换**: 独立的JSON转Excel转换工具

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### API爬虫（推荐）

```bash
# 完整数据爬取
python3 api_crawler.py

# 测试模式（5条记录）
python3 api_crawler.py --test

# 指定记录数
python3 api_crawler.py --test --max-records 10
```

### 网页爬虫（备用）

```bash
# 测试模式
python3 final_crawler.py --test

# 完整爬取
python3 final_crawler.py --full
```

### JSON转Excel转换

```bash
# 转换单个文件
python3 json_to_excel.py data/api_full_data_20250708_141211.json

# 批量转换
python3 json_to_excel.py --batch

# 列出可用文件
python3 json_to_excel.py --list
```

## 输出文件

```
data/
├── api_full_data_YYYYMMDD_HHMMSS.json   # 完整数据（JSON）
├── api_full_data_YYYYMMDD_HHMMSS.xlsx   # 完整数据（Excel）
├── api_latest_data.json                 # 最新数据（JSON）
├── api_latest_data.xlsx                 # 最新数据（Excel）
└── api_statistics_YYYYMMDD_HHMMSS.json  # 统计报告
```

## 数据格式

### JSON格式示例

```json
[
  {
    "process_id": "1",
    "material": "ZrO2",
    "reactant_a": "ZrI4",
    "reactant_b": "H2O2",
    "contributor": "Smith",
    "reviewed": true,
    "references": [
      {
        "doi": "10.1002/1521-3862(20020503)8:3<105::AID-CVDE105>3.0.CO;2-E",
        "url": "https://doi.org/10.1002/1521-3862(20020503)8:3<105::AID-CVDE105>3.0.CO;2-E",
        "author": "Forsgren",
        "citations": "15"
      }
    ]
  }
]
```

### Excel格式

Excel文件包含三个工作表：
- **ALD工艺数据**: 主数据表，包含URL链接列
- **参考文献详情**: 详细的参考文献信息
- **数据统计**: 材料分布和统计分析

## 核心文件说明

- `api_crawler.py`: API爬虫（推荐使用）
- `final_crawler.py`: 网页爬虫
- `improved_crawler.py`: 改进版网页爬虫
- `crawler.py`: 基础网页爬虫
- `json_to_excel.py`: JSON转Excel转换工具
- `requirements.txt`: 依赖包列表

## 注意事项

1. **推荐使用API爬虫**: 速度快、数据完整、稳定性好
2. **首次运行**: 网页爬虫会自动下载Chrome驱动程序
3. **测试优先**: 建议先使用测试模式验证功能
4. **网络连接**: 确保网络连接稳定

## 故障排除

### Chrome驱动问题
```bash
pip install --upgrade webdriver-manager
```

### 权限问题
```bash
chmod 755 .
```

## 许可证

本项目仅供学习和研究使用，请遵守目标网站的使用条款。
