#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON转Excel转换工具
将ALD数据库爬虫保存的JSON文件转换为Excel格式
"""

import json
import pandas as pd
import os
import argparse
from datetime import datetime
from typing import Dict, List, Any

class JSONToExcelConverter:
    """JSON转Excel转换器"""
    
    def __init__(self):
        pass
    
    def load_json_data(self, json_file: str) -> List[Dict[str, Any]]:
        """加载JSON数据"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"成功加载JSON文件: {json_file}")
            print(f"记录数: {len(data)}")
            return data
            
        except FileNotFoundError:
            print(f"错误: 文件 {json_file} 不存在")
            return []
        except json.JSONDecodeError as e:
            print(f"错误: JSON解析失败 - {e}")
            return []
        except Exception as e:
            print(f"错误: 加载文件失败 - {e}")
            return []
    
    def convert_to_excel(self, data: List[Dict[str, Any]], output_file: str = None) -> str:
        """转换数据为Excel格式"""
        if not data:
            print("错误: 没有数据可转换")
            return ""
        
        # 检查数据格式，跳过统计文件
        if not isinstance(data, list) or not data:
            print("错误: 数据格式不正确")
            return ""
        
        # 检查第一条记录是否包含工艺数据的关键字段
        first_record = data[0]
        if not isinstance(first_record, dict) or 'material' not in first_record:
            print("警告: 这似乎不是工艺数据文件，跳过转换")
            return ""
        
        # 生成输出文件名
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'data/converted_data_{timestamp}.xlsx'
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 准备Excel数据
        excel_data = []
        for record in data:
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
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
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
            if any(record.get('references') for record in data):
                ref_data = []
                for record in data:
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
            
            # 添加数据统计表
            stats_data = self.generate_statistics(data)
            stats_rows = [
                ['统计项目', '数值'],
                ['总记录数', stats_data['total_records']],
                ['已审核记录数', stats_data['reviewed_count']],
                ['包含参考文献的记录数', stats_data['with_references']],
                ['总参考文献数', stats_data['total_references']],
                ['', ''],
                ['热门材料 (前10)', '记录数'],
            ]
            
            # 添加热门材料
            for material, count in list(stats_data['top_materials'].items())[:10]:
                stats_rows.append([material, count])
            
            stats_rows.extend([['', ''], ['热门反应物 (前10)', '记录数']])
            
            # 添加热门反应物
            for reactant, count in list(stats_data['top_reactants'].items())[:10]:
                stats_rows.append([reactant, count])
            
            stats_df = pd.DataFrame(stats_rows[1:], columns=stats_rows[0])
            stats_df.to_excel(writer, sheet_name='数据统计', index=False)
            
            # 调整统计表格式
            stats_worksheet = writer.sheets['数据统计']
            stats_worksheet.column_dimensions['A'].width = 30
            stats_worksheet.column_dimensions['B'].width = 15
        
        print(f"Excel文件已保存到: {output_file}")
        print(f"转换记录数: {len(data)}")
        
        return output_file
    
    def generate_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成数据统计信息"""
        stats = {
            'total_records': len(data),
            'materials': {},
            'reactants': {},
            'contributors': {},
            'reviewed_count': 0,
            'with_references': 0,
            'total_references': 0
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
    
    def batch_convert(self, input_dir: str = 'data', pattern: str = '*.json') -> List[str]:
        """批量转换目录中的JSON文件"""
        import glob
        
        json_files = glob.glob(os.path.join(input_dir, pattern))
        converted_files = []
        
        print(f"在目录 {input_dir} 中找到 {len(json_files)} 个JSON文件")
        
        for json_file in json_files:
            print(f"\n正在转换: {json_file}")
            data = self.load_json_data(json_file)
            
            if data:
                # 生成对应的Excel文件名
                base_name = os.path.splitext(os.path.basename(json_file))[0]
                excel_file = os.path.join(input_dir, f"{base_name}.xlsx")
                
                result_file = self.convert_to_excel(data, excel_file)
                if result_file:
                    converted_files.append(result_file)
        
        return converted_files
    
    def list_available_files(self, data_dir: str = 'data') -> List[str]:
        """列出可用的JSON文件"""
        import glob
        
        if not os.path.exists(data_dir):
            print(f"数据目录 {data_dir} 不存在")
            return []
        
        json_files = glob.glob(os.path.join(data_dir, '*.json'))
        
        if not json_files:
            print(f"在 {data_dir} 目录中没有找到JSON文件")
            return []
        
        print(f"\n在 {data_dir} 目录中找到以下JSON文件:")
        for i, file in enumerate(json_files, 1):
            file_size = os.path.getsize(file)
            file_size_mb = file_size / (1024 * 1024)
            print(f"  {i}. {os.path.basename(file)} ({file_size_mb:.2f} MB)")
        
        return json_files

def main():
    parser = argparse.ArgumentParser(description='JSON转Excel转换工具')
    parser.add_argument('input_file', nargs='?', help='输入的JSON文件路径')
    parser.add_argument('-o', '--output', help='输出的Excel文件路径')
    parser.add_argument('-b', '--batch', action='store_true', help='批量转换data目录中的所有JSON文件')
    parser.add_argument('-l', '--list', action='store_true', help='列出可用的JSON文件')
    parser.add_argument('-d', '--dir', default='data', help='数据目录路径（默认: data）')
    
    args = parser.parse_args()
    
    converter = JSONToExcelConverter()
    
    # 列出可用文件
    if args.list:
        converter.list_available_files(args.dir)
        return
    
    # 批量转换
    if args.batch:
        print("开始批量转换...")
        converted_files = converter.batch_convert(args.dir)
        print(f"\n批量转换完成，共转换 {len(converted_files)} 个文件:")
        for file in converted_files:
            print(f"  - {file}")
        return
    
    # 单文件转换
    if not args.input_file:
        print("错误: 请指定输入文件或使用 --batch 进行批量转换")
        print("使用 --help 查看帮助信息")
        return
    
    if not os.path.exists(args.input_file):
        print(f"错误: 输入文件 {args.input_file} 不存在")
        return
    
    print(f"开始转换文件: {args.input_file}")
    data = converter.load_json_data(args.input_file)
    
    if data:
        output_file = converter.convert_to_excel(data, args.output)
        if output_file:
            print(f"\n转换成功！")
            print(f"输出文件: {output_file}")
        else:
            print("转换失败！")
    else:
        print("无法加载数据，转换失败！")

if __name__ == '__main__':
    main()