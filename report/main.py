"""
Main Weather Analysis System
主程式 - 控制整個天氣數據分析流程
支持自動化報告生成，可處理不同的輸入文件
"""

import os
import sys
from datetime import datetime
from data_loader import WeatherDataLoader
from weather_analyzer import WeatherAnalyzer
from report_generator import ReportGenerator

class WeatherAnalysisSystem:
    def __init__(self):
        """初始化天氣分析系統"""
        self.loader = None
        self.analyzer = None
        self.report_generator = None
        
    def analyze_file(self, excel_file, output_prefix=None):
        """
        分析單個Excel文件
        
        Args:
            excel_file (str): Excel文件路徑
            output_prefix (str): 輸出文件前綴，如果為None則自動生成
        
        Returns:
            dict: 包含生成的文件路徑的字典
        """
        print(f"\n{'='*60}")
        print(f"開始分析文件: {excel_file}")
        print(f"{'='*60}")
        
        # 如果沒有指定輸出前綴，則根據文件名自動生成
        if output_prefix is None:
            base_name = os.path.splitext(os.path.basename(excel_file))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_prefix = f"{base_name}_{timestamp}"
        
        try:
            # 1. 載入數據
            print("\n步驟 1: 載入數據")
            self.loader = WeatherDataLoader(excel_file)
            
            if not self.loader.load_weather_data():
                print("❌ 數據載入失敗")
                return None
            
            self.loader.load_precipitation_data()
            data, precip_data = self.loader.get_data()
            
            # 2. 進行分析
            print("\n步驟 2: 進行數據分析")
            self.analyzer = WeatherAnalyzer(data, precip_data)
            
            # 執行各種分析
            self.analyzer.basic_statistics()
            self.analyzer.daily_analysis()
            self.analyzer.correlation_analysis()
            self.analyzer.extreme_events()
            self.analyzer.comfort_index()
            
            # 3. 生成報告
            print("\n步驟 3: 生成報告和圖表")
            self.report_generator = ReportGenerator(
                data=data,
                daily_stats=self.analyzer.get_daily_stats(),
                analysis_results=self.analyzer.get_analysis_results(),
                output_prefix=output_prefix
            )
            
            # 生成所有報告
            generated_files = self.report_generator.generate_all_reports()
            
            # 4. 總結
            print(f"\n{'='*60}")
            print("✅ 分析完成！生成的文件:")
            print(f"📊 圖表: {generated_files['chart']}")
            print(f"📝 Markdown報告: {generated_files['markdown']}")
            if generated_files['pdf']:
                print(f"📄 PDF報告: {generated_files['pdf']}")
            else:
                print("📄 PDF報告: 生成失敗 (可能缺少ReportLab)")
            print(f"{'='*60}")
            
            return generated_files
            
        except Exception as e:
            print(f"❌ 分析過程中發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def batch_analyze(self, file_list, output_dir=None):
        """
        批量分析多個文件
        
        Args:
            file_list (list): Excel文件路徑列表
            output_dir (str): 輸出目錄，如果為None則使用當前目錄
        
        Returns:
            dict: 每個文件的分析結果
        """
        print(f"\n{'='*60}")
        print(f"開始批量分析 {len(file_list)} 個文件")
        print(f"{'='*60}")
        
        results = {}
        
        for i, excel_file in enumerate(file_list, 1):
            print(f"\n處理文件 {i}/{len(file_list)}: {excel_file}")
            
            if not os.path.exists(excel_file):
                print(f"❌ 文件不存在: {excel_file}")
                results[excel_file] = None
                continue
            
            # 生成輸出前綴
            base_name = os.path.splitext(os.path.basename(excel_file))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_prefix = f"{base_name}_{timestamp}"
            
            if output_dir:
                output_prefix = os.path.join(output_dir, output_prefix)
            
            # 分析文件
            result = self.analyze_file(excel_file, output_prefix)
            results[excel_file] = result
        
        # 批量分析總結
        print(f"\n{'='*60}")
        print("批量分析完成總結:")
        successful = sum(1 for r in results.values() if r is not None)
        failed = len(file_list) - successful
        print(f"✅ 成功: {successful} 個文件")
        print(f"❌ 失敗: {failed} 個文件")
        print(f"{'='*60}")
        
        return results
    
    def get_data_summary(self):
        """獲取當前載入數據的摘要"""
        if self.loader is None:
            return None
        return self.loader.get_data_summary()
    
    def get_analysis_results(self):
        """獲取分析結果"""
        if self.analyzer is None:
            return None
        return self.analyzer.get_analysis_results()

def main():
    """主函數 - 命令行界面"""
    print("=== 天氣數據自動分析系統 ===")
    print("支持單文件和批量分析")
    
    # 創建分析系統實例
    system = WeatherAnalysisSystem()
    
    # 檢查命令行參數
    if len(sys.argv) < 2:
        print("\n使用方法:")
        print("  單文件分析: python main.py <excel_file>")
        print("  批量分析: python main.py <file1> <file2> <file3> ...")
        print("\n示例:")
        print("  python main.py GL860+RAWDATA_2507.xlsx")
        print("  python main.py file1.xlsx file2.xlsx file3.xlsx")
        
        # 如果沒有參數，嘗試分析當前目錄下的默認文件
        default_file = "GL860+RAWDATA_2507.xlsx"
        if os.path.exists(default_file):
            print(f"\n找到默認文件 {default_file}，開始分析...")
            system.analyze_file(default_file)
        else:
            print(f"\n未找到默認文件 {default_file}")
            return
    
    elif len(sys.argv) == 2:
        # 單文件分析
        excel_file = sys.argv[1]
        if not os.path.exists(excel_file):
            print(f"❌ 文件不存在: {excel_file}")
            return
        
        system.analyze_file(excel_file)
    
    else:
        # 批量分析
        file_list = sys.argv[1:]
        system.batch_analyze(file_list)

def analyze_single_file(excel_file, output_prefix=None):
    """
    便捷函數：分析單個文件
    可以在其他Python腳本中調用
    
    Args:
        excel_file (str): Excel文件路徑
        output_prefix (str): 輸出文件前綴
    
    Returns:
        dict: 生成的文件路徑
    """
    system = WeatherAnalysisSystem()
    return system.analyze_file(excel_file, output_prefix)

def analyze_multiple_files(file_list, output_dir=None):
    """
    便捷函數：批量分析多個文件
    可以在其他Python腳本中調用
    
    Args:
        file_list (list): Excel文件路徑列表
        output_dir (str): 輸出目錄
    
    Returns:
        dict: 每個文件的分析結果
    """
    system = WeatherAnalysisSystem()
    return system.batch_analyze(file_list, output_dir)

if __name__ == "__main__":
    main()
