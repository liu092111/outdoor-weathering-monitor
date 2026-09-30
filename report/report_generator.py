"""
Report Generator Module
負責生成可視化圖表和PDF/Markdown報告
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Import for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    PDF_AVAILABLE = True
except ImportError:
    print("Warning: ReportLab not available. PDF generation will be skipped.")
    PDF_AVAILABLE = False

class ReportGenerator:
    def __init__(self, data, daily_stats, analysis_results, output_prefix="weather_analysis"):
        """初始化報告生成器"""
        self.data = data
        self.daily_stats = daily_stats
        self.analysis_results = analysis_results
        self.output_prefix = output_prefix
        
        # 設置圖表樣式
        plt.style.use('default')
        plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def create_visualizations(self):
        """創建可視化圖表"""
        print("\n=== Creating Visualization Charts ===")
        
        fig = plt.figure(figsize=(20, 12))
        
        # 計算統計數據用於圖例
        temp_stats = {
            'mean': self.data['Temperature'].mean(),
            'max': self.data['Temperature'].max(),
            'min': self.data['Temperature'].min(),
            'std': self.data['Temperature'].std()
        }
        
        humidity_stats = {
            'mean': self.data['Humidity'].mean(),
            'max': self.data['Humidity'].max(),
            'min': self.data['Humidity'].min(),
            'std': self.data['Humidity'].std()
        }
        
        correlation = self.data['Temperature'].corr(self.data['Humidity'])
        
        # 1. 溫度時間序列
        ax1 = plt.subplot(2, 4, 1)
        line1 = ax1.plot(self.data['DateTime'], self.data['Temperature'], 'r-', alpha=0.7, linewidth=0.5, label='Temperature')[0]
        ax1.set_title('Temperature Time Series', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Temperature (°C)')
        ax1.grid(True, alpha=0.3)
        
        temp_legend = f'Temperature\nMean: {temp_stats["mean"]:.1f}°C\nMax: {temp_stats["max"]:.1f}°C\nMin: {temp_stats["min"]:.1f}°C\nStd: {temp_stats["std"]:.1f}°C\nRange: {temp_stats["max"]-temp_stats["min"]:.1f}°C'
        ax1.legend([line1], [temp_legend], loc='upper right', fontsize=8, framealpha=0.9)
        
        # 2. 濕度時間序列
        ax2 = plt.subplot(2, 4, 2)
        line2 = ax2.plot(self.data['DateTime'], self.data['Humidity'], 'b-', alpha=0.7, linewidth=0.5, label='Humidity')[0]
        ax2.set_title('Humidity Time Series', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Humidity (%)')
        ax2.grid(True, alpha=0.3)
        
        humidity_legend = f'Humidity\nMean: {humidity_stats["mean"]:.1f}%\nMax: {humidity_stats["max"]:.1f}%\nMin: {humidity_stats["min"]:.1f}%\nStd: {humidity_stats["std"]:.1f}%\nRange: {humidity_stats["max"]-humidity_stats["min"]:.1f}%'
        ax2.legend([line2], [humidity_legend], loc='upper right', fontsize=8, framealpha=0.9)
        
        # 3. 溫濕度關係散點圖（改進的顏色說明）
        ax3 = plt.subplot(2, 4, 3)
        time_hours = self.data['DateTime'].dt.hour + self.data['DateTime'].dt.minute/60
        scatter = ax3.scatter(self.data['Temperature'], self.data['Humidity'], 
                            c=time_hours, cmap='plasma', alpha=0.6, s=3)
        ax3.set_xlabel('Temperature (°C)')
        ax3.set_ylabel('Humidity (%)')
        ax3.set_title('Temperature-Humidity Relationship', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        cbar = plt.colorbar(scatter, ax=ax3, shrink=0.6, pad=0.02)
        cbar.set_label('Time of Day (Hours)', fontsize=8)
        cbar.ax.tick_params(labelsize=7)
        
        corr_legend = f'Correlation: {correlation:.3f}\n{"Strong Negative" if correlation < -0.7 else "Strong Positive" if correlation > 0.7 else "Moderate" if abs(correlation) > 0.3 else "Weak"} Relationship\n\nColor Meanings:\n🟣 Purple: Night (0-6h)\n   Cool, High Humidity\n🔵 Blue: Morning (6-12h)\n   Warming, Moderate RH\n🟢 Green: Afternoon (12-18h)\n   Hot, Low Humidity\n🟡 Yellow: Evening (18-24h)\n   Cooling, Rising RH\n\nPoints: {len(self.data):,}'
        ax3.text(0.98, 0.98, corr_legend, transform=ax3.transAxes, fontsize=6.5, 
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
        # 4. 日溫度變化
        if self.daily_stats is not None:
            ax4 = plt.subplot(2, 4, 4)
            line4 = ax4.plot(self.daily_stats['Date'], self.daily_stats['Temperature_mean'], 'ro-', markersize=4, label='Daily Mean')[0]
            ax4.fill_between(self.daily_stats['Date'], 
                           self.daily_stats['Temperature_min'], 
                           self.daily_stats['Temperature_max'], alpha=0.3, label='Min-Max Range')
            ax4.set_title('Daily Temperature Variation', fontsize=12, fontweight='bold')
            ax4.set_ylabel('Temperature (°C)')
            ax4.grid(True, alpha=0.3)
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
            
            daily_temp_legend = f'Daily Temperature\nMean: {self.daily_stats["Temperature_mean"].mean():.1f}°C\nMax Daily: {self.daily_stats["Temperature_max"].max():.1f}°C\nMin Daily: {self.daily_stats["Temperature_min"].min():.1f}°C\nAvg Range: {self.daily_stats["temp_range"].mean():.1f}°C\nMax Range: {self.daily_stats["temp_range"].max():.1f}°C'
            ax4.legend([line4], [daily_temp_legend], loc='upper right', fontsize=8, framealpha=0.9)
            
            # 5. 日濕度變化
            ax5 = plt.subplot(2, 4, 5)
            line5 = ax5.plot(self.daily_stats['Date'], self.daily_stats['Humidity_mean'], 'bo-', markersize=4, label='Daily Mean')[0]
            ax5.fill_between(self.daily_stats['Date'], 
                           self.daily_stats['Humidity_min'], 
                           self.daily_stats['Humidity_max'], alpha=0.3, label='Min-Max Range')
            ax5.set_title('Daily Humidity Variation', fontsize=12, fontweight='bold')
            ax5.set_ylabel('Humidity (%)')
            ax5.grid(True, alpha=0.3)
            plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45)
            
            daily_humidity_legend = f'Daily Humidity\nMean: {self.daily_stats["Humidity_mean"].mean():.1f}%\nMax Daily: {self.daily_stats["Humidity_max"].max():.1f}%\nMin Daily: {self.daily_stats["Humidity_min"].min():.1f}%\nAvg Range: {self.daily_stats["humidity_range"].mean():.1f}%\nMax Range: {self.daily_stats["humidity_range"].max():.1f}%'
            ax5.legend([line5], [daily_humidity_legend], loc='upper right', fontsize=8, framealpha=0.9)
        
        # 6. 溫度分布
        ax6 = plt.subplot(2, 4, 6)
        n, bins, patches = ax6.hist(self.data['Temperature'], bins=30, alpha=0.7, color='red', edgecolor='black', label='Temperature Distribution')
        ax6.set_title('Temperature Distribution', fontsize=12, fontweight='bold')
        ax6.set_xlabel('Temperature (°C)')
        ax6.set_ylabel('Frequency')
        ax6.grid(True, alpha=0.3)
        
        temp_dist_legend = f'Temperature Distribution\nMean: {temp_stats["mean"]:.1f}°C\nMedian: {self.data["Temperature"].median():.1f}°C\nStd Dev: {temp_stats["std"]:.1f}°C\nSkewness: {self.data["Temperature"].skew():.2f}\nSamples: {len(self.data):,}'
        ax6.legend([patches[0]], [temp_dist_legend], loc='upper right', fontsize=8, framealpha=0.9)
        
        # 7. 濕度分布
        ax7 = plt.subplot(2, 4, 7)
        n, bins, patches = ax7.hist(self.data['Humidity'], bins=30, alpha=0.7, color='blue', edgecolor='black', label='Humidity Distribution')
        ax7.set_title('Humidity Distribution', fontsize=12, fontweight='bold')
        ax7.set_xlabel('Humidity (%)')
        ax7.set_ylabel('Frequency')
        ax7.grid(True, alpha=0.3)
        
        humidity_dist_legend = f'Humidity Distribution\nMean: {humidity_stats["mean"]:.1f}%\nMedian: {self.data["Humidity"].median():.1f}%\nStd Dev: {humidity_stats["std"]:.1f}%\nSkewness: {self.data["Humidity"].skew():.2f}\nSamples: {len(self.data):,}'
        ax7.legend([patches[0]], [humidity_dist_legend], loc='upper right', fontsize=8, framealpha=0.9)
        
        # 8. 小時溫度模式
        ax8 = plt.subplot(2, 4, 8)
        hourly_temp = self.data.groupby('Hour')['Temperature'].mean()
        line8 = ax8.plot(hourly_temp.index, hourly_temp.values, 'ro-', markersize=6, label='Hourly Average')[0]
        ax8.set_title('Hourly Temperature Pattern', fontsize=12, fontweight='bold')
        ax8.set_xlabel('Hour of Day')
        ax8.set_ylabel('Average Temperature (°C)')
        ax8.set_xticks(range(0, 24, 3))
        ax8.grid(True, alpha=0.3)
        
        hourly_legend = f'Hourly Pattern\nPeak Hour: {hourly_temp.idxmax()}:00\nPeak Temp: {hourly_temp.max():.1f}°C\nLowest Hour: {hourly_temp.idxmin()}:00\nLowest Temp: {hourly_temp.min():.1f}°C\nDaily Range: {hourly_temp.max()-hourly_temp.min():.1f}°C'
        ax8.legend([line8], [hourly_legend], loc='upper right', fontsize=8, framealpha=0.9)
        
        plt.tight_layout()
        chart_filename = f'{self.output_prefix}_comprehensive.png'
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"Charts saved as '{chart_filename}'")
        return chart_filename
    
    def generate_markdown_report(self):
        """生成Markdown報告"""
        print("\n=== 生成Markdown報告 ===")
        
        # 從分析結果中獲取數據
        basic_stats = self.analysis_results.get('basic_stats', {})
        correlation = self.analysis_results.get('correlation', {})
        comfort = self.analysis_results.get('comfort', {})
        
        report = f"""
