#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版科研数据库爬虫
使用webdriver-manager自动管理Chrome驱动
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
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedResearchDatabaseCrawler:
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
        """设置Chrome浏览器驱动（使用webdriver-manager）"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            # 使用webdriver-manager自动下载和管理Chrome驱动
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome驱动初始化成功")
        except Exception as e:
            logger.error(f"Chrome驱动初始化失败: {e}")
            raise
    
    def navigate_to_site(self):
        """导航到目标网站"""
        try:
            logger.info(f"正在访问: {self.base_url}")
            self.driver.get(self.base_url)
            
            # 等待页面基本加载完成
            WebDriverWait(self.driver, 30).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # 等待React应用加载完成，寻找任何包含数据的元素
            logger.info("等待React应用加载...")
            time.sleep(10)  # 给React应用更多时间加载
            
            # 检查页面是否有实际内容
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            if "You need to enable JavaScript" in body_text:
                raise Exception("页面需要JavaScript支持，但内容未正确加载")
            
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
            
            # 首先探索页面结构
            page_info = self.driver.execute_script("""
                return {
                    title: document.title,
                    bodyText: document.body.innerText.substring(0, 500),
                    hasTable: !!document.querySelector('table'),
                    hasProcessList: !!document.querySelector('.processList--table'),
                    allTables: Array.from(document.querySelectorAll('table')).length,
                    divCount: Array.from(document.querySelectorAll('div')).length,
                    reactElements: Array.from(document.querySelectorAll('[data-reactroot]')).length
                }
            """)
            
            logger.info(f"页面信息: {page_info}")
            
            # 使用正确的数据提取脚本
            data_extraction_script = """
            (() => {
                const table = document.querySelector('.processList--table');
                if (!table) return [];
                
                const rows = Array.from(table.querySelectorAll('tr'));
                const result = [];
                
                // 跳过标题行，从第二行开始
                for (let i = 1; i < rows.length; i++) {
                    const cells = Array.from(rows[i].querySelectorAll('td'));
                    if (cells.length < 7) continue;
                    
                    // 跳过副标题行（如"Lithium"这样的元素名称行）
                    const isSubtitle = rows[i].classList.contains('processList--subtitle');
                    if (isSubtitle) continue;
                    
                    const refCell = cells[6];
                    const links = Array.from(refCell.querySelectorAll('a'));
                    
                    // 只处理有实际数据的行
                    const material = cells[1].textContent.trim();
                    const reactantA = cells[2].textContent.trim();
                    
                    if (material || reactantA) {
                        result.push({
                            material: material,
                            reactantA: reactantA,
                            reactantB: cells[3].textContent.trim(),
                            reactantC: cells[4].textContent.trim(),
                            furtherReactants: cells[5].textContent.trim(),
                            references: links.map(link => ({
                                name: link.textContent.trim(),
                                url: link.href
                            }))
                        });
                    }
                }
                return result;
            })()
            """
            
            try:
                logger.info("开始提取数据...")
                raw_data = self.driver.execute_script(data_extraction_script)
                
                if not raw_data:
                    logger.warning("未提取到数据")
                    self.save_debug_info()
                    raise Exception("未能提取到数据")
                
                logger.info(f"成功提取到 {len(raw_data)} 条数据")
                
            except Exception as e:
                logger.error(f"数据提取失败: {str(e)}")
                self.save_debug_info()
                raise
                
            logger.info(f"原始数据提取完成，共 {len(raw_data)} 条记录")
            
            # 如果是调试信息（方法3），直接返回
            if isinstance(raw_data, list) and len(raw_data) > 0 and 'tagName' in raw_data[0]:
                logger.info("返回页面结构调试信息")
                return raw_data
            
            return self.process_data(raw_data)
            
        except Exception as e:
            logger.error(f"数据提取失败: {e}")
            # 保存页面源码用于调试
            self.save_debug_info()
            raise
    
    def process_data(self, raw_data):
        """处理和清理数据"""
        processed_data = []
        
        for i, item in enumerate(raw_data):
            # 跳过标题行（Lithium）
            if item['material'] == 'Lithium' and not item['reactantA']:
                continue
                
            # 创建数据记录
            record = {}
            
            # Material字段
            if item['material']:
                record['Material'] = item['material']
            
            # Reactant A字段
            if item['reactantA']:
                record['Reactant A'] = item['reactantA']
            
            # Reactant B字段（异常处理：如果没有就不记录）
            if item['reactantB']:
                record['Reactant B'] = item['reactantB']
            
            # Reactant C字段（异常处理：如果没有就不记录）
            if item['reactantC']:
                record['Reactant C'] = item['reactantC']
            
            # Further reactants字段
            if item['furtherReactants']:
                record['Further reactants'] = item['furtherReactants']
            
            # References字段（保存名称以及对应的链接地址）
            if item['references'] and len(item['references']) > 0:
                record['References'] = item['references']
            
            # 只添加有实际内容的记录
            if len(record) > 0:
                processed_data.append(record)
                
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
            
            # 打印前几条记录作为示例
            if data:
                logger.info("数据示例:")
                for i, record in enumerate(data[:3]):
                    logger.info(f"记录 {i+1}: {json.dumps(record, ensure_ascii=False, indent=2)}")
            
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
    
    def save_debug_info(self):
        """保存调试信息"""
        try:
            debug_dir = os.path.join(self.data_dir, "debug")
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            
            # 保存页面源码
            with open(os.path.join(debug_dir, "page_source.html"), 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            # 保存截图
            self.driver.save_screenshot(os.path.join(debug_dir, "error_screenshot.png"))
            
            logger.info(f"调试信息已保存到: {debug_dir}")
            
        except Exception as e:
            logger.error(f"保存调试信息失败: {e}")
    
    def run(self):
        """运行爬虫"""
        try:
            logger.info("开始运行改进版爬虫...")
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
    
    parser = argparse.ArgumentParser(description='改进版科研数据库爬虫')
    parser.add_argument('--test', action='store_true', help='测试模式，只保存前10条数据')
    parser.add_argument('--max-records', type=int, default=10, help='测试模式下的最大记录数')
    
    args = parser.parse_args()
    
    # 创建并运行爬虫
    crawler = ImprovedResearchDatabaseCrawler(test_mode=args.test, max_records=args.max_records)
    crawler.run()

if __name__ == "__main__":
    main()