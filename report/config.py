"""
Configuration File
配置文件 - 包含系統的各種設置參數
"""

# 數據載入配置
DATA_CONFIG = {
    # Excel文件配置
    'main_sheet_name': '2507_Modify',  # 主要數據表名稱
    'skip_rows': 14,                   # 跳過的行數
    'precipitation_sheet': 'Precp(mm)', # 降水數據表名稱
    
    # 列名映射
    'column_mapping': {
        'NO.': 'Number',
        'Time': 'DateTime',
        'degC': 'Temperature',
        '%': 'Humidity',
        'degC.1': 'Temperature_CH3'
    },
    
    # 數據清理參數
    'required_columns': ['DateTime', 'Temperature', 'Humidity'],
    'sampling_interval': '10分鐘'
}

# 分析配置
ANALYSIS_CONFIG = {
    # 極端事件閾值
    'extreme_events': {
        'temp_high_percentile': 0.95,    # 極端高溫百分位
        'temp_low_percentile': 0.05,     # 極端低溫百分位
        'humidity_high_threshold': 90,    # 高濕度閾值 (%)
        'heavy_rain_threshold': 10        # 大雨閾值 (mm)
    },
    
    # 舒適度指數參數
    'comfort_zones': {
        'comfortable': {'temp_range': (20, 26), 'humidity_range': (40, 60)},
        'fairly_comfortable': {'temp_range': (18, 28), 'humidity_range': (30, 70)},
        'uncomfortable_conditions': {'temp_threshold': 30, 'humidity_threshold': 80},
        'less_comfortable_conditions': {'temp_threshold': 18, 'humidity_threshold': 30}
    },
    
    # 體感溫度計算參數
    'heat_index': {
        'base_temp_threshold': 27  # 低於此溫度時體感溫度約等於實際溫度
    }
}

# 可視化配置
VISUALIZATION_CONFIG = {
    # 圖表尺寸和佈局
    'figure_size': (20, 12),
    'subplot_layout': (2, 4),
    'dpi': 300,
    
    # 字體設置
    'fonts': ['Arial', 'DejaVu Sans'],
    'chinese_fonts': ['Microsoft YaHei', 'SimHei'],
    
    # 顏色配置
    'colors': {
        'temperature': 'red',
        'humidity': 'blue',
        'scatter_colormap': 'plasma'
    },
    
    # 圖例設置
    'legend': {
        'location': 'upper right',
        'fontsize': 8,
        'framealpha': 0.9
    },
    
    # 時間顏色編碼說明
    'time_color_meanings': {
        'night': {'hours': '0-6h', 'description': 'Cool, High Humidity', 'emoji': '🟣'},
        'morning': {'hours': '6-12h', 'description': 'Warming, Moderate RH', 'emoji': '🔵'},
        'afternoon': {'hours': '12-18h', 'description': 'Hot, Low Humidity', 'emoji': '🟢'},
        'evening': {'hours': '18-24h', 'description': 'Cooling, Rising RH', 'emoji': '🟡'}
    }
}

# 報告生成配置
REPORT_CONFIG = {
    # PDF設置
    'pdf': {
        'page_size': 'A4',
        'title_font_size': 24,
        'heading_font_size': 16,
        'subheading_font_size': 14,
        'image_width': 7,  # inches
        'image_height': 4.2  # inches
    },
    
    # 輸出文件設置
    'output': {
        'chart_suffix': '_comprehensive.png',
        'markdown_suffix': '_report.md',
        'pdf_suffix': '_Report.pdf',
        'timestamp_format': '%Y%m%d_%H%M%S'
    },
    
    # 報告語言設置
    'languages': {
        'markdown': 'zh-TW',  # 中文繁體
        'pdf': 'en-US'        # 英文
    }
}

# 系統配置
SYSTEM_CONFIG = {
    # 默認文件
    'default_file': 'GL860+RAWDATA_2507.xlsx',
    
    # 批量處理設置
    'batch_processing': {
        'max_concurrent_files': 5,
        'continue_on_error': True
    },
    
    # 日誌設置
    'logging': {
        'level': 'INFO',
        'format': '%(asctime)s - %(levelname)s - %(message)s'
    }
}

# 驗證配置
def validate_config():
    """驗證配置文件的有效性"""
    errors = []
    
    # 檢查必要的配置項
    required_configs = ['DATA_CONFIG', 'ANALYSIS_CONFIG', 'VISUALIZATION_CONFIG', 'REPORT_CONFIG']
    for config_name in required_configs:
        if config_name not in globals():
            errors.append(f"Missing required configuration: {config_name}")
    
    # 檢查數據配置
    if 'required_columns' not in DATA_CONFIG:
        errors.append("Missing required_columns in DATA_CONFIG")
    
    # 檢查分析配置
    if 'extreme_events' not in ANALYSIS_CONFIG:
        errors.append("Missing extreme_events in ANALYSIS_CONFIG")
    
    return errors

# 獲取配置值的便捷函數
def get_config(section, key, default=None):
    """
    獲取配置值
    
    Args:
        section (str): 配置段名稱
        key (str): 配置鍵名
        default: 默認值
    
    Returns:
        配置值或默認值
    """
    config_sections = {
        'data': DATA_CONFIG,
        'analysis': ANALYSIS_CONFIG,
        'visualization': VISUALIZATION_CONFIG,
        'report': REPORT_CONFIG,
        'system': SYSTEM_CONFIG
    }
    
    section_config = config_sections.get(section, {})
    return section_config.get(key, default)

if __name__ == "__main__":
    # 驗證配置
    errors = validate_config()
    if errors:
        print("配置驗證失敗:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("配置驗證通過 ✅")
        
        # 顯示配置摘要
        print("\n配置摘要:")
        print(f"  數據採樣間隔: {DATA_CONFIG['sampling_interval']}")
        print(f"  圖表尺寸: {VISUALIZATION_CONFIG['figure_size']}")
        print(f"  默認文件: {SYSTEM_CONFIG['default_file']}")
        print(f"  PDF頁面大小: {REPORT_CONFIG['pdf']['page_size']}")
