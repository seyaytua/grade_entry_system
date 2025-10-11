from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PIL import Image
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ImagePreviewWidget(QGraphicsView):
    """画像プレビューウィジェット（PDF複数ページ対応）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        self.current_pixmap_item = None
        self.current_file_path = None
        self.pdf_pages = []  # PDFの各ページ
        self.current_page = 1
        self.total_pages = 1
    
    def load_image(self, file_path: str) -> bool:
        """
        画像またはPDFを読み込む
        
        Args:
            file_path: ファイルパス
            
        Returns:
            読み込み成功: True, 失敗: False
        """
        try:
            self.current_file_path = file_path
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                return self.load_pdf(file_path)
            else:
                return self.load_image_file(file_path)
        
        except Exception as e:
            logger.error(f"ファイル読み込みエラー: {e}")
            return False
    
    def load_image_file(self, file_path: str) -> bool:
        """画像ファイルを読み込む"""
        try:
            # PILで画像を開く
            pil_image = Image.open(file_path)
            
            # RGBに変換
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # QImageに変換
            width, height = pil_image.size
            qimage = QImage(
                pil_image.tobytes(), width, height,
                width * 3, QImage.Format.Format_RGB888
            )
            
            # QPixmapに変換
            pixmap = QPixmap.fromImage(qimage)
            
            # シーンをクリア
            self.scene.clear()
            
            # 画像を追加
            self.current_pixmap_item = self.scene.addPixmap(pixmap)
            self.scene.setSceneRect(self.current_pixmap_item.boundingRect())
            
            # ズームをリセット
            self.reset_zoom()
            
            # PDFページ情報をリセット
            self.pdf_pages = []
            self.current_page = 1
            self.total_pages = 1
            
            logger.info(f"画像を読み込みました: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"画像読み込みエラー: {e}")
            return False
    
    def load_pdf(self, file_path: str) -> bool:
        """PDFファイルを読み込む"""
        try:
            import fitz  # PyMuPDF
            
            # PDFを開く
            pdf_document = fitz.open(file_path)
            self.total_pages = len(pdf_document)
            
            # 各ページを画像に変換して保存
            self.pdf_pages = []
            for page_num in range(self.total_pages):
                page = pdf_document[page_num]
                
                # ページを画像に変換（解像度150dpi）
                pix = page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72))
                
                # QImageに変換
                qimage = QImage(
                    pix.samples, pix.width, pix.height,
                    pix.stride, QImage.Format.Format_RGB888
                )
                
                # QPixmapに変換して保存
                pixmap = QPixmap.fromImage(qimage)
                self.pdf_pages.append(pixmap)
            
            pdf_document.close()
            
            # 最初のページを表示
            self.current_page = 1
            self.show_current_page()
            
            logger.info(f"PDFを読み込みました: {file_path} ({self.total_pages}ページ)")
            return True
        
        except ImportError:
            logger.error("PyMuPDF (fitz) がインストールされていません")
            # 代替処理: PIL + pdf2image を使用
            return self.load_pdf_with_pdf2image(file_path)
        
        except Exception as e:
            logger.error(f"PDF読み込みエラー: {e}")
            return False
    
    def load_pdf_with_pdf2image(self, file_path: str) -> bool:
        """pdf2imageを使用してPDFを読み込む（代替手段）"""
        try:
            from pdf2image import convert_from_path
            
            # PDFを画像に変換
            images = convert_from_path(file_path, dpi=150)
            self.total_pages = len(images)
            
            # 各ページをQPixmapに変換
            self.pdf_pages = []
            for pil_image in images:
                # RGBに変換
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                # QImageに変換
                width, height = pil_image.size
                qimage = QImage(
                    pil_image.tobytes(), width, height,
                    width * 3, QImage.Format.Format_RGB888
                )
                
                # QPixmapに変換して保存
                pixmap = QPixmap.fromImage(qimage)
                self.pdf_pages.append(pixmap)
            
            # 最初のページを表示
            self.current_page = 1
            self.show_current_page()
            
            logger.info(f"PDFを読み込みました (pdf2image): {file_path} ({self.total_pages}ページ)")
            return True
        
        except ImportError:
            logger.error("pdf2image がインストールされていません")
            return False
        
        except Exception as e:
            logger.error(f"PDF読み込みエラー (pdf2image): {e}")
            return False
    
    def show_current_page(self):
        """現在のページを表示"""
        if not self.pdf_pages or self.current_page < 1 or self.current_page > self.total_pages:
            return
        
        # シーンをクリア
        self.scene.clear()
        
        # 現在のページを表示
        pixmap = self.pdf_pages[self.current_page - 1]
        self.current_pixmap_item = self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(self.current_pixmap_item.boundingRect())
        
        # ズームをリセット
        self.reset_zoom()
    
    def prev_page(self):
        """前のページへ"""
        if self.current_page > 1:
            self.current_page -= 1
            self.show_current_page()
    
    def next_page(self):
        """次のページへ"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.show_current_page()
    
    def get_current_page(self) -> int:
        """現在のページ番号を取得"""
        return self.current_page
    
    def get_total_pages(self) -> int:
        """総ページ数を取得"""
        return self.total_pages
    
    def zoom_in(self):
        """拡大"""
        if self.zoom_factor < self.max_zoom:
            self.scale(1.1, 1.1)
            self.zoom_factor *= 1.1
    
    def zoom_out(self):
        """縮小"""
        if self.zoom_factor > self.min_zoom:
            self.scale(0.9, 0.9)
            self.zoom_factor *= 0.9
    

    

    def reset_zoom(self):
        """ズームをリセット"""
        self.resetTransform()
        self.zoom_factor = 1.0
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def go_to_page(self, page_number: int):
        """指定ページに移動（PDFのみ）"""
        if not hasattr(self, 'pdf_document') or not self.pdf_document:
            return
        
        if 1 <= page_number <= len(self.pdf_document):
            self.current_page = page_number
            self.display_current_page()

    def get_zoom_percentage(self) -> int:
        """ズーム率を取得（パーセント）"""
        return int(self.zoom_factor * 100)
    
    def wheelEvent(self, event):
        """マウスホイールイベント（ズーム）"""
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()