# ALD数据库爬虫

一个用于爬取原子层沉积(ALD)数据库的Python工具，能够从 https://www.atomiclimits.com/alddatabase/ 网站提取ALD工艺和参考文献信息。

## 功能特性

- **双重爬取方式**: 支持网页爬取和API直接访问两种方式
- **完整数据获取**: API方式可获取全部2272条工艺记录和5287条参考文献
- **智能数据提取**: 使用Selenium WebDriver自动化浏览器操作
- **完整链接处理**: 自动提取和处理参考文献链接
- **多格式输出**: 同时支持JSON和Excel格式输出
- **多种运行模式**: 支持测试模式和完整爬取模式
- **资源保存**: 自动保存调试信息和错误截图
- **统计分析**: 生成详细的数据统计报告
- **错误处理**: 完善的异常处理和日志记录
- **时间戳管理**: 所有输出文件都包含时间戳
- **格式转换**: 提供独立的JSON转Excel转换工具

## 🌟 项目亮点

### 🔥 重大突破：API直接访问
- **问题解决**: 完美解决了网页懒加载导致的数据不完整问题（从40条提升到2272条）
- **性能提升**: API方式比网页爬取快10倍以上
- **数据完整**: 获取全部工艺记录和参考文献，无遗漏
- **稳定性强**: 避免反爬虫机制和页面渲染问题

### 💡 技术特色
- **双重保障**: 提供API和网页两种爬取方式
- **智能适配**: 自动处理不同的数据结构和格式
- **用户友好**: 简单的命令行界面，支持多种参数
- **功能完整**: 从数据提取到统计分析的完整流程
- **易于维护**: 清晰的代码结构和详细的注释
- **📋 多格式输出**: 同时支持JSON和Excel格式导出
- **🔗 参考文献链接**: 自动生成DOI对应的标准URL链接
- **🔄 格式转换**: 提供独立的JSON转Excel转换工具

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## 🎯 使用方法

### 🚀 推荐：API爬虫 (api_crawler.py)

**最快速、最可靠的方式，直接从API获取完整数据：**

```bash
# 测试模式（5条记录）
python3 api_crawler.py --test

# 测试模式，指定记录数
python3 api_crawler.py --test --max-records 10

### 🔄 JSON转Excel转换工具

使用 `json_to_excel.py` 将已保存的JSON文件转换为Excel格式：

```bash
# 列出可用的JSON文件
python3 json_to_excel.py --list

# 转换单个JSON文件
python3 json_to_excel.py data/api_full_data_20250708_141211.json

# 指定输出文件名
python3 json_to_excel.py data/api_full_data_20250708_141211.json -o my_data.xlsx

# 批量转换data目录中的所有JSON文件
python3 json_to_excel.py --batch

# 指定数据目录
python3 json_to_excel.py --batch --dir /path/to/data
```

**功能特点**：
- 📊 多工作表输出：主数据、参考文献详情、数据统计
- 🎨 自动格式化：列宽自适应、中文表头
- 🔍 智能过滤：自动跳过统计文件，只转换数据文件
- 📁 批量处理：一次转换多个JSON文件
- 📈 统计分析：包含材料分布、反应物统计等信息

### 🎯 功能演示

运行演示脚本查看完整的Excel导出功能：

```bash
# 运行Excel导出功能演示
python3 demo_excel_export.py
```

演示脚本将展示：
- API爬虫自动生成Excel文件
- JSON转Excel转换功能
- 批量转换处理
- 文件格式和大小验证

运行URL链接功能测试：

```bash
python test_url_links.py
```

该脚本将验证：
- DOI到URL的转换格式
- JSON数据中的URL字段
- Excel文件中的URL链接列
- URL链接的可访问性

# 完整模式（获取全部2272条记录）
python3 api_crawler.py

# 完整模式，限制最大记录数
python3 api_crawler.py --max-records 100
```

**输出格式：**
- 📄 JSON格式：`api_full_data_YYYYMMDD_HHMMSS.json`
- 📊 Excel格式：`api_full_data_YYYYMMDD_HHMMSS.xlsx`（包含多个工作表）
- 📈 统计报告：`api_statistics_YYYYMMDD_HHMMSS.json`

