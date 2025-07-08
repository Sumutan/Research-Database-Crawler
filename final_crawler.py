#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版科研数据库爬虫
用于爬取 https://www.atomiclimits.com/alddatabase/ 的完整数据
"""

import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalResearchDatabaseCrawler:
    def __init__(self, test_mode=False, max_records=None):
        self.test_mode = test_mode
        self.max_records = max_records if max_records else (10 if test_mode else None)
        self.driver = None
        self.base_url = "https://www.atomiclimits.com/alddatabase/"
        
        # 创建数据目录
        self.data_dir = "data"
        self.resources_dir = os.path.join(self.data_dir, "resources")
        self.debug_dir = os.path.join(self.data_dir, "debug")
        
        for directory in [self.data_dir, self.resources_dir, self.debug_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # 如果不是测试模式，可以选择无头模式
            if not self.test_mode:
                chrome_options.add_argument('--headless')
            
            # 使用webdriver-manager自动管理驱动
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Chrome驱动初始化成功")
            
        except Exception as e:
            logger.error(f"驱动初始化失败: {e}")
            raise
    
    def navigate_to_site(self):
        """访问目标网站"""
        try:
            logger.info(f"正在访问: {self.base_url}")
            self.driver.get(self.base_url)
            
            # 等待页面加载
            time.sleep(8)
            
            # 检查页面是否正确加载
            title = self.driver.title
            logger.info(f"页面标题: {title}")
            
            if "Database of ALD processes" not in title:
                logger.warning("页面标题不匹配，可能加载有问题")
            
            logger.info("页面加载完成")
            
        except Exception as e:
            logger.error(f"访问网站失败: {e}")
            raise
    
    def extract_data(self):
        """提取数据"""
        try:
            logger.info("开始提取数据...")
            
            # 数据提取脚本
            extraction_script = """
            return (() => {
                const table = document.querySelector('.processList--table');
                if (!table) {
                    console.log('未找到表格');
                    return [];
                }
                
                const rows = Array.from(table.querySelectorAll('tr'));
                const result = [];
                
                console.log('找到表格，行数:', rows.length);
                
                // 跳过标题行，从第二行开始
                for (let i = 1; i < rows.length; i++) {
                    const cells = Array.from(rows[i].querySelectorAll('td'));
                    if (cells.length < 7) continue;
                    
                    // 跳过副标题行（如"Lithium"这样的元素名称行）
                    const isSubtitle = rows[i].classList.contains('processList--subtitle');
                    if (isSubtitle) {
                        console.log('跳过副标题行:', cells[1] ? cells[1].textContent.trim() : '');
                        continue;
                    }
                    
                    const refCell = cells[6];
                    const links = Array.from(refCell.querySelectorAll('a'));
                    
                    // 只处理有实际数据的行
                    const material = cells[1].textContent.trim();
                    const reactantA = cells[2].textContent.trim();
                    
                    if (material || reactantA) {
                        const record = {
                            material: material,
                            reactantA: reactantA,
                            reactantB: cells[3].textContent.trim(),
                            reactantC: cells[4].textContent.trim(),
                            furtherReactants: cells[5].textContent.trim(),
                            references: links.map(link => ({
                                name: link.textContent.trim(),
                                url: link.href
                            }))
                        };
                        result.push(record);
                    }
                }
                
                console.log('提取完成，总记录数:', result.length);
                return result;
            })();
            """
            
            raw_data = self.driver.execute_script(extraction_script)
            
            if not raw_data:
                logger.warning("未提取到数据")
                self.save_debug_info()
                raise Exception("未能提取到数据")
            
            logger.info(f"成功提取到 {len(raw_data)} 条原始数据")
            
            # 处理数据
            processed_data = self.process_data(raw_data)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"数据提取失败: {e}")
            self.save_debug_info()
            raise
    
    def process_data(self, raw_data):
        """处理和清理数据"""
        processed_data = []
        
        for i, item in enumerate(raw_data):
            # 创建数据记录
            record = {}
            
            # Material字段
            if item['material']:
                record['Material'] = item['material']
            
            # Reactant A字段
            if item['reactantA']:
                record['Reactant A'] = item['reactantA']
            
            # Reactant B字段
            if item['reactantB']:
                record['Reactant B'] = item['reactantB']
            
            # Reactant C字段
            if item['reactantC']:
                record['Reactant C'] = item['reactantC']
            
            # Further reactants字段
            if item['furtherReactants']:
                record['Further reactants'] = item['furtherReactants']
            
            # References字段
            if item['references'] and len(item['references']) > 0:
                record['References'] = item['references']
            
            # 只添加有实际内容的记录
            if len(record) > 0:
                processed_data.append(record)
                
            # 测试模式：只保存前N条数据
            if self.test_mode and self.max_records and len(processed_data) >= self.max_records:
                logger.info(f"测试模式：已达到最大记录数 {self.max_records}")
                break
        
        logger.info(f"数据处理完成，有效记录 {len(processed_data)} 条")
        return processed_data
    
    def save_data(self, data):
        """保存数据为JSON格式"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if self.test_mode:
                filename = f"test_data_{timestamp}.json"
            else:
                filename = f"research_database_{timestamp}.json"
            
            filepath = os.path.join(self.data_dir, filename)
            
            # 保存主数据文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 同时保存一个最新版本（不带时间戳）
            latest_filename = "test_data.json" if self.test_mode else "research_database.json"
            latest_filepath = os.path.join(self.data_dir, latest_filename)
            
            with open(latest_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存到: {filepath}")
            logger.info(f"最新数据: {latest_filepath}")
            logger.info(f"总共保存了 {len(data)} 条记录")
            
            # 保存统计信息
            stats = self.generate_statistics(data)
            stats_filepath = os.path.join(self.data_dir, f"statistics_{timestamp}.json")
            
            with open(stats_filepath, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            logger.info(f"统计信息已保存到: {stats_filepath}")
            
            # 打印前几条记录作为示例
            if data:
                logger.info("数据示例:")
                for i, record in enumerate(data[:2]):
                    logger.info(f"记录 {i+1}: {json.dumps(record, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            raise
    
    def generate_statistics(self, data):
        """生成数据统计信息"""
        stats = {
            'total_records': len(data),
            'timestamp': datetime.now().isoformat(),
            'fields_count': {},
            'materials': set(),
            'reactants': set()
        }
        
        for record in data:
            # 统计字段出现次数
            for field in record.keys():
                stats['fields_count'][field] = stats['fields_count'].get(field, 0) + 1
            
            # 收集材料和反应物
            if 'Material' in record:
                stats['materials'].add(record['Material'])
            
            for field in ['Reactant A', 'Reactant B', 'Reactant C']:
                if field in record:
                    stats['reactants'].add(record[field])
        
        # 转换set为list以便JSON序列化
        stats['materials'] = sorted(list(stats['materials']))
        stats['reactants'] = sorted(list(stats['reactants']))
        stats['unique_materials_count'] = len(stats['materials'])
        stats['unique_reactants_count'] = len(stats['reactants'])
        
        return stats
    
    def save_resources(self):
        """保存页面资源"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存页面HTML
            html_content = self.driver.page_source
            html_filepath = os.path.join(self.resources_dir, f"page_{timestamp}.html")
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 保存页面截图
            screenshot_filepath = os.path.join(self.resources_dir, f"screenshot_{timestamp}.png")
            self.driver.save_screenshot(screenshot_filepath)
            
            logger.info(f"页面资源已保存到: {self.resources_dir}")
            
        except Exception as e:
            logger.error(f"保存资源失败: {e}")
    
    def save_debug_info(self):
        """保存调试信息"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存页面源码
            html_filepath = os.path.join(self.debug_dir, f"page_source_{timestamp}.html")
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            # 保存截图
            screenshot_filepath = os.path.join(self.debug_dir, f"error_screenshot_{timestamp}.png")
            self.driver.save_screenshot(screenshot_filepath)
            
            # 保存调试信息到JSON
            debug_info = {
                'timestamp': datetime.now().isoformat(),
                'url': self.driver.current_url,
                'title': self.driver.title,
                'page_source_length': len(self.driver.page_source)
            }
            
            debug_filepath = os.path.join(self.debug_dir, f"debug_info_{timestamp}.json")
            with open(debug_filepath, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"调试信息已保存到: {self.debug_dir}")
            
        except Exception as e:
            logger.error(f"保存调试信息失败: {e}")
    
    def run(self):
        """运行爬虫"""
        try:
            logger.info("开始运行最终版爬虫...")
            if self.test_mode:
                logger.info(f"测试模式：只保存前 {self.max_records} 条数据")
            else:
                logger.info("生产模式：提取所有数据")
            
            # 设置浏览器驱动
            self.setup_driver()
            
            # 访问目标网站
            self.navigate_to_site()
            
            # 保存页面资源
            self.save_resources()
            
            # 提取数据
            data = self.extract_data()
            
            # 保存数据
            self.save_data(data)
            
            logger.info("爬虫运行完成！")
            return True
            
        except Exception as e:
            logger.error(f"爬虫运行失败: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("浏览器驱动已关闭")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='最终版科研数据库爬虫')
    parser.add_argument('--test', action='store_true', help='测试模式，只保存前N条数据')
    parser.add_argument('--max-records', type=int, default=10, help='测试模式下的最大记录数')
    parser.add_argument('--full', action='store_true', help='完整模式，提取所有数据')
    
    args = parser.parse_args()
    
    # 确定运行模式
    if args.full:
        test_mode = False
        max_records = None
    else:
        test_mode = args.test if args.test else True  # 默认测试模式
        max_records = args.max_records
    
    # 创建并运行爬虫
    crawler = FinalResearchDatabaseCrawler(test_mode=test_mode, max_records=max_records)
    success = crawler.run()
    
    if success:
        print("\n✓ 爬虫运行成功！")
        print(f"数据已保存到 data/ 目录")
        if test_mode:
            print("使用 --full 参数运行完整爬取")
    else:
        print("\n✗ 爬虫运行失败！")
        print("请检查 data/debug/ 目录中的调试信息")

if __name__ == "__main__":
    main()