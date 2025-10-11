import time
from typing import Dict, Optional
from PyQt6.QtWidgets import QRadioButton, QButtonGroup
import logging

logger = logging.getLogger(__name__)


class RadioButtonHelper:
    """ラジオボタン2回押し解除を実現するヘルパークラス"""
    
    def __init__(self, click_threshold: float = 0.5):
        """
        初期化
        
        Args:
            click_threshold: クリック判定の閾値（秒）
        """
        self.last_clicked: Dict[str, Optional[QRadioButton]] = {}
        self.last_time: Dict[str, float] = {}
        self.click_threshold = click_threshold
    
    def handle_click(self, button: QRadioButton, group_name: str, 
                    button_group: QButtonGroup) -> bool:
        """
        ラジオボタンのクリックを処理（2回押しで解除）
        
        Args:
            button: クリックされたラジオボタン
            group_name: ボタングループ名（識別用）
            button_group: QButtonGroupオブジェクト
            
        Returns:
            解除された場合はTrue、選択された場合はFalse
        """
        current_time = time.time()
        
        # 同じボタンが短時間に2回押された場合
        if (self.last_clicked.get(group_name) == button and
            current_time - self.last_time.get(group_name, 0) < self.click_threshold):
            
            # ボタンを解除
            button.setAutoExclusive(False)
            button.setChecked(False)
            button.setAutoExclusive(True)
            
            self.last_clicked[group_name] = None
            logger.debug(f"ラジオボタン解除: {group_name}")
            return True
        else:
            # 通常の選択
            self.last_clicked[group_name] = button
            self.last_time[group_name] = current_time
            logger.debug(f"ラジオボタン選択: {group_name}")
            return False
    
    def reset_group(self, group_name: str):
        """
        特定のグループの状態をリセット
        
        Args:
            group_name: ボタングループ名
        """
        self.last_clicked[group_name] = None
        self.last_time[group_name] = 0
        logger.debug(f"ラジオボタングループをリセット: {group_name}")
    
    def reset_all(self):
        """全グループの状態をリセット"""
        self.last_clicked.clear()
        self.last_time.clear()
        logger.debug("全ラジオボタングループをリセット")
