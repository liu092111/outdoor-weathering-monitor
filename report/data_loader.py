"""
Data Loader Module
負責從Excel文件中載入和預處理天氣數據
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class WeatherDataLoader:
    def __init__(self, excel_file):
        """初始化數據載入器"""
        self.excel_file = excel_file
        self.data = None
        self.precip_data = None
        
    def load_weather_data(self):
        """載入主要天氣數據"""
        try:
            # 讀取主要數據表
            self.data = pd.read_excel(self.excel_file, sheet_name='2507_Modify', skiprows=14)
            
            print(f"原始列名: {list(self.data.columns)}")
            print(f"數據形狀: {self.data.shape}")
            
            # 根據實際列名進行映射
            if len(self.data.columns) >= 4:
                column_mapping = {
                    'NO.': 'Number',
                    'Time': 'DateTime',
                    'degC': 'Temperature',
                    '%': 'Humidity'
                }
                
                if 'degC.1' in self.data.columns:
                    column_mapping['degC.1'] = 'Temperature_CH3'
                
                self.data = self.data.rename(columns=column_mapping)
                
                # 數據清理
                self.data = self.data.dropna(subset=['DateTime', 'Temperature', 'Humidity'])
                
                # 轉換數據類型
                self.data['DateTime'] = pd.to_datetime(self.data['DateTime'])
                self.data['Date'] = self.data['DateTime'].dt.date
                self.data['Hour'] = self.data['DateTime'].dt.hour
                self.data['Minute'] = self.data['DateTime'].dt.minute
                
                self.data['Temperature'] = pd.to_numeric(self.data['Temperature'], errors='coerce')
                self.data['Humidity'] = pd.to_numeric(self.data['Humidity'], errors='coerce')
                
                if 'Temperature_CH3' in self.data.columns:
                    self.data['Temperature_CH3'] = pd.to_numeric(self.data['Temperature_CH3'], errors='coerce')
                
                # 移除包含NaN的行
                self.data = self.data.dropna(subset=['Temperature', 'Humidity'])
                
            else:
                raise ValueError(f"Excel文件列數不足，期望至少4列，實際{len(self.data.columns)}列")
            
            print(f"數據載入成功！")
            print(f"數據範圍: {self.data['DateTime'].min()} 到 {self.data['DateTime'].max()}")
            print(f"總數據點: {len(self.data)}")
            print(f"溫度範圍: {self.data['Temperature'].min():.1f}°C - {self.data['Temperature'].max():.1f}°C")
            print(f"濕度範圍: {self.data['Humidity'].min():.1f}% - {self.data['Humidity'].max():.1f}%")
            
            return True
            
        except Exception as e:
            print(f"數據載入失敗: {e}")
            return False
    
    def load_precipitation_data(self):
        """載入降水數據"""
        try:
            precip_data = pd.read_excel(self.excel_file, sheet_name='Precp(mm)')
            print(f"降水數據列名: {list(precip_data.columns)}")
            
            precip_cols = list(precip_data.columns)
            if len(precip_cols) >= 2:
                precip_mapping = {
                    precip_cols[1]: 'Date',
                    precip_cols[2]: 'Precipitation'
                }
                self.precip_data = precip_data.rename(columns=precip_mapping)
                
                self.precip_data['Date'] = pd.to_datetime(self.precip_data['Date']).dt.date
                self.precip_data['Precipitation'] = pd.to_numeric(self.precip_data['Precipitation'], errors='coerce')
                self.precip_data = self.precip_data.dropna(subset=['Precipitation'])
            else:
                self._create_default_precipitation_data()
                
        except Exception as precip_error:
            print(f"降水數據載入失敗: {precip_error}")
            self._create_default_precipitation_data()
    
    def _create_default_precipitation_data(self):
        """創建默認降水數據"""
        print("使用默認降水數據")
        dates = pd.date_range(start=self.data['DateTime'].min().date(), 
                            end=self.data['DateTime'].max().date(), freq='D')
        self.precip_data = pd.DataFrame({
            'Date': dates.date,
            'Precipitation': [0] * len(dates)
        })
    
    def get_data(self):
        """獲取載入的數據"""
        return self.data, self.precip_data
    
    def get_data_summary(self):
        """獲取數據摘要信息"""
        if self.data is None:
            return None
            
        summary = {
            'file_name': self.excel_file,
            'date_range': {
                'start': self.data['DateTime'].min(),
                'end': self.data['DateTime'].max()
            },
            'total_points': len(self.data),
            'temperature_range': {
                'min': self.data['Temperature'].min(),
                'max': self.data['Temperature'].max(),
                'mean': self.data['Temperature'].mean()
            },
            'humidity_range': {
                'min': self.data['Humidity'].min(),
                'max': self.data['Humidity'].max(),
                'mean': self.data['Humidity'].mean()
            }
        }
        return summary
