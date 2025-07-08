#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科研数据库爬虫
爬取 https://www.atomiclimits.com/alddatabase/ 中的所有数据
"""

import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResearchDatabaseCrawler:
    def __init__(self, test_mode=False, max_records=10):
        """
        初始化爬虫
        :param test_mode: 是否为测试模式，只保存前10条数据
        :param max_records: 测试模式下的最大记录数
        """
        self.test_mode = test_mode
        self.max_records = max_records
        self.base_url = "https://www.atomiclimits.com/alddatabase/"
        self.data_dir = "data"
        self.driver = None
        
        # 创建数据目录
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome驱动初始化成功")
        except Exception as e:
            logger.error(f"Chrome驱动初始化失败: {e}")
            raise
    
    def navigate_to_site(self):
        """导航到目标网站"""
        try:
            logger.info(f"正在访问: {self.base_url}")
            self.driver.get(self.base_url)
            
            # 等待页面加载完成
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "processList--table"))
            )
            logger.info("页面加载完成")
            
        except TimeoutException:
            logger.error("页面加载超时")
            raise
        except Exception as e:
            logger.error(f"访问网站失败: {e}")
            raise
    
    def extract_data(self):
        """提取数据"""
        try:
            logger.info("开始提取数据...")
            
            # 执行JavaScript获取数据
            script = """
            (() => {
                const table = document.querySelector('.processList--table');
                const rows = Array.from(table.querySelectorAll('tr'));
                const result = [];
                
                for (let i = 1; i < rows.length; i++) {
                    const cells = Array.from(rows[i].querySelectorAll('td'));
                    const refCell = cells[6];
                    const links = Array.from(refCell.querySelectorAll('a'));
                    
                    result.push({
                        material: cells[1].textContent.trim(),
                        reactantA: cells[2].textContent.trim(),
                        reactantB: cells[3].textContent.trim(),
                        reactantC: cells[4].textContent.trim(),
                        furtherReactants: cells[5].textContent.trim(),
                        references: links.map(link => ({
                            name: link.textContent.trim(),
                            url: link.href
                        }))
                    });
                }
                return result;
            })()
            """
            
            raw_data = self.driver.execute_script(script)
            logger.info(f"原始数据提取完成，共 {len(raw_data)} 条记录")
            
            return self.process_data(raw_data)
            
        except Exception as e:
            logger.error(f"数据提取失败: {e}")
            raise
    
    def process_data(self, raw_data):
        """处理和清理数据"""
        processed_data = []
        
        for i, item in enumerate(raw_data):
            # 跳过标题行（Lithium）
            if item['material'] == 'Lithium' and not item['reactantA']:
                continue
                
            # 创建数据记录
            record = {
                'Material': item['material'] if item['material'] else None,
                'Reactant A': item['reactantA'] if item['reactantA'] else None,
                'Reactant B': item['reactantB'] if item['reactantB'] else None,
                'Reactant C': item['reactantC'] if item['reactantC'] else None,
                'Further reactants': item['furtherReactants'] if item['furtherReactants'] else None,
                'References': item['references'] if item['references'] else []
            }
            
            # 异常处理：如果没有某些字段，就不记录这些字段
            cleaned_record = {}
            for key, value in record.items():
                if value is not None and value != "":
                    if key == 'References' and len(value) == 0:
                        continue
                    cleaned_record[key] = value
            
            if cleaned_record:  # 只添加非空记录
                processed_data.append(cleaned_record)
                
            # 测试模式：只保存前10条数据
            if self.test_mode and len(processed_data) >= self.max_records:
                logger.info(f"测试模式：已达到最大记录数 {self.max_records}")
                break
        
        logger.info(f"数据处理完成，有效记录 {len(processed_data)} 条")
        return processed_data
    
    def save_data(self, data):
        """保存数据为JSON格式"""
        try:
            filename = "test_data.json" if self.test_mode else "research_database.json"
            filepath = os.path.join(self.data_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存到: {filepath}")
            logger.info(f"总共保存了 {len(data)} 条记录")
            
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            raise
    
    def save_resources(self):
        """保存页面资源到子文件夹"""
        try:
            resources_dir = os.path.join(self.data_dir, "resources")
            if not os.path.exists(resources_dir):
                os.makedirs(resources_dir)
            
            # 保存页面HTML
            html_content = self.driver.page_source
            with open(os.path.join(resources_dir, "page.html"), 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 保存页面截图
            screenshot_path = os.path.join(resources_dir, "screenshot.png")
            self.driver.save_screenshot(screenshot_path)
            
            logger.info(f"页面资源已保存到: {resources_dir}")
            
        except Exception as e:
            logger.error(f"保存资源失败: {e}")
    
    def run(self):
        """运行爬虫"""
        try:
            logger.info("开始运行爬虫...")
            if self.test_mode:
                logger.info(f"测试模式：只保存前 {self.max_records} 条数据")
            
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
            
        except Exception as e:
            logger.error(f"爬虫运行失败: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("浏览器驱动已关闭")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='科研数据库爬虫')
    parser.add_argument('--test', action='store_true', help='测试模式，只保存前10条数据')
    parser.add_argument('--max-records', type=int, default=10, help='测试模式下的最大记录数')
    
    args = parser.parse_args()
    
    # 创建并运行爬虫
    crawler = ResearchDatabaseCrawler(test_mode=args.test, max_records=args.max_records)
    crawler.run()

if __name__ == "__main__":
    main()