"""
Weather Analyzer Module
負責進行天氣數據的統計分析和計算
"""

import pandas as pd
import numpy as np
from datetime import datetime

class WeatherAnalyzer:
    def __init__(self, data, precip_data):
        """初始化分析器"""
        self.data = data
        self.precip_data = precip_data
        self.daily_stats = None
        self.analysis_results = {}
        
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
        
        # 打印統計結果
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
        
        # 保存結果
        self.analysis_results['basic_stats'] = {
            'temperature': temp_stats,
            'humidity': humidity_stats,
            'precipitation': precip_stats
        }
        
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
        
        # 保存結果
        self.analysis_results['daily_stats'] = {
            'temp_range_min': daily_stats['Temperature_mean'].min(),
            'temp_range_max': daily_stats['Temperature_mean'].max(),
            'humidity_range_min': daily_stats['Humidity_mean'].min(),
            'humidity_range_max': daily_stats['Humidity_mean'].max(),
            'max_temp_range': daily_stats['temp_range'].max(),
            'max_humidity_range': daily_stats['humidity_range'].max()
        }
        
        return daily_stats
    
    def correlation_analysis(self):
        """相關性分析"""
        print("\n=== 相關性分析 ===")
        
        # 計算相關係數
        temp_humidity_corr = self.data['Temperature'].corr(self.data['Humidity'])
        print(f"溫度與濕度相關係數: {temp_humidity_corr:.3f}")
        
        if abs(temp_humidity_corr) > 0.7:
            correlation_strength = "強相關關係"
        elif abs(temp_humidity_corr) > 0.3:
            correlation_strength = "中等相關關係"
        else:
            correlation_strength = "弱相關關係"
        
        print(f"  -> {correlation_strength}")
        
        # 降水日與溫濕度的關係
        rainy_temp_mean = np.nan
        dry_temp_mean = np.nan
        rainy_humidity_mean = np.nan
        dry_humidity_mean = np.nan
        
        if self.daily_stats is not None:
            rainy_days = self.daily_stats[self.daily_stats['Precipitation'] > 0]
            dry_days = self.daily_stats[self.daily_stats['Precipitation'] == 0]
            
            if len(rainy_days) > 0:
                rainy_temp_mean = rainy_days['Temperature_mean'].mean()
                rainy_humidity_mean = rainy_days['Humidity_mean'].mean()
            
            if len(dry_days) > 0:
                dry_temp_mean = dry_days['Temperature_mean'].mean()
                dry_humidity_mean = dry_days['Humidity_mean'].mean()
            
            print(f"\n降水日平均溫度: {rainy_temp_mean:.1f}°C" if not np.isnan(rainy_temp_mean) else "\n降水日平均溫度: nan°C")
            print(f"無降水日平均溫度: {dry_temp_mean:.1f}°C" if not np.isnan(dry_temp_mean) else "無降水日平均溫度: nan°C")
            print(f"降水日平均濕度: {rainy_humidity_mean:.1f}%" if not np.isnan(rainy_humidity_mean) else "降水日平均濕度: nan%")
            print(f"無降水日平均濕度: {dry_humidity_mean:.1f}%" if not np.isnan(dry_humidity_mean) else "無降水日平均濕度: nan%")
        
        # 保存結果
        self.analysis_results['correlation'] = {
            'temp_humidity_corr': temp_humidity_corr,
            'correlation_strength': correlation_strength,
            'rainy_temp_mean': rainy_temp_mean,
            'dry_temp_mean': dry_temp_mean,
            'rainy_humidity_mean': rainy_humidity_mean,
            'dry_humidity_mean': dry_humidity_mean
        }
        
        return temp_humidity_corr
    
    def extreme_events(self):
        """極端事件分析"""
        print("\n=== 極端事件分析 ===")
        
        # 定義極端事件閾值
        temp_high_threshold = self.data['Temperature'].quantile(0.95)
        temp_low_threshold = self.data['Temperature'].quantile(0.05)
        humidity_high_threshold = 90
        heavy_rain_threshold = 10
        
        # 極端事件統計
        high_temp_events = self.data[self.data['Temperature'] > temp_high_threshold]
        low_temp_events = self.data[self.data['Temperature'] < temp_low_threshold]
        high_humidity_events = self.data[self.data['Humidity'] > humidity_high_threshold]
        heavy_rain_days = self.precip_data[self.precip_data['Precipitation'] > heavy_rain_threshold]
        
        print(f"極端高溫事件 (>{temp_high_threshold:.1f}°C): {len(high_temp_events)}次")
        print(f"極端低溫事件 (<{temp_low_threshold:.1f}°C): {len(low_temp_events)}次")
        print(f"高濕度事件 (>{humidity_high_threshold}%): {len(high_humidity_events)}次")
        print(f"大雨日數 (>{heavy_rain_threshold}mm): {len(heavy_rain_days)}天")
        
        max_rain_amount = 0
        max_rain_date = None
        if len(heavy_rain_days) > 0:
            max_rain_amount = heavy_rain_days['Precipitation'].max()
            max_rain_date = heavy_rain_days.loc[heavy_rain_days['Precipitation'].idxmax(), 'Date']
            print(f"最大日降水量: {max_rain_amount:.1f}mm")
            print(f"最大降水日期: {max_rain_date}")
        
        # 保存結果
        self.analysis_results['extreme_events'] = {
            'temp_high_threshold': temp_high_threshold,
            'temp_low_threshold': temp_low_threshold,
            'high_temp_events_count': len(high_temp_events),
            'low_temp_events_count': len(low_temp_events),
            'high_humidity_events_count': len(high_humidity_events),
            'heavy_rain_days_count': len(heavy_rain_days),
            'max_rain_amount': max_rain_amount,
            'max_rain_date': max_rain_date
        }
        
        return {
            'high_temp_events': len(high_temp_events),
            'low_temp_events': len(low_temp_events),
            'high_humidity_events': len(high_humidity_events),
            'heavy_rain_days': len(heavy_rain_days)
        }
    
    def comfort_index(self):
        """舒適度指數計算"""
        print("\n=== 舒適度指數分析 ===")
        
        # 計算體感溫度 (Heat Index)
        def heat_index(temp, humidity):
            if temp < 27:
                return temp
            
            T = temp * 9/5 + 32  # 轉華氏
            R = humidity
            
            HI = -42.379 + 2.04901523*T + 10.14333127*R - 0.22475541*T*R - \
                 6.83783e-3*T*T - 5.481717e-2*R*R + 1.22874e-3*T*T*R + \
                 8.5282e-4*T*R*R - 1.99e-6*T*T*R*R
            
            return (HI - 32) * 5/9  # 轉回攝氏
        
        # 計算舒適度等級
        def comfort_level(temp, humidity):
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
        
        # 計算體感溫度和舒適度
        self.data['heat_index'] = self.data.apply(
            lambda row: heat_index(row['Temperature'], row['Humidity']), axis=1
        )
        
        self.data['comfort'] = self.data.apply(
            lambda row: comfort_level(row['Temperature'], row['Humidity']), axis=1
        )
        
        # 統計舒適度分布
        comfort_dist = self.data['comfort'].value_counts()
        print("舒適度分布:")
        for level, count in comfort_dist.items():
            percentage = count / len(self.data) * 100
            print(f"  {level}: {count}次 ({percentage:.1f}%)")
        
        avg_heat_index = self.data['heat_index'].mean()
        max_heat_index = self.data['heat_index'].max()
        
        print(f"\n平均體感溫度: {avg_heat_index:.1f}°C")
        print(f"最高體感溫度: {max_heat_index:.1f}°C")
        
        # 保存結果
        self.analysis_results['comfort'] = {
            'comfort_distribution': comfort_dist.to_dict(),
            'avg_heat_index': avg_heat_index,
            'max_heat_index': max_heat_index
        }
        
        return comfort_dist, avg_heat_index, max_heat_index
    
    def get_analysis_results(self):
        """獲取所有分析結果"""
        return self.analysis_results
    
    def get_daily_stats(self):
        """獲取日統計數據"""
        return self.daily_stats