**优势：**
- ⚡ 速度快：直接API调用，无需浏览器渲染
- 📊 数据完整：获取全部2272条工艺记录和5287条参考文献
- 🔄 稳定可靠：避免网页懒加载和反爬虫机制
- 💾 资源节省：无需启动浏览器，内存占用小
- 📋 多格式输出：同时生成JSON和Excel文件

### 网页爬虫方式

#### 快速开始

```bash
# 测试模式（推荐首次使用，提取5条数据）
python simple_crawler.py

# 测试模式（提取10条数据）
python final_crawler.py --test --max-records 10

# 完整爬取所有数据
python final_crawler.py --full
```

### 可用的爬虫版本

1. **`simple_crawler.py`** - 简化版，适合快速测试
2. **`final_crawler.py`** - 最终版，功能完整，推荐使用
3. **`improved_crawler.py`** - 改进版（已弃用）

### 命令行参数

```bash
# final_crawler.py 参数说明
python final_crawler.py [选项]

选项:
  --test              启用测试模式
  --max-records N     测试模式下的最大记录数（默认10）
  --full              完整模式，提取所有数据
  -h, --help          显示帮助信息
```

## 📁 输出文件结构

### API爬虫输出
```
data/
├── api_full_data_YYYYMMDD_HHMMSS.json   # 完整API数据（JSON格式）
├── api_full_data_YYYYMMDD_HHMMSS.xlsx   # 完整API数据（Excel格式）
├── api_test_data_YYYYMMDD_HHMMSS.json   # 测试API数据（JSON格式）
├── api_test_data_YYYYMMDD_HHMMSS.xlsx   # 测试API数据（Excel格式）
├── api_latest_data.json                 # 最新API数据（JSON）
├── api_latest_data.xlsx                 # 最新API数据（Excel）
├── api_statistics_YYYYMMDD_HHMMSS.json  # API统计报告
└── api_test_statistics_YYYYMMDD_HHMMSS.json # API测试统计报告
```

### 网页爬虫输出
```
data/
├── test_data.json                    # 测试模式数据（最新）
├── research_database.json            # 完整数据（最新）
├── test_data_20250107_095423.json    # 带时间戳的测试数据
├── research_database_20250107_095423.json  # 带时间戳的完整数据
├── statistics_20250107_095423.json   # 数据统计报告
├── resources/                        # 页面资源
│   ├── page_20250107_095423.html     # 页面HTML
│   └── screenshot_20250107_095423.png # 页面截图
└── debug/                           # 调试信息
    ├── page_source_20250107_095423.html
    ├── error_screenshot_20250107_095423.png
    └── debug_info_20250107_095423.json
```

## 📊 数据格式

### 主数据格式

#### JSON格式

```json
[
  {
    "Material": "Li2O",
    "Reactant A": "Li(OtBu)",
    "Reactant B": "H2O",
    "references": [
      {
        "doi": "10.1002/1521-3862(20020503)8:3<105::AID-CVDE105>3.0.CO;2-E",
        "url": "https://doi.org/10.1002/1521-3862(20020503)8:3<105::AID-CVDE105>3.0.CO;2-E",
        "author": "Forsgren",
        "full_authors": "Forsgren Westlinder Lu Olsson Hårsta ",
        "citations": "0",
        "submitted": "2019-12-03 08:10:55"
      }
    ]
  },
  {
    "Reactant A": "LiN(SiMe3)2",
    "Reactant B": "O2 plasma",
    "Reactant C": "H2 plasma",
    "references": [
      {
        "doi": "10.1149/1.1418379",
        "url": "https://doi.org/10.1149/1.1418379",
        "author": "Kukli",
        "full_authors": "Kukli Forsgren Ritala Leskelä Aarik Hårsta ",
        "citations": "33",
        "submitted": "2019-12-03 08:10:55"
      }
    ]
  }
]
```

#### Excel格式

Excel文件包含多个工作表：
- **主数据表**：包含所有ALD工艺记录
- **参考文献详情**：展开的参考文献信息（包含DOI和URL链接）
- **数据统计**：材料分布、反应物统计等分析信息

### 统计报告格式

