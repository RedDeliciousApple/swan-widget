import sys
import random
import os
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPoint, QTimer


class SwanWidget(QWidget):
    def __init__(self):
        super().__init__()
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
        image_path = os.path.join(script_dir, "swan.png")  # Ensure correct path
        
        # Load swan image and resize it
        self.swan_pixmap = QPixmap(image_path).scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)
        self.resize(self.swan_pixmap.size())

        # Remove window frame & set transparency
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Label to display swan image
        self.label = QLabel(self)
        self.label.setPixmap(self.swan_pixmap)
        self.label.setMask(self.swan_pixmap.mask())

        # Dragging variables
        self.dragging = False
        self.offset = QPoint()

        # List of test quotes
        self.all_quotes = [
            "Goedendag.",
            "William III? Tsk.",
            "Public opinion is ignorant and bigoted.",
            "Would you like to be pecked?",
            "I am not food.",
            "How many open tabs do you have right now? Be honest."
        ]
        self.quote_pool = self.all_quotes.copy()
        random.shuffle(self.quote_pool)

        self.speech_bubble = None  
        self.is_speaking = False  

    def get_unique_quote(self):
        if not self.quote_pool:
            self.quote_pool = self.all_quotes.copy()
            random.shuffle(self.quote_pool)
        return self.quote_pool.pop()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print("[DEBUG] Swan clicked!")
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            self.react_to_click()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            print("[DEBUG] Double-click detected! Quacking!")

         # Get absolute path of quack.mp3 (works regardless of how script is run)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            quack_path = os.path.join(script_dir, "quack.mp3")

            # Play sound using full path
            os.system(f'afplay "{quack_path}"')

    def react_to_click(self):
        if self.is_speaking:
            return
        print("[DEBUG] Reacting to click!")
        self.is_speaking = True
        self.show_speech_bubble()

    def show_speech_bubble(self):
        if self.speech_bubble:
            self.speech_bubble.hide()
            self.speech_bubble.deleteLater()
            self.speech_bubble = None

        random_quote = self.get_unique_quote()
        print(f"[DEBUG] Speech bubble text: {random_quote}")

        self.speech_bubble = SpeechBubble(self, random_quote)
        self.speech_bubble.move_near_swan(self.x(), self.y(), self.width())
        self.speech_bubble.show()

        QTimer.singleShot(2000, self.hide_speech_bubble)

    def hide_speech_bubble(self):
        if self.speech_bubble:
            self.speech_bubble.setParent(None)
            self.speech_bubble.hide()
            self.speech_bubble.deleteLater()
            self.speech_bubble = None
        self.is_speaking = False
        print("[DEBUG] Finished speaking!")

class SpeechBubble(QWidget):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.label = QLabel(text, self)
        self.label.setStyleSheet("background: white; color: black; border: 2px solid black; border-radius: 5px; padding: 5px; font-size: 12px;")
        self.label.adjustSize()
        self.resize(self.label.size())

    def move_near_swan(self, swan_x, swan_y, swan_width):
        bubble_x = swan_x + (swan_width // 2) - (self.width() // 2)
        bubble_y = swan_y - 30
        print(f"[DEBUG] Moving speech bubble to: ({bubble_x}, {bubble_y})")
        self.move(bubble_x, bubble_y)

app = QApplication(sys.argv)
swan = SwanWidget()
swan.show()
sys.exit(app.exec())