# 天氣數據分析報告

## 數據概況
- 監測期間: {self.data['DateTime'].min().strftime('%Y-%m-%d')} 至 {self.data['DateTime'].max().strftime('%Y-%m-%d')}
- 數據點數: {len(self.data):,} 個
- 採樣間隔: 10分鐘

## 主要發現

### 溫度特徵
- 平均溫度: {self.data['Temperature'].mean():.1f}°C
- 溫度範圍: {self.data['Temperature'].min():.1f}°C - {self.data['Temperature'].max():.1f}°C
- 日溫差: 平均 {self.daily_stats['temp_range'].mean():.1f}°C，最大 {self.daily_stats['temp_range'].max():.1f}°C

### 濕度特徵
- 平均濕度: {self.data['Humidity'].mean():.1f}%
- 濕度範圍: {self.data['Humidity'].min():.1f}% - {self.data['Humidity'].max():.1f}%
- 高濕度時段: {(self.data['Humidity'] > 90).sum()} 次測量 ({(self.data['Humidity'] > 90).sum()/len(self.data)*100:.1f}%)

### 溫濕度關係
- 相關係數: {correlation.get('temp_humidity_corr', 0):.3f}
- 關係性質: {correlation.get('correlation_strength', '未知')}

### 舒適度評估
- 舒適時段比例: {(self.data['comfort'] == '舒適').sum()/len(self.data)*100:.1f}%
- 平均體感溫度: {comfort.get('avg_heat_index', 0):.1f}°C

