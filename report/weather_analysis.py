import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

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
    print("Install with: pip install reportlab")
    PDF_AVAILABLE = False

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

class WeatherDataAnalyzer:
    def __init__(self, excel_file):
        """初始化天氣數據分析器"""
        self.excel_file = excel_file
        self.data = None
        self.daily_stats = None
        
    def load_data(self):
        """載入Excel數據"""
        try:
            # 讀取主要數據表 - 使用正確的skiprows=14參數
            self.data = pd.read_excel(self.excel_file, sheet_name='2507_Modify', skiprows=14)
            
            # 檢查實際列名並進行映射
            print(f"原始列名: {list(self.data.columns)}")
            print(f"數據形狀: {self.data.shape}")
            
            # 根據調試結果，實際列名是: ['NO.', 'Time', 'degC', '%', 'degC.1']
            if len(self.data.columns) >= 4:
                # 重新命名列 - 使用實際的列名
                column_mapping = {
                    'NO.': 'Number',           # 序號
                    'Time': 'DateTime',        # 時間
                    'degC': 'Temperature',     # 溫度 (CH1)
                    '%': 'Humidity'            # 濕度 (CH2)
                }
                
                # 如果有第三個溫度通道
                if 'degC.1' in self.data.columns:
                    column_mapping['degC.1'] = 'Temperature_CH3'
                
                self.data = self.data.rename(columns=column_mapping)
                
                # 只保留有數據的行
                self.data = self.data.dropna(subset=['DateTime', 'Temperature', 'Humidity'])
                
                # 轉換日期時間格式
                self.data['DateTime'] = pd.to_datetime(self.data['DateTime'])
                self.data['Date'] = self.data['DateTime'].dt.date
                self.data['Hour'] = self.data['DateTime'].dt.hour
                self.data['Minute'] = self.data['DateTime'].dt.minute
                
                # 確保數值列為數值類型
                self.data['Temperature'] = pd.to_numeric(self.data['Temperature'], errors='coerce')
                self.data['Humidity'] = pd.to_numeric(self.data['Humidity'], errors='coerce')
                if 'Temperature_CH3' in self.data.columns:
                    self.data['Temperature_CH3'] = pd.to_numeric(self.data['Temperature_CH3'], errors='coerce')
                
                # 移除包含NaN的行
                self.data = self.data.dropna(subset=['Temperature', 'Humidity'])
                
            else:
                raise ValueError(f"Excel文件列數不足，期望至少4列，實際{len(self.data.columns)}列")
            
            # 讀取降水數據
            try:
                precip_data = pd.read_excel(self.excel_file, sheet_name='Precp(mm)')
                print(f"降水數據列名: {list(precip_data.columns)}")
                
                # 重新映射降水數據列名
                precip_cols = list(precip_data.columns)
                if len(precip_cols) >= 2:
                    precip_mapping = {
                        precip_cols[1]: 'Date',           # Time列
                        precip_cols[2]: 'Precipitation'   # Precp(mm)列
                    }
                    self.precip_data = precip_data.rename(columns=precip_mapping)
                    
                    # 轉換日期格式
                    self.precip_data['Date'] = pd.to_datetime(self.precip_data['Date']).dt.date
                    self.precip_data['Precipitation'] = pd.to_numeric(self.precip_data['Precipitation'], errors='coerce')
                    self.precip_data = self.precip_data.dropna(subset=['Precipitation'])
                else:
                    print("降水數據格式不正確，使用默認值")
                    # 創建默認降水數據
                    dates = pd.date_range(start=self.data['DateTime'].min().date(), 
                                        end=self.data['DateTime'].max().date(), freq='D')
                    self.precip_data = pd.DataFrame({
                        'Date': dates.date,
                        'Precipitation': [0] * len(dates)
                    })
                    
            except Exception as precip_error:
                print(f"降水數據載入失敗: {precip_error}")
                # 創建默認降水數據
                dates = pd.date_range(start=self.data['DateTime'].min().date(), 
                                    end=self.data['DateTime'].max().date(), freq='D')
                self.precip_data = pd.DataFrame({
                    'Date': dates.date,
                    'Precipitation': [0] * len(dates)
                })
            
            print(f"數據載入成功！")
            print(f"數據範圍: {self.data['DateTime'].min()} 到 {self.data['DateTime'].max()}")
            print(f"總數據點: {len(self.data)}")
            print(f"溫度範圍: {self.data['Temperature'].min():.1f}°C - {self.data['Temperature'].max():.1f}°C")
            print(f"濕度範圍: {self.data['Humidity'].min():.1f}% - {self.data['Humidity'].max():.1f}%")
            
        except Exception as e:
            print(f"數據載入失敗: {e}")
            import traceback
            traceback.print_exc()
    
    def basic_statistics(self):
        """基礎統計分析"""
        print("\n=== 基礎統計分析 ===")
        
        # 溫度統計
        temp_stats = {
            '平均溫度': self.data['Temperature'].mean(),
            '最高溫度': self.data['Temperature'].max(),
            '最低溫度': self.data['Temperature'].min(),
            '溫度標準差': self.data['Temperature'].std(),
            '溫度範圍': self.data['Temperature'].max() - self.data['Temperature'].min()
        }
        
        # 濕度統計
        humidity_stats = {
            '平均濕度': self.data['Humidity'].mean(),
            '最高濕度': self.data['Humidity'].max(),
            '最低濕度': self.data['Humidity'].min(),
            '濕度標準差': self.data['Humidity'].std(),
            '濕度範圍': self.data['Humidity'].max() - self.data['Humidity'].min()
        }
        
        # 降水統計
        precip_stats = {
            '總降水量': self.precip_data['Precipitation'].sum(),
            '平均日降水量': self.precip_data['Precipitation'].mean(),
            '最大日降水量': self.precip_data['Precipitation'].max(),
            '降水日數': (self.precip_data['Precipitation'] > 0).sum(),
            '無降水日數': (self.precip_data['Precipitation'] == 0).sum()
        }
        
        print("\n溫度統計:")
        for key, value in temp_stats.items():
            print(f"  {key}: {value:.2f}°C")
            
        print("\n濕度統計:")
        for key, value in humidity_stats.items():
            print(f"  {key}: {value:.2f}%")
            
        print("\n降水統計:")
        for key, value in precip_stats.items():
            if 'mm' in str(value) or '量' in key:
                print(f"  {key}: {value:.1f}mm")
            else:
                print(f"  {key}: {value}天")
        
        return temp_stats, humidity_stats, precip_stats
    
    def daily_analysis(self):
        """日統計分析"""
        print("\n=== 日統計分析 ===")
        
        # 計算每日統計
        daily_stats = self.data.groupby('Date').agg({
            'Temperature': ['mean', 'max', 'min', 'std'],
            'Humidity': ['mean', 'max', 'min', 'std']
        }).round(2)
        
        # 扁平化列名
        daily_stats.columns = ['_'.join(col).strip() for col in daily_stats.columns]
        
        # 計算日溫差
        daily_stats['temp_range'] = daily_stats['Temperature_max'] - daily_stats['Temperature_min']
        daily_stats['humidity_range'] = daily_stats['Humidity_max'] - daily_stats['Humidity_min']
        
        # 合併降水數據
        daily_stats = daily_stats.reset_index()
        daily_stats = daily_stats.merge(self.precip_data, left_on='Date', right_on='Date', how='left')
        
        self.daily_stats = daily_stats
        
        print(f"日平均溫度範圍: {daily_stats['Temperature_mean'].min():.1f}°C - {daily_stats['Temperature_mean'].max():.1f}°C")
        print(f"日平均濕度範圍: {daily_stats['Humidity_mean'].min():.1f}% - {daily_stats['Humidity_mean'].max():.1f}%")
        print(f"最大日溫差: {daily_stats['temp_range'].max():.1f}°C")
        print(f"最大日濕度差: {daily_stats['humidity_range'].max():.1f}%")
        
        return daily_stats
    
    def correlation_analysis(self):
        """相關性分析"""
        print("\n=== 相關性分析 ===")
        
        # 計算相關係數
        temp_humidity_corr = self.data['Temperature'].corr(self.data['Humidity'])
        print(f"溫度與濕度相關係數: {temp_humidity_corr:.3f}")
        
        if abs(temp_humidity_corr) > 0.7:
            print("  -> 強相關關係")
        elif abs(temp_humidity_corr) > 0.3:
            print("  -> 中等相關關係")
        else:
            print("  -> 弱相關關係")
        
        # 降水日與溫濕度的關係
        if self.daily_stats is not None:
            rainy_days = self.daily_stats[self.daily_stats['Precipitation'] > 0]
            dry_days = self.daily_stats[self.daily_stats['Precipitation'] == 0]
            
            print(f"\n降水日平均溫度: {rainy_days['Temperature_mean'].mean():.1f}°C")
            print(f"無降水日平均溫度: {dry_days['Temperature_mean'].mean():.1f}°C")
            print(f"降水日平均濕度: {rainy_days['Humidity_mean'].mean():.1f}%")
            print(f"無降水日平均濕度: {dry_days['Humidity_mean'].mean():.1f}%")
        
        return temp_humidity_corr
    
    def extreme_events(self):
        """極端事件分析"""
        print("\n=== 極端事件分析 ===")
        
        # 定義極端事件閾值
        temp_high_threshold = self.data['Temperature'].quantile(0.95)  # 95百分位
        temp_low_threshold = self.data['Temperature'].quantile(0.05)   # 5百分位
        humidity_high_threshold = 90  # 高濕度閾值
        heavy_rain_threshold = 10     # 大雨閾值
        
        # 極端高溫事件
        high_temp_events = self.data[self.data['Temperature'] > temp_high_threshold]
        low_temp_events = self.data[self.data['Temperature'] < temp_low_threshold]
        high_humidity_events = self.data[self.data['Humidity'] > humidity_high_threshold]
        heavy_rain_days = self.precip_data[self.precip_data['Precipitation'] > heavy_rain_threshold]
        
        print(f"極端高溫事件 (>{temp_high_threshold:.1f}°C): {len(high_temp_events)}次")
        print(f"極端低溫事件 (<{temp_low_threshold:.1f}°C): {len(low_temp_events)}次")
        print(f"高濕度事件 (>{humidity_high_threshold}%): {len(high_humidity_events)}次")
        print(f"大雨日數 (>{heavy_rain_threshold}mm): {len(heavy_rain_days)}天")
        
        if len(heavy_rain_days) > 0:
            print(f"最大日降水量: {heavy_rain_days['Precipitation'].max():.1f}mm")
            max_rain_date = heavy_rain_days.loc[heavy_rain_days['Precipitation'].idxmax(), 'Date']
            print(f"最大降水日期: {max_rain_date}")
    
    def comfort_index(self):
        """舒適度指數計算"""
        print("\n=== 舒適度指數分析 ===")
        
        # 計算體感溫度 (Heat Index)
        def heat_index(temp, humidity):
            """計算體感溫度"""
            if temp < 27:  # 低於27度時體感溫度約等於實際溫度
                return temp
            
            # Heat Index公式 (華氏轉攝氏)
            T = temp * 9/5 + 32  # 轉華氏
            R = humidity
            
            HI = -42.379 + 2.04901523*T + 10.14333127*R - 0.22475541*T*R - \
                 6.83783e-3*T*T - 5.481717e-2*R*R + 1.22874e-3*T*T*R + \
                 8.5282e-4*T*R*R - 1.99e-6*T*T*R*R
            
            return (HI - 32) * 5/9  # 轉回攝氏
        
        # 計算舒適度等級
        def comfort_level(temp, humidity):
            """根據溫濕度判斷舒適度"""
            if 20 <= temp <= 26 and 40 <= humidity <= 60:
                return "舒適"
            elif 18 <= temp <= 28 and 30 <= humidity <= 70:
                return "較舒適"
            elif temp > 30 or humidity > 80:
                return "不舒適"
            elif temp < 18 or humidity < 30:
                return "較不舒適"
            else:
                return "一般"
        
        # 計算體感溫度
        self.data['heat_index'] = self.data.apply(
            lambda row: heat_index(row['Temperature'], row['Humidity']), axis=1
        )
        
        # 計算舒適度等級
        self.data['comfort'] = self.data.apply(
            lambda row: comfort_level(row['Temperature'], row['Humidity']), axis=1
        )
        
        # 統計舒適度分布
        comfort_dist = self.data['comfort'].value_counts()
        print("舒適度分布:")
        for level, count in comfort_dist.items():
            percentage = count / len(self.data) * 100
            print(f"  {level}: {count}次 ({percentage:.1f}%)")
        
        print(f"\n平均體感溫度: {self.data['heat_index'].mean():.1f}°C")
        print(f"最高體感溫度: {self.data['heat_index'].max():.1f}°C")
    
    def create_visualizations(self):
        """創建可視化圖表"""
        print("\n=== Creating Visualization Charts ===")
        
        # Set chart style and font for English
        plt.style.use('default')
        plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        fig = plt.figure(figsize=(20, 12))  # Adjusted for 2x4 layout (removed precipitation)
        
        # Calculate statistics for legends
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
        
        # 1. Temperature Time Series
        ax1 = plt.subplot(2, 4, 1)
        line1 = ax1.plot(self.data['DateTime'], self.data['Temperature'], 'r-', alpha=0.7, linewidth=0.5, label='Temperature')[0]
        ax1.set_title('Temperature Time Series', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Temperature (°C)')
        ax1.grid(True, alpha=0.3)
        
        # Add comprehensive legend with statistics - FIXED TO UPPER RIGHT
        temp_legend = f'Temperature\nMean: {temp_stats["mean"]:.1f}°C\nMax: {temp_stats["max"]:.1f}°C\nMin: {temp_stats["min"]:.1f}°C\nStd: {temp_stats["std"]:.1f}°C\nRange: {temp_stats["max"]-temp_stats["min"]:.1f}°C'
        ax1.legend([line1], [temp_legend], loc='upper right', fontsize=8, framealpha=0.9)
        
        # 2. Humidity Time Series
        ax2 = plt.subplot(2, 4, 2)
        line2 = ax2.plot(self.data['DateTime'], self.data['Humidity'], 'b-', alpha=0.7, linewidth=0.5, label='Humidity')[0]
        ax2.set_title('Humidity Time Series', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Humidity (%)')
        ax2.grid(True, alpha=0.3)
        
        # Add comprehensive legend with statistics - FIXED TO UPPER RIGHT
        humidity_legend = f'Humidity\nMean: {humidity_stats["mean"]:.1f}%\nMax: {humidity_stats["max"]:.1f}%\nMin: {humidity_stats["min"]:.1f}%\nStd: {humidity_stats["std"]:.1f}%\nRange: {humidity_stats["max"]-humidity_stats["min"]:.1f}%'
        ax2.legend([line2], [humidity_legend], loc='upper right', fontsize=8, framealpha=0.9)
        
        # 3. Temperature-Humidity Scatter Plot with IMPROVED COLOR EXPLANATION
        ax3 = plt.subplot(2, 4, 3)
        # Create time-based colors for better interpretation
        time_hours = self.data['DateTime'].dt.hour + self.data['DateTime'].dt.minute/60
        scatter = ax3.scatter(self.data['Temperature'], self.data['Humidity'], 
                            c=time_hours, cmap='plasma', alpha=0.6, s=3)
        ax3.set_xlabel('Temperature (°C)')
        ax3.set_ylabel('Humidity (%)')
        ax3.set_title('Temperature-Humidity Relationship', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # Add colorbar for time interpretation with better positioning
        cbar = plt.colorbar(scatter, ax=ax3, shrink=0.6, pad=0.02)
        cbar.set_label('Time of Day (Hours)', fontsize=8)
        cbar.ax.tick_params(labelsize=7)
        
        # Add correlation information in legend with DETAILED COLOR EXPLANATION - FIXED TO UPPER RIGHT
        corr_legend = f'Correlation: {correlation:.3f}\n{"Strong Negative" if correlation < -0.7 else "Strong Positive" if correlation > 0.7 else "Moderate" if abs(correlation) > 0.3 else "Weak"} Relationship\n\nColor Meanings:\n🟣 Purple: Night (0-6h)\n   Cool, High Humidity\n🔵 Blue: Morning (6-12h)\n   Warming, Moderate RH\n🟢 Green: Afternoon (12-18h)\n   Hot, Low Humidity\n🟡 Yellow: Evening (18-24h)\n   Cooling, Rising RH\n\nPoints: {len(self.data):,}'
        ax3.text(0.98, 0.98, corr_legend, transform=ax3.transAxes, fontsize=6.5, 
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
        # 4. Daily Temperature Variation
        if self.daily_stats is not None:
            ax4 = plt.subplot(2, 4, 4)
            line4 = ax4.plot(self.daily_stats['Date'], self.daily_stats['Temperature_mean'], 'ro-', markersize=4, label='Daily Mean')[0]
            fill4 = ax4.fill_between(self.daily_stats['Date'], 
                           self.daily_stats['Temperature_min'], 
                           self.daily_stats['Temperature_max'], alpha=0.3, label='Min-Max Range')
            ax4.set_title('Daily Temperature Variation', fontsize=12, fontweight='bold')
            ax4.set_ylabel('Temperature (°C)')
            ax4.grid(True, alpha=0.3)
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
            
            # Add daily statistics in legend - FIXED TO UPPER RIGHT
            daily_temp_legend = f'Daily Temperature\nMean: {self.daily_stats["Temperature_mean"].mean():.1f}°C\nMax Daily: {self.daily_stats["Temperature_max"].max():.1f}°C\nMin Daily: {self.daily_stats["Temperature_min"].min():.1f}°C\nAvg Range: {self.daily_stats["temp_range"].mean():.1f}°C\nMax Range: {self.daily_stats["temp_range"].max():.1f}°C'
            ax4.legend([line4], [daily_temp_legend], loc='upper right', fontsize=8, framealpha=0.9)
            
            # 5. Daily Humidity Variation
            ax5 = plt.subplot(2, 4, 5)
            line5 = ax5.plot(self.daily_stats['Date'], self.daily_stats['Humidity_mean'], 'bo-', markersize=4, label='Daily Mean')[0]
            fill5 = ax5.fill_between(self.daily_stats['Date'], 
                           self.daily_stats['Humidity_min'], 
                           self.daily_stats['Humidity_max'], alpha=0.3, label='Min-Max Range')
            ax5.set_title('Daily Humidity Variation', fontsize=12, fontweight='bold')
            ax5.set_ylabel('Humidity (%)')
            ax5.grid(True, alpha=0.3)
            plt.setp(ax5.xaxis.get_majorticklabels(), rotation=45)
            
            # Add daily humidity statistics in legend - FIXED TO UPPER RIGHT
            daily_humidity_legend = f'Daily Humidity\nMean: {self.daily_stats["Humidity_mean"].mean():.1f}%\nMax Daily: {self.daily_stats["Humidity_max"].max():.1f}%\nMin Daily: {self.daily_stats["Humidity_min"].min():.1f}%\nAvg Range: {self.daily_stats["humidity_range"].mean():.1f}%\nMax Range: {self.daily_stats["humidity_range"].max():.1f}%'
            ax5.legend([line5], [daily_humidity_legend], loc='upper right', fontsize=8, framealpha=0.9)
        
        # 6. Temperature Distribution (moved from position 7)
        ax6 = plt.subplot(2, 4, 6)
        n, bins, patches = ax6.hist(self.data['Temperature'], bins=30, alpha=0.7, color='red', edgecolor='black', label='Temperature Distribution')
        ax6.set_title('Temperature Distribution', fontsize=12, fontweight='bold')
        ax6.set_xlabel('Temperature (°C)')
        ax6.set_ylabel('Frequency')
        ax6.grid(True, alpha=0.3)
        
        # Add distribution statistics in legend - FIXED TO UPPER RIGHT
        temp_dist_legend = f'Temperature Distribution\nMean: {temp_stats["mean"]:.1f}°C\nMedian: {self.data["Temperature"].median():.1f}°C\nStd Dev: {temp_stats["std"]:.1f}°C\nSkewness: {self.data["Temperature"].skew():.2f}\nSamples: {len(self.data):,}'
        ax6.legend([patches[0]], [temp_dist_legend], loc='upper right', fontsize=8, framealpha=0.9)
        
        # 7. Humidity Distribution (moved from position 8)
        ax7 = plt.subplot(2, 4, 7)
        n, bins, patches = ax7.hist(self.data['Humidity'], bins=30, alpha=0.7, color='blue', edgecolor='black', label='Humidity Distribution')
        ax7.set_title('Humidity Distribution', fontsize=12, fontweight='bold')
        ax7.set_xlabel('Humidity (%)')
        ax7.set_ylabel('Frequency')
        ax7.grid(True, alpha=0.3)
        
        # Add humidity distribution statistics in legend - FIXED TO UPPER RIGHT
        humidity_dist_legend = f'Humidity Distribution\nMean: {humidity_stats["mean"]:.1f}%\nMedian: {self.data["Humidity"].median():.1f}%\nStd Dev: {humidity_stats["std"]:.1f}%\nSkewness: {self.data["Humidity"].skew():.2f}\nSamples: {len(self.data):,}'
        ax7.legend([patches[0]], [humidity_dist_legend], loc='upper right', fontsize=8, framealpha=0.9)
        
        # 8. Hourly Temperature Pattern (moved from position 9)
        ax8 = plt.subplot(2, 4, 8)
        hourly_temp = self.data.groupby('Hour')['Temperature'].mean()
        hourly_temp_std = self.data.groupby('Hour')['Temperature'].std()
        line8 = ax8.plot(hourly_temp.index, hourly_temp.values, 'ro-', markersize=6, label='Hourly Average')[0]
        ax8.set_title('Hourly Temperature Pattern', fontsize=12, fontweight='bold')
        ax8.set_xlabel('Hour of Day')
        ax8.set_ylabel('Average Temperature (°C)')
        ax8.set_xticks(range(0, 24, 3))
        ax8.grid(True, alpha=0.3)
        
        # Add hourly pattern statistics in legend - FIXED TO UPPER RIGHT
        hourly_legend = f'Hourly Pattern\nPeak Hour: {hourly_temp.idxmax()}:00\nPeak Temp: {hourly_temp.max():.1f}°C\nLowest Hour: {hourly_temp.idxmin()}:00\nLowest Temp: {hourly_temp.min():.1f}°C\nDaily Range: {hourly_temp.max()-hourly_temp.min():.1f}°C'
        ax8.legend([line8], [hourly_legend], loc='upper right', fontsize=8, framealpha=0.9)
        
        plt.tight_layout()
        plt.savefig('weather_analysis_comprehensive.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Charts saved as 'weather_analysis_comprehensive.png'")
    
    def generate_report(self):
        """生成分析報告"""
        print("\n=== 生成分析報告 ===")
        
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

### 降水特徵
- 總降水量: {self.precip_data['Precipitation'].sum():.1f}mm
- 降水日數: {(self.precip_data['Precipitation'] > 0).sum()} 天
- 最大日降水量: {self.precip_data['Precipitation'].max():.1f}mm

### 溫濕度關係
- 相關係數: {self.data['Temperature'].corr(self.data['Humidity']):.3f}
- 關係性質: {"負相關" if self.data['Temperature'].corr(self.data['Humidity']) < 0 else "正相關"}

### 舒適度評估
- 舒適時段比例: {(self.data['comfort'] == '舒適').sum()/len(self.data)*100:.1f}%
- 平均體感溫度: {self.data['heat_index'].mean():.1f}°C

## 建議
1. 該地區7月份氣候特點為高溫高濕，需注意防暑降溫
2. 降水集中且強度較大，需做好排水防澇準備
3. 濕度變化劇烈，需注意通風除濕
4. 溫濕度呈負相關，可用於天氣預測參考

報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        with open('weather_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("詳細報告已保存為 'weather_analysis_report.md'")
        return report
    
    def generate_pdf_report(self):
        """Generate comprehensive PDF report in English"""
        if not PDF_AVAILABLE:
            print("PDF generation skipped - ReportLab not available")
            return
            
        print("\n=== Generating PDF Report ===")
        
        # Create PDF document
        doc = SimpleDocTemplate("Weather_Analysis_Report.pdf", pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
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
        
        # Calculate statistics for the report
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
        
        # Title
        story.append(Paragraph("Weather Data Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        summary_text = f"""
        This report presents a comprehensive analysis of weather data collected from July 1-31, 2025, using a GRAPHTEC GL860 data logger. 
        The dataset contains {len(self.data):,} measurements taken at 10-minute intervals, providing detailed insights into temperature and humidity patterns.
        
        Key findings include a strong negative correlation ({correlation:.3f}) between temperature and humidity, with temperatures ranging from 
        {temp_stats['min']:.1f}°C to {temp_stats['max']:.1f}°C and humidity levels from {humidity_stats['min']:.1f}% to {humidity_stats['max']:.1f}%. 
        The analysis reveals distinct daily patterns and weather characteristics typical of summer conditions.
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Data Overview
        story.append(Paragraph("Data Overview", heading_style))
        
        # Create data overview table
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
        
        # Add visualization charts
        story.append(Paragraph("Weather Analysis Charts", heading_style))
        story.append(Paragraph("The following comprehensive visualization shows all key weather patterns and relationships identified in the data:", styles['Normal']))
        story.append(Spacer(1, 10))
        
        # Add the main chart image
        try:
            img = Image('weather_analysis_comprehensive.png', width=7*inch, height=4.2*inch)
            story.append(img)
        except:
            story.append(Paragraph("Chart image not available - please ensure visualization has been generated", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Detailed Analysis Sections
        story.append(Paragraph("Detailed Analysis", heading_style))
        
        # Temperature Analysis
        story.append(Paragraph("Temperature Characteristics", subheading_style))
        temp_analysis = f"""
        The temperature data reveals typical summer weather patterns with significant daily variations. The average temperature was {temp_stats['mean']:.1f}°C, 
        with a standard deviation of {temp_stats['std']:.1f}°C indicating moderate variability. The temperature range of {temp_stats['max']-temp_stats['min']:.1f}°C 
        demonstrates the substantial thermal differences experienced during the monitoring period.
        
        Daily temperature patterns show clear diurnal cycles, with peak temperatures typically occurring in the afternoon hours and minimum temperatures 
        during early morning. The average daily temperature range was {self.daily_stats['temp_range'].mean():.1f}°C, with the maximum daily range 
        reaching {self.daily_stats['temp_range'].max():.1f}°C, indicating significant thermal variation within individual days.
        """
        story.append(Paragraph(temp_analysis, styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Humidity Analysis
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
        
        # Correlation Analysis
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
        story.append(Spacer(1, 15))
        
        # Extreme Events
        story.append(Paragraph("Extreme Weather Events", subheading_style))
        temp_high_threshold = self.data['Temperature'].quantile(0.95)
        temp_low_threshold = self.data['Temperature'].quantile(0.05)
        high_temp_events = len(self.data[self.data['Temperature'] > temp_high_threshold])
        low_temp_events = len(self.data[self.data['Temperature'] < temp_low_threshold])
        high_humidity_events = len(self.data[self.data['Humidity'] > 90])
        
        extreme_analysis = f"""
        Extreme weather events were identified using statistical thresholds:
        
        • High temperature events (>{temp_high_threshold:.1f}°C): {high_temp_events} occurrences
        • Low temperature events (<{temp_low_threshold:.1f}°C): {low_temp_events} occurrences  
        • High humidity events (>90%): {high_humidity_events} occurrences
        
        These extreme events represent approximately {(high_temp_events + low_temp_events + high_humidity_events)/len(self.data)*100:.1f}% of all measurements, 
        indicating that while extreme conditions occurred regularly, they were not the dominant weather pattern during the monitoring period.
        """
        story.append(Paragraph(extreme_analysis, styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Comfort Analysis
        story.append(Paragraph("Human Comfort Assessment", subheading_style))
        comfort_dist = self.data['comfort'].value_counts()
        comfort_analysis = f"""
        Human comfort levels were assessed using standard temperature-humidity comfort indices. The analysis shows:
        
        • Comfortable conditions: {comfort_dist.get('舒適', 0)} measurements ({comfort_dist.get('舒適', 0)/len(self.data)*100:.1f}%)
        • Moderately comfortable: {comfort_dist.get('較舒適', 0)} measurements ({comfort_dist.get('較舒適', 0)/len(self.data)*100:.1f}%)
        • Uncomfortable conditions: {comfort_dist.get('不舒適', 0)} measurements ({comfort_dist.get('不舒適', 0)/len(self.data)*100:.1f}%)
        
        The average heat index (apparent temperature) was {self.data['heat_index'].mean():.1f}°C, with a maximum of {self.data['heat_index'].max():.1f}°C. 
        These values indicate that the monitoring period experienced predominantly warm to hot conditions that would require cooling measures 
        for optimal human comfort.
        """
        story.append(Paragraph(comfort_analysis, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Conclusions and Recommendations
        story.append(Paragraph("Conclusions and Recommendations", heading_style))
        conclusions = f"""
        Based on the comprehensive analysis of the weather data, the following conclusions and recommendations are made:
        
        1. Climate Characteristics: The monitoring period exhibited typical summer weather patterns with high temperatures and variable humidity. 
           The strong negative correlation between temperature and humidity is consistent with expected meteorological relationships.
        
        2. Daily Patterns: Clear diurnal cycles were observed in both temperature and humidity, with predictable patterns that can be used 
           for weather forecasting and planning purposes.
        
        3. Extreme Events: While extreme temperature and humidity events occurred regularly, they followed expected patterns and frequencies 
           for the season and location.
        
        4. Comfort Considerations: The predominance of uncomfortable conditions suggests that cooling and dehumidification measures would be 
           beneficial during similar weather periods.
        
        5. Data Quality: The high-resolution 10-minute sampling interval provided excellent temporal resolution for identifying short-term 
           weather variations and patterns that might be missed with lower frequency sampling.
        
        This analysis provides a solid foundation for understanding local weather patterns and can inform decision-making for activities 
        sensitive to temperature and humidity conditions.
        """
        story.append(Paragraph(conclusions, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        
        # Build PDF
        try:
            doc.build(story)
            print("PDF report successfully generated: 'Weather_Analysis_Report.pdf'")
        except Exception as e:
            print(f"Error generating PDF: {e}")

def main():
    """主函數"""
    print("=== 天氣數據分析系統 ===")
    
    # 初始化分析器
    analyzer = WeatherDataAnalyzer('GL860+RAWDATA_2507.xlsx')
    
    # 執行分析流程
    try:
        # 1. 載入數據
        analyzer.load_data()
        
        # 2. 基礎統計
        analyzer.basic_statistics()
        
        # 3. 日統計分析
        analyzer.daily_analysis()
        
        # 4. 相關性分析
        analyzer.correlation_analysis()
        
        # 5. 極端事件分析
        analyzer.extreme_events()
        
        # 6. 舒適度分析
        analyzer.comfort_index()
        
        # 7. 創建可視化
        analyzer.create_visualizations()
        
        # 8. 生成報告
        analyzer.generate_report()
        
        # 9. 生成PDF報告
        analyzer.generate_pdf_report()
        
        print("\n=== 分析完成 ===")
        print("所有結果已保存到文件中")
        print("- Markdown報告: weather_analysis_report.md")
        print("- PDF報告: Weather_Analysis_Report.pdf")
        print("- 圖表: weather_analysis_comprehensive.png")
        
    except Exception as e:
        print(f"分析過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