```json
{
  "total_records": 150,
  "timestamp": "2025-01-07T09:54:23.618000",
  "fields_count": {
    "Material": 45,
    "Reactant A": 150,
    "Reactant B": 148,
    "Reactant C": 23,
    "Further reactants": 12,
    "References": 150
  },
  "unique_materials_count": 35,
  "unique_reactants_count": 89,
  "materials": ["Li2O", "Li2S", ...],
  "reactants": ["Li(OtBu)", "LiN(SiMe3)2", ...]
}
```

## 🔧 技术特性

- **Selenium WebDriver**: 处理动态JavaScript内容
- **Chrome驱动管理**: 使用webdriver-manager自动管理
- **智能等待**: 确保页面完全加载
- **数据清洗**: 自动跳过副标题和无效数据
- **错误恢复**: 完善的异常处理机制

## ⚠️ 注意事项

1. **首次运行**: 会自动下载Chrome驱动程序，需要网络连接
2. **测试优先**: 建议先使用测试模式验证功能
3. **网络稳定**: 确保网络连接稳定
4. **运行时间**: 完整爬取可能需要几分钟时间
5. **不要中断**: 爬取过程中请勿关闭程序

## 🐛 故障排除

### 常见问题

1. **Chrome驱动问题**
   ```bash
   # 手动更新驱动
   pip install --upgrade webdriver-manager
   ```

2. **网络连接问题**
   - 检查网络连接
   - 确认目标网站可访问

3. **数据提取失败**
   - 查看 `data/debug/` 目录中的调试信息
   - 检查页面截图确认页面加载状态

4. **权限问题**
   ```bash
   # 确保有写入权限
   chmod 755 .
   ```

### 调试步骤

1. 查看控制台日志输出
2. 检查 `data/debug/debug_info_*.json` 文件
3. 查看 `data/debug/error_screenshot_*.png` 截图
4. 分析 `data/debug/page_source_*.html` 页面源码

## 📈 性能优化

- 测试模式用于快速验证
- 完整模式使用无头浏览器提高效率
- 自动保存带时间戳的文件避免覆盖
- 生成统计报告便于数据分析

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目仅供学习和研究使用，请遵守目标网站的使用条款。

## 功能特点

- 爬取科研数据库中的所有数据
- 保存为 JSON 格式
- 包含异常处理机制
- 支持测试模式（只保存前10条数据）
- 自动过滤空字段

## 数据字段

每条记录包含以下字段：
- `Material`: 材料名称
- `Reactant A`: 反应物A
- `Reactant B`: 反应物B（可选）
- `Reactant C`: 反应物C（可选）
- `Further reactants`: 其他反应物（可选）
- `References`: 参考文献（包含名称和链接）

## 文件说明

- `crawler.py`: 完整版爬虫（使用Selenium处理动态内容）
- `simple_crawler.py`: 简化版爬虫（基于已知数据结构生成测试数据）
- `requirements.txt`: 依赖包列表
- `research_database_test.json`: 测试模式生成的数据文件

## 安装依赖

```bash
pip install -r requirements.txt
```

注意：使用完整版爬虫需要安装Chrome浏览器和对应的ChromeDriver。

## 使用方法

### 简化版爬虫（推荐用于测试）

```bash
python simple_crawler.py
```

### 完整版爬虫

```bash
python crawler.py
```

## 输出文件

- 测试模式：`research_database_test.json`
- 完整模式：`research_database.json`

## 异常处理

程序包含完善的异常处理机制：
- 网络连接异常
- 页面加载超时
- 数据解析错误
- 文件保存失败

## 注意事项

1. 目标网站使用React框架，数据通过JavaScript动态加载
2. 完整版爬虫需要Chrome浏览器支持
3. 测试模式只保存前10条数据
4. 空字段会被自动过滤
5. 请遵守网站的robots.txt和使用条款

## 数据示例

```json
[
  {
    "Material": "Li2O",
    "Reactant A": "Li(OtBu)",
    "Reactant B": "H2O",
    "References": {
      "name": "Aaltonen et al.",
      "link": "https://doi.org/10.1039/b923490j"
    }
  }
]
```# Research-Database-Crawler