## 建議
1. 該地區監測期間氣候特點為高溫高濕，需注意防暑降溫
2. 濕度變化劇烈，需注意通風除濕
3. 溫濕度呈負相關，可用於天氣預測參考

報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        markdown_filename = f'{self.output_prefix}_report.md'
        with open(markdown_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Markdown報告已保存為 '{markdown_filename}'")
        return markdown_filename
    
    def generate_pdf_report(self, chart_filename):
        """生成PDF報告"""
        if not PDF_AVAILABLE:
            print("PDF generation skipped - ReportLab not available")
            return None
            
        print("\n=== Generating PDF Report ===")
        
        pdf_filename = f'{self.output_prefix}_Report.pdf'
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # 自定義樣式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkgreen
        )
        
        # 計算統計數據
        temp_stats = {
            'mean': self.data['Temperature'].mean(),
            'max': self.data['Temperature'].max(),
            'min': self.data['Temperature'].min(),
            'std': self.data['Temperature'].std()
        }
        
        humidity_stats = {
            'mean': self.data['Humidity'].mean(),
            'max': self.data['Humidity'].max(),
            'min': self.data['Humidity'].min(),
            'std': self.data['Humidity'].std()
        }
        
        correlation = self.data['Temperature'].corr(self.data['Humidity'])
        
        # 標題
        story.append(Paragraph("Weather Data Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # 執行摘要
        story.append(Paragraph("Executive Summary", heading_style))
        summary_text = f"""
        This report presents a comprehensive analysis of weather data collected from {self.data['DateTime'].min().strftime('%Y-%m-%d')} to {self.data['DateTime'].max().strftime('%Y-%m-%d')}, using a GRAPHTEC GL860 data logger. 
        The dataset contains {len(self.data):,} measurements taken at 10-minute intervals, providing detailed insights into temperature and humidity patterns.
        
        Key findings include a strong negative correlation ({correlation:.3f}) between temperature and humidity, with temperatures ranging from 
        {temp_stats['min']:.1f}°C to {temp_stats['max']:.1f}°C and humidity levels from {humidity_stats['min']:.1f}% to {humidity_stats['max']:.1f}%. 
        The analysis reveals distinct daily patterns and weather characteristics typical of the monitoring period.
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 數據概覽
        story.append(Paragraph("Data Overview", heading_style))
        
        data_overview = [
            ['Parameter', 'Value'],
            ['Monitoring Period', f"{self.data['DateTime'].min().strftime('%Y-%m-%d')} to {self.data['DateTime'].max().strftime('%Y-%m-%d')}"],
            ['Total Data Points', f"{len(self.data):,}"],
            ['Sampling Interval', '10 minutes'],
            ['Data Logger Model', 'GRAPHTEC GL860'],
            ['Temperature Range', f"{temp_stats['min']:.1f}°C - {temp_stats['max']:.1f}°C"],
            ['Humidity Range', f"{humidity_stats['min']:.1f}% - {humidity_stats['max']:.1f}%"]
        ]
        
        table = Table(data_overview, colWidths=[2.5*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        
        # 添加圖表
        story.append(Paragraph("Weather Analysis Charts", heading_style))
        story.append(Paragraph("The following comprehensive visualization shows all key weather patterns and relationships identified in the data:", styles['Normal']))
        story.append(Spacer(1, 10))
        
        try:
            if os.path.exists(chart_filename):
                img = Image(chart_filename, width=7*inch, height=4.2*inch)
                story.append(img)
            else:
                story.append(Paragraph("Chart image not available", styles['Normal']))
        except:
            story.append(Paragraph("Chart image could not be loaded", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # 詳細分析
        story.append(Paragraph("Detailed Analysis", heading_style))
        
        # 溫度分析
        story.append(Paragraph("Temperature Characteristics", subheading_style))
        temp_analysis = f"""
        The temperature data reveals weather patterns with significant daily variations. The average temperature was {temp_stats['mean']:.1f}°C, 
        with a standard deviation of {temp_stats['std']:.1f}°C indicating moderate variability. The temperature range of {temp_stats['max']-temp_stats['min']:.1f}°C 
        demonstrates the substantial thermal differences experienced during the monitoring period.
        
        Daily temperature patterns show clear diurnal cycles, with peak temperatures typically occurring in the afternoon hours and minimum temperatures 
        during early morning. The average daily temperature range was {self.daily_stats['temp_range'].mean():.1f}°C, with the maximum daily range 
        reaching {self.daily_stats['temp_range'].max():.1f}°C, indicating significant thermal variation within individual days.
        """
        story.append(Paragraph(temp_analysis, styles['Normal']))
        story.append(Spacer(1, 15))
        
        # 濕度分析
        story.append(Paragraph("Humidity Characteristics", subheading_style))
        humidity_analysis = f"""
        Humidity levels showed considerable variation throughout the monitoring period, with an average of {humidity_stats['mean']:.1f}% and a 
        standard deviation of {humidity_stats['std']:.1f}%. The humidity range extended from {humidity_stats['min']:.1f}% to {humidity_stats['max']:.1f}%, 
        covering nearly the full spectrum of possible humidity conditions.
        
        High humidity events (>90%) occurred {(self.data['Humidity'] > 90).sum()} times ({(self.data['Humidity'] > 90).sum()/len(self.data)*100:.1f}% of measurements), 
        indicating frequent periods of very moist conditions. These high humidity periods typically coincided with lower temperatures, 
        particularly during nighttime and early morning hours.
        """
        story.append(Paragraph(humidity_analysis, styles['Normal']))
        story.append(Spacer(1, 15))
        
        # 相關性分析
        story.append(Paragraph("Temperature-Humidity Relationship", subheading_style))
        correlation_analysis = f"""
        A strong negative correlation ({correlation:.3f}) exists between temperature and humidity, indicating that as temperatures rise, 
        humidity levels tend to decrease, and vice versa. This relationship is typical of natural weather patterns where warm air can hold more 
        moisture, leading to lower relative humidity readings at higher temperatures.
        
        The scatter plot visualization uses color coding to show temporal patterns:
        • Purple points represent nighttime measurements (0-6 hours) - typically showing lower temperatures and higher humidity
        • Blue points represent morning measurements (6-12 hours) - showing transitional conditions
        • Green points represent afternoon measurements (12-18 hours) - typically showing higher temperatures and lower humidity  
        • Yellow points represent evening measurements (18-24 hours) - showing cooling temperatures and rising humidity
        
        This temporal color coding reveals the daily cycle of temperature-humidity relationships and helps identify patterns 
        that might not be apparent from the correlation coefficient alone.
        """
        story.append(Paragraph(correlation_analysis, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 結論
        story.append(Paragraph("Conclusions and Recommendations", heading_style))
        conclusions = f"""
        Based on the comprehensive analysis of the weather data, the following conclusions and recommendations are made:
        
        1. Climate Characteristics: The monitoring period exhibited weather patterns with high temperatures and variable humidity. 
           The strong negative correlation between temperature and humidity is consistent with expected meteorological relationships.
        
        2. Daily Patterns: Clear diurnal cycles were observed in both temperature and humidity, with predictable patterns that can be used 
           for weather forecasting and planning purposes.
        
        3. Data Quality: The high-resolution 10-minute sampling interval provided excellent temporal resolution for identifying short-term 
           weather variations and patterns that might be missed with lower frequency sampling.
        
        This analysis provides a solid foundation for understanding local weather patterns and can inform decision-making for activities 
        sensitive to temperature and humidity conditions.
        """
        story.append(Paragraph(conclusions, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 頁腳
        story.append(Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        
        # 建立PDF
        try:
            doc.build(story)
            print(f"PDF report successfully generated: '{pdf_filename}'")
            return pdf_filename
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
    
    def generate_all_reports(self):
        """生成所有報告和圖表"""
        print(f"\n=== 生成報告 (前綴: {self.output_prefix}) ===")
        
        # 生成圖表
        chart_filename = self.create_visualizations()
        
        # 生成Markdown報告
        markdown_filename = self.generate_markdown_report()
        
        # 生成PDF報告
        pdf_filename = self.generate_pdf_report(chart_filename)
        
        return {
            'chart': chart_filename,
            'markdown': markdown_filename,
            'pdf': pdf_filename
        }
