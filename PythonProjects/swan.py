import sys
import random
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPoint, QTimer

class SwanWidget(QWidget):
    def __init__(self):
        super().__init__()
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
        image_path = os.path.join(script_dir, "swan.png")  # Create the correct path
        
        # Load swan image and resize it (keeping aspect ratio)
        self.swan_pixmap = QPixmap(image_path).scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)
        
        # Set window size to image size
        self.resize(self.swan_pixmap.size())

        # Remove window frame & set transparency
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Label to display swan image
        self.label = QLabel(self)
        self.label.setPixmap(self.swan_pixmap)
        self.label.setMask(self.swan_pixmap.mask())  # Makes only swan visible

        # Dragging variables
        self.dragging = False
        self.offset = QPoint()

        # List of test quotes (cycling without replacement)
        self.all_quotes = [
            "Goedendag.",
            "William III? Tsk.",
            "Public opinion is ignorant and bigoted.",
            "War is an obstacle to freedom.",
            "Quack.",
            "I am not food."
        ]
        self.quote_pool = self.all_quotes.copy()  # Copy for shuffling
        random.shuffle(self.quote_pool)  # Initial shuffle

        self.speech_bubble = None  

    def get_unique_quote(self):
        """Selects a unique quote without repeating until all are used."""
        if not self.quote_pool:  # If empty, refill and reshuffle
            self.quote_pool = self.all_quotes.copy()
            random.shuffle(self.quote_pool)  # Randomize again

        return self.quote_pool.pop()  # Take the last one from the shuffled list

    def mousePressEvent(self, event):
        """Detect when mouse clicks the swan & trigger response"""
        if event.button() == Qt.MouseButton.LeftButton:
            print("[DEBUG] Swan clicked!")  # Confirm click is detected
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        """Move the swan when dragged"""
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        """Stop dragging"""
        if self.dragging:
            self.dragging = False
            self.react_to_click()  # React after releasing click

    def react_to_click(self):
        """Make the swan react when clicked."""
        print("[DEBUG] Reacting to click!")  # Confirm function is called
        self.show_speech_bubble()  

    def show_speech_bubble(self):
        """Show a random swan quote in a floating bubble."""
        if self.speech_bubble:  
            self.speech_bubble.close()  # Close old one before making new one

        random_quote = self.get_unique_quote()  # Get a unique quote
        print(f"[DEBUG] Speech bubble text: {random_quote}")  

        # Create the speech bubble
        self.speech_bubble = SpeechBubble(self, random_quote)
        self.speech_bubble.move_near_swan(self.x(), self.y(), self.width())  
        self.speech_bubble.show()
    
        # Hide it after 2 seconds
        QTimer.singleShot(2000, self.speech_bubble.close)


class SpeechBubble(QWidget):
    """A floating speech bubble window for the swan."""
    def __init__(self, parent, text):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Label for speech bubble
        self.label = QLabel(text, self)
        self.label.setStyleSheet("background: white; color: black; border: 2px solid black; border-radius: 5px; padding: 5px; font-size: 12px;")
        self.label.adjustSize()

        # Resize the window to fit text
        self.resize(self.label.size())

    def move_near_swan(self, swan_x, swan_y, swan_width):
        """Position speech bubble slightly above swan's head."""
        bubble_x = swan_x + (swan_width // 2) - (self.width() // 2)  # Centered above swan
        bubble_y = swan_y - 30  # Adjusted for better positioning
        print(f"[DEBUG] Moving speech bubble to: ({bubble_x}, {bubble_y})")  
        self.move(bubble_x, bubble_y)

# Run the app
app = QApplication(sys.argv)
swan = SwanWidget()
swan.show()
sys.exit(app.exec())
