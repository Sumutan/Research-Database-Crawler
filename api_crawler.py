#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALD数据库API爬虫
直接从API接口获取完整数据，避免页面懒加载问题
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
import time
import pandas as pd

class ALDDatabaseAPICrawler:
    """ALD数据库API爬虫类"""
    
    def __init__(self):
        self.api_url = "https://www.atomiclimits.com/alddatabase/api/processes.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.atomiclimits.com/alddatabase/'
        })
        
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """从API获取数据"""
        try:
            print(f"正在从API获取数据: {self.api_url}")
            response = self.session.get(self.api_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            print(f"API响应成功: {data.get('success', False)}")
            
            if not data.get('success', False):
                print("API返回失败状态")
                return None
                
            processes = data.get('processes', [])
            references = data.get('references', [])
            
            print(f"获取到 {len(processes)} 条工艺记录")
            print(f"获取到 {len(references)} 条参考文献")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            print(f"未知错误: {e}")
            return None
    
    def process_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """处理和合并数据"""
        processes = raw_data.get('processes', [])
        references = raw_data.get('references', [])
        
        # 创建参考文献索引
        ref_index = {}
        for ref in references:
            process_id = ref.get('process_id')
            if process_id not in ref_index:
                ref_index[process_id] = []
            doi = ref.get('reference_doi', '')
            # 为DOI生成标准URL链接
            url = f"https://doi.org/{doi}" if doi else ''
            
            ref_index[process_id].append({
                'doi': doi,
                'url': url,
                'author': ref.get('reference_author', ''),
                'full_authors': ref.get('reference_fullAuthorList', ''),
                'citations': ref.get('reference_citations', '0'),
                'submitted': ref.get('EntrySubmitted', '')
            })
        
        # 合并工艺和参考文献数据
        processed_data = []
        for process in processes:
            process_id = process.get('process_id')
            
            # 构建统一的数据结构
            record = {
                'process_id': process_id,
                'material': process.get('process_material', ''),
                'reactant_a': process.get('process_reactantA', ''),
                'reactant_b': process.get('process_reactantB', ''),
                'reactant_c': process.get('process_reactantC', ''),
                'reactant_d': process.get('process_reactantD', ''),
                'note': process.get('process_note', ''),
                'contributor': process.get('process_contributor', ''),
                'reviewed': process.get('process_reviewed', '0') == '1',
                'references': ref_index.get(process_id, [])
            }
            
            # 过滤空记录
            if record['material'] or record['reactant_a'] or record['reactant_b']:
                processed_data.append(record)
        
        print(f"处理完成，有效记录数: {len(processed_data)}")
        return processed_data
    
    def save_data(self, data: List[Dict[str, Any]], filename: str = None, test_mode: bool = False, max_records: int = None) -> str:
        """保存数据到文件"""
        # 确保数据目录存在
        os.makedirs('data', exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if filename is None:
            if test_mode:
                filename = f'data/api_test_data_{timestamp}.json'
            else:
                filename = f'data/api_full_data_{timestamp}.json'
        
        # 限制记录数（测试模式或指定最大记录数）
        if test_mode and max_records is None:
            max_records = 10
        
        save_data = data[:max_records] if max_records else data
        
        # 保存数据
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到: {filename}")
        print(f"保存记录数: {len(save_data)}")
        
        # 同时保存最新版本（不带时间戳）
        latest_filename = 'data/api_latest_data.json'
        with open(latest_filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def save_to_excel(self, data: List[Dict[str, Any]], filename: str = None, test_mode: bool = False, max_records: int = None) -> str:
        """保存数据到Excel文件"""
        # 确保数据目录存在
        os.makedirs('data', exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if filename is None:
            if test_mode:
                filename = f'data/api_test_data_{timestamp}.xlsx'
            else:
                filename = f'data/api_full_data_{timestamp}.xlsx'
        
        # 限制记录数（测试模式或指定最大记录数）
        if test_mode and max_records is None:
            max_records = 10
        
        save_data = data[:max_records] if max_records else data
        
        # 准备Excel数据
        excel_data = []
        for record in save_data:
            # 基础信息
            base_info = {
                '工艺ID': record.get('process_id', ''),
                '材料': record.get('material', ''),
                '反应物A': record.get('reactant_a', ''),
                '反应物B': record.get('reactant_b', ''),
                '反应物C': record.get('reactant_c', ''),
                '反应物D': record.get('reactant_d', ''),
                '备注': record.get('note', ''),
                '贡献者': record.get('contributor', ''),
                '已审核': '是' if record.get('reviewed', False) else '否',
                '参考文献数量': len(record.get('references', []))
            }
            
            # 处理参考文献
            references = record.get('references', [])
            if references:
                # 合并所有DOI和URL
                dois = [ref.get('doi', '') for ref in references if ref.get('doi', '')]
                urls = [ref.get('url', '') for ref in references if ref.get('url', '')]
                authors = [ref.get('author', '') for ref in references if ref.get('author', '')]
                
                base_info['DOI列表'] = '; '.join(dois) if dois else ''
                base_info['URL链接'] = '; '.join(urls) if urls else ''
                base_info['作者列表'] = '; '.join(authors) if authors else ''
                base_info['总引用数'] = sum(int(ref.get('citations', '0')) for ref in references if ref.get('citations', '0').isdigit())
            else:
                base_info['DOI列表'] = ''
                base_info['URL链接'] = ''
                base_info['作者列表'] = ''
                base_info['总引用数'] = 0
            
            excel_data.append(base_info)
        
        # 创建DataFrame并保存到Excel
        df = pd.DataFrame(excel_data)
        
        # 使用ExcelWriter来设置格式
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 主数据表
            df.to_excel(writer, sheet_name='ALD工艺数据', index=False)
            
            # 获取工作表对象进行格式设置
            worksheet = writer.sheets['ALD工艺数据']
            
            # 自动调整列宽
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # 最大宽度50
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # 如果有参考文献数据，创建详细的参考文献表
            if any(record.get('references') for record in save_data):
                ref_data = []
                for record in save_data:
                    process_id = record.get('process_id', '')
                    material = record.get('material', '')
                    for ref in record.get('references', []):
                        ref_data.append({
                            '工艺ID': process_id,
                            '材料': material,
                            'DOI': ref.get('doi', ''),
                            'URL链接': ref.get('url', ''),
                            '作者': ref.get('author', ''),
                            '完整作者列表': ref.get('full_authors', ''),
                            '引用数': ref.get('citations', '0'),
                            '提交日期': ref.get('submitted', '')
                        })
                
                if ref_data:
                    ref_df = pd.DataFrame(ref_data)
                    ref_df.to_excel(writer, sheet_name='参考文献详情', index=False)
                    
                    # 调整参考文献表格式
                    ref_worksheet = writer.sheets['参考文献详情']
                    for column in ref_worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 60)  # 参考文献表最大宽度60
                        ref_worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Excel数据已保存到: {filename}")
        print(f"保存记录数: {len(save_data)}")
        
        # 同时保存最新版本（不带时间戳）
        latest_filename = 'data/api_latest_data.xlsx'
        df.to_excel(latest_filename, index=False)
        
        return filename
    
    def generate_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成数据统计信息"""
        stats = {
            'total_records': len(data),
            'materials': {},
            'reactants': {},
            'contributors': {},
            'reviewed_count': 0,
            'with_references': 0,
            'total_references': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        for record in data:
            # 材料统计
            material = record.get('material', '').strip()
            if material:
                stats['materials'][material] = stats['materials'].get(material, 0) + 1
            
            # 反应物统计
            for reactant_key in ['reactant_a', 'reactant_b', 'reactant_c', 'reactant_d']:
                reactant = record.get(reactant_key, '').strip()
                if reactant:
                    stats['reactants'][reactant] = stats['reactants'].get(reactant, 0) + 1
            
            # 贡献者统计
            contributor = record.get('contributor', '').strip()
            if contributor:
                stats['contributors'][contributor] = stats['contributors'].get(contributor, 0) + 1
            
            # 审核状态统计
            if record.get('reviewed', False):
                stats['reviewed_count'] += 1
            
            # 参考文献统计
            references = record.get('references', [])
            if references:
                stats['with_references'] += 1
                stats['total_references'] += len(references)
        
        # 排序统计结果
        stats['top_materials'] = dict(sorted(stats['materials'].items(), key=lambda x: x[1], reverse=True)[:20])
        stats['top_reactants'] = dict(sorted(stats['reactants'].items(), key=lambda x: x[1], reverse=True)[:20])
        stats['top_contributors'] = dict(sorted(stats['contributors'].items(), key=lambda x: x[1], reverse=True)[:10])
        
        return stats
    
    def save_statistics(self, stats: Dict[str, Any], test_mode: bool = False) -> str:
        """保存统计信息"""
        os.makedirs('data', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if test_mode:
            filename = f'data/api_test_statistics_{timestamp}.json'
        else:
            filename = f'data/api_statistics_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"统计信息已保存到: {filename}")
        return filename
    
    def run(self, test_mode: bool = False, max_records: int = None) -> bool:
        """运行爬虫"""
        print("=== ALD数据库API爬虫启动 ===")
        print(f"测试模式: {test_mode}")
        if max_records:
            print(f"最大记录数: {max_records}")
        
        # 获取原始数据
        raw_data = self.fetch_data()
        if not raw_data:
            print("数据获取失败")
            return False
        
        # 处理数据
        processed_data = self.process_data(raw_data)
        if not processed_data:
            print("数据处理失败")
            return False
        
        # 保存数据
        data_file = self.save_data(processed_data, test_mode=test_mode, max_records=max_records)
        
        # 保存Excel文件（默认启用）
        excel_file = self.save_to_excel(processed_data, test_mode=test_mode, max_records=max_records)
        
        # 生成和保存统计信息
        stats = self.generate_statistics(processed_data[:max_records] if max_records else processed_data)
        stats_file = self.save_statistics(stats, test_mode=test_mode)
        
        # 显示示例数据
        print("\n=== 数据示例 ===")
        for i, record in enumerate(processed_data[:3]):
            print(f"\n记录 {i+1}:")
            print(f"  材料: {record['material']}")
            print(f"  反应物A: {record['reactant_a']}")
            print(f"  反应物B: {record['reactant_b']}")
            if record['reactant_c']:
                print(f"  反应物C: {record['reactant_c']}")
            if record['reactant_d']:
                print(f"  反应物D: {record['reactant_d']}")
            print(f"  参考文献数: {len(record['references'])}")
            if record['references']:
                print(f"  首个DOI: {record['references'][0].get('doi', 'N/A')}")
        
        print(f"\n=== 爬取完成 ===")
        print(f"总记录数: {stats['total_records']}")
        print(f"已审核记录: {stats['reviewed_count']}")
        print(f"包含参考文献的记录: {stats['with_references']}")
        print(f"总参考文献数: {stats['total_references']}")
        print(f"JSON数据文件: {data_file}")
        print(f"Excel数据文件: {excel_file}")
        print(f"统计文件: {stats_file}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='ALD数据库API爬虫')
    parser.add_argument('--test', action='store_true', help='测试模式（限制记录数）')
    parser.add_argument('--max-records', type=int, help='最大记录数')
    
    args = parser.parse_args()
    
    crawler = ALDDatabaseAPICrawler()
    success = crawler.run(test_mode=args.test, max_records=args.max_records)
    
    if success:
        print("\n爬虫运行成功！")
    else:
        print("\n爬虫运行失败！")
        exit(1)

if __name__ == '__main__':
    main()