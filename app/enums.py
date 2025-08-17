from enum import Enum


class OrderProbability(Enum):
    """受注角度の列挙型"""
    HIGH = (100, "〇", "高")      # 受注確実
    MEDIUM = (50, "△", "中")     # 受注可能性あり
    LOW = (0, "×", "低")         # 受注困難
    
    def __init__(self, numeric_value, symbol, description):
        self.numeric_value = numeric_value
        self.symbol = symbol
        self.description = description
    
    @classmethod
    def from_value(cls, value):
        """数値から対応するEnumを取得"""
        for item in cls:
            if item.numeric_value == value:
                return item
        raise ValueError(f"無効な受注角度の値: {value}")
    
    @classmethod
    def from_symbol(cls, symbol):
        """記号から対応するEnumを取得"""
        for item in cls:
            if item.symbol == symbol:
                return item
        raise ValueError(f"無効な受注角度の記号: {symbol}")
    
    @classmethod
    def get_choices(cls):
        """フォーム用の選択肢を取得"""
        return [(item.numeric_value, f"{item.symbol} ({item.description})") for item in cls]
    
    @classmethod
    def get_symbol_choices(cls):
        """記号での選択肢を取得"""
        return [(item.symbol, f"{item.symbol} ({item.description})") for item in cls]
    
    def __str__(self):
        return self.symbol


class ProjectStatus(Enum):
    """プロジェクトステータスの列挙型"""
    PLANNING = ("planning", "企画中")
    IN_PROGRESS = ("in_progress", "進行中")
    COMPLETED = ("completed", "完了")
    CANCELLED = ("cancelled", "中止")
    ON_HOLD = ("on_hold", "保留")
    
    def __init__(self, status_value, description):
        self.status_value = status_value
        self.description = description
    
    @classmethod
    def get_choices(cls):
        """フォーム用の選択肢を取得"""
        return [(item.status_value, item.description) for item in cls]
    
    @classmethod
    def from_value(cls, value):
        """値から対応するEnumを取得"""
        for item in cls:
            if item.status_value == value:
                return item
        raise ValueError(f"無効なプロジェクトステータス: {value}")
    
    def __str__(self):
        return self.description