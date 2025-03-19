import sys
import os
import time
import random
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QMenu
from PyQt6.QtGui import QPixmap, QPainter, QImage, QScreen, QMovie
from PyQt6.QtCore import Qt, QTimer, QPoint, QEvent, QSize

class SwanWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Configure the window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Create a QLabel to display the GIF
        self.swan_label = QLabel(self)
        self.swan_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the image

        # Load GIF
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gif_path = os.path.join(script_dir, "swan.gif")  
        self.swan_movie = QMovie(gif_path)

        # **🔹 Force GIF Scaling**
        target_size = QSize(120, 120)  # Adjust to your desired size
        self.swan_movie.setScaledSize(target_size)  # ✅ This resizes the GIF itself

        self.swan_label.setMovie(self.swan_movie)
        self.swan_movie.start()

        # Resize QLabel and widget to match GIF
        self.swan_label.resize(target_size)
        self.resize(target_size)

        # Dragging variables
        self.dragging = False
        self.offset = QPoint()
        self.mouse_moved = False  # Track if the mouse moved

        # Click tracking
        self.click_count = 0  # Track number of clicks
        self.click_stage = 1  # Default click stage

        # Reset click quotes
        self.click_reset_timer = QTimer(self)
        self.click_reset_timer.setSingleShot(True)
        self.click_reset_timer.timeout.connect(self.reset_click_stage)


        # Stage 1: Click Quotes
        self.click_quotes = [
            "Goedendag.",
            "I am not food.",
            "Hm? Yes, I'm still here.",
            "Ah, you remembered I exist. Touching.",
            "If you require assistance\nwith mathematics, I am available.",
            "What are your thoughts on annuities?",
            "No ribbon, thank you.\nLet us not make a spectacle of this.",
            "The Dutch fleet was the best in Europe.\nI trust it still exists?",
            "I concede 'True Freedom'wasn't the best slogan...\nbut it was ideologically sound.",
            "Shall we discuss shipbuilding?\nNo? Pity.",
            "You appear free of obligations.\nMust be nice."
    
        ]
        self.quote_pool = []  # ✅ Initialize as empty (it will be filled on demand)

        # Stage 2: Annoyed Click Quotes
        self.annoyed_click_quotes = [
            "I am not a rubber duck. \nThis is undignified.",
            "You are persistent.",
            "Please refrain—I bruise easily,\n historically speaking.",
            "Must you?",
            "This is harassment.",
            "You're fortunate my brother isn't \nthe one dealing with this."
        
        ]
        
        self.speech_bubble = None  
        self.is_speaking = False  

        # Start idle animation timer
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.tiny_float)
        self.start_idle_animation()
    
        # Start idle speech timer
        self.idle_speech_timer = QTimer(self)
        self.idle_speech_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.idle_speech_timer.timeout.connect(self.trigger_idle_speech)
        self.idle_speech_timer.start(1800000)  # 30 minutes(adjust for testing)

        # Dragging speech timer
        self.drag_speech_timer = QTimer(self)
        self.drag_speech_timer.timeout.connect(self.trigger_drag_speech)
        self.drag_start_time = None  # Track when dragging started
        self.drag_stage = 0  # Tracks whether 1s or 6s complaint has triggered

        # Feeding Counter
        self.feed_count = 0  # Track how many stroopwafels were eaten today


    def update_size(self):
        """Adjust the widget size to match a resized GIF."""
        original_size = self.swan_movie.frameRect().size()

        # Define a fixed width and calculate proportional height
        fixed_width = 100  # Change this if needed
        aspect_ratio = original_size.height() / original_size.width()
        new_height = int(fixed_width * aspect_ratio)  # Keep proportions

        self.swan_label.resize(fixed_width, new_height)
        self.resize(fixed_width, new_height)  # Resize the widget itself



    # Menu
    def contextMenuEvent(self, event):
        """Opens right-click menu."""
        menu = QMenu(self)

        # Screenshot
        screenshot_action = menu.addAction("Screenshot")
        screenshot_action.triggered.connect(self.take_screenshot)

        # "Feed Stroopwafel" 
        feed_action = menu.addAction("Feed Stroopwafel")
        feed_action.triggered.connect(self.spawn_stroopwafel)

        # Exit
        exit_action = menu.addAction("Resign")
        exit_action.triggered.connect(self.close)

        menu.exec(event.globalPos())

    def take_screenshot(self):
        """Captures the screen and automatically saves it to the Desktop with a timestamp."""
        screen = QApplication.primaryScreen()
        if not screen:
            print("[DEBUG] No screen detected!")  # Failsafe
            return
        
        """Hides the swan & menu before capturing a screenshot."""
        self.hide()  # Hide the swan
        self.close()  # Close the menu
        
        QTimer.singleShot(200, self.capture_and_restore)  # Wait briefly

    def capture_and_restore(self):
        """Takes the screenshot and restores the swan."""
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0)

        # Format timestamp like macOS screenshots
        timestamp = time.strftime("%Y-%m-%d at %H.%M.%S")
        desktop_path = os.path.expanduser("~/Desktop")
        save_path = os.path.join(desktop_path, f"Screenshot {timestamp}.png")

        # Save the screenshot
        screenshot.save(save_path, "PNG")

        print(f"[DEBUG] Screenshot saved: {save_path}")

        self.show()  # Bring the swan back
        
        self.show_speech_bubble("I trust this is not evidence of treason.")

    def spawn_stroopwafel(self):
        """Creates a stroopwafel at a random position."""
        if self.feed_count >= 3:
            self.show_speech_bubble("I have made my decision. There will be no further consumption.")
            return  # Stops spawning if he's full

        screen_geometry = QApplication.primaryScreen().geometry()
        max_x, max_y = screen_geometry.width(), screen_geometry.height()

        # Random position (avoiding the swan’s location)
        while True:
            rand_x = random.randint(50, max_x - 150)  # Avoid screen edges
            rand_y = random.randint(50, max_y - 150)

            if not (self.x() - 50 <= rand_x <= self.x() + 50 and self.y() - 50 <= rand_y <= self.y() + 50):
                break  # Ensure it doesn't spawn directly on the swan

        print("[DEBUG] Stroopwafel spawned at:", rand_x, rand_y)

        self.stroopwafel = StroopwafelWidget(self, rand_x, rand_y)
        self.stroopwafel.show()

        self.raise_()
        self.repaint()
 

    def feed_swan(self):
        """Handles what happens when the swan eats a stroopwafel."""
        if self.feed_count < 3:  
            self.feed_count += 1
            self.show_speech_bubble(quote=random.choice([
                "A fine offering. I approve.",
                "Hmph. Well. I shall not refuse efficiency.",
                "Very well. Thank you.\n But do not make a habit of this.",
                "I am not certain this is a balanced diet.",
            ]))

        if self.feed_count == 3:
            self.show_speech_bubble("I have made my decision. There will be no further consumption.")


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.mouse_moved = False  # Track movement

                 
    def mouseMoveEvent(self, event):
        if self.dragging:
            if (event.pos() - self.offset).manhattanLength() > 3:  # Detect dragging
                if not self.mouse_moved:
                    print("[DEBUG] Swan dragged!")
                    self.mouse_moved = True
                    self.drag_start_time = time.time()  # Start drag timer
                    self.drag_stage = 0  # Reset drag stage

                new_x = event.globalPosition().toPoint().x() - self.offset.x()
                new_y = event.globalPosition().toPoint().y() - self.offset.y()
                self.move(new_x, new_y)


                # Check if it's time for a complaint
                elapsed = time.time() - self.drag_start_time
                if elapsed >= 1 and self.drag_stage == 0:
                    self.trigger_drag_speech(stage=1)  # First complaint at 1s
                    self.drag_stage = 1
                elif elapsed >= 6 and self.drag_stage == 1:
                    self.trigger_drag_speech(stage=2)  # Second complaint at 6s
                    self.drag_stage = 2

    
    
    def mouseReleaseEvent(self, event):
        """Stops dragging behavior, resets timers, and handles click escalation."""
        if self.dragging:
            self.dragging = False
            if self.mouse_moved:
                print("[DEBUG] Dragging stopped.")
                return  # Prevents resetting idle timer for drags
    
        # **Force squish with a slight delay (prevents race conditions)**
        QTimer.singleShot(30, lambda: self.small_squish())

        # **Reset idle speech timer when click is registered**
        self.idle_speech_timer.start(1800000)  # 30 minutes (adjust for testing)

        # ✅ Track the click count (but don't reset timer every click)
        self.click_count += 1

        # ✅ Start the **30-second click timer ONCE** (if not already running)
        if not self.click_reset_timer.isActive():
            print("[DEBUG] Click escalation timer started (30s).")
            self.click_reset_timer.start(30000)  # 30-second fixed reset

        # ✅ Escalate to Stage 2 if clicked 5+ times within 30s
        if self.click_count >= 5:
            self.click_stage = 2

        print(f"[DEBUG] Click count: {self.click_count}, Click stage: {self.click_stage}")

        # **Click escalation tracking**
        current_time = time.time()

        # **Trigger click speech**
        if self.click_stage == 1:
            self.show_speech_bubble(self.get_click_quote())
        else:
            self.show_speech_bubble(self.get_annoyed_click_quote())




    def get_click_quote(self):
        """Returns a non-repeating quote from Stage 1 click quotes."""
        if not self.quote_pool:  # ✅ If empty, refill from master list
            self.quote_pool = self.click_quotes.copy()  
            random.shuffle(self.quote_pool)  # ✅ Shuffle when refilling

        new_quote = self.quote_pool.pop()  # ✅ Always removes a quote from the pool
        print(f"[DEBUG] Selected click quote: {new_quote}, Remaining in pool: {len(self.quote_pool)}")  # Debugging

        return new_quote  # ✅ Returns the selected quote

       
    def get_annoyed_click_quote(self):
        """Returns a random annoyed quote from Stage 2 click quotes."""
        return random.choice(self.annoyed_click_quotes)  # ✅ Now correctly refers to the `__init__` list

    def reset_click_stage(self):
        """Resets click count and stage back to normal after cooldown."""
        print("[DEBUG] Click cooldown over, resetting to Stage 1.")
        self.click_count = 0
        self.click_stage = 1



    def get_dragging_quote(self, stage):
        """Returns a dragging quote depending on stage."""
        if stage == 1:
            dragging_quotes = [
                "Where are you taking me?",
                "I should warn you, I do not travel lightly.",
                "Do be careful."
            ]
        else:
            dragging_quotes = [
                "Do you intend to carry me to The Hague?",
                "I see you prefer decentralization literally.",
                "I'm starting to think you find this amusing."
            ]
        return random.choice(dragging_quotes)

    
    
    def trigger_drag_speech(self, stage):
        """Triggers speech when dragging reaches 1s and 6s."""
        if not self.dragging:
            return  # Don't speak if dragging stopped

        quote = self.get_dragging_quote(stage)
        self.show_speech_bubble(quote)



  # Small Squish Effect
    def small_squish(self):
        """Squishes the GIF vertically with width compression for better effect."""
        if hasattr(self, "is_squishing") and self.is_squishing:
            return  # ❌ Prevents starting a new squish while restoring
        
        print("[DEBUG] Squish triggered!")
        self.is_squishing = True  # ✅ Mark as squishing

        original_size = self.swan_movie.scaledSize()  # Get current GIF size
        squish_size = QSize(int(original_size.width()), int(original_size.height() * 0.95))  # Compress height

        # Apply squish
        self.swan_movie.setScaledSize(squish_size)
        self.swan_label.repaint()  # ✅ Force immediate redraw

        # Restore after 150ms (adjust if needed)
        QTimer.singleShot(150, lambda: self.restore_pixmap(original_size))

    def restore_pixmap(self, original_size):
        """Restores the GIF back to normal size with a forced refresh."""
        print("[DEBUG] Restoring size!")

        self.swan_movie.setScaledSize(original_size)
        self.swan_label.repaint()  # ✅ Force immediate update

        # ✅ Unlock squishing after full restore
        QTimer.singleShot(50, self.unlock_squish)

    def unlock_squish(self):
        """Allows squishing again after fully restoring."""
        self.is_squishing = False  # ✅ Reset flag
        print("[DEBUG] Squish fully restored!")

    

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:

            # Play quack sound (absolute path)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            quack_path = os.path.join(script_dir, "quack.mp3")
            os.system(f'afplay "{quack_path}"')  # For Mac, replace with `playsound` for Windows/Linux

    # Idle Quotes
    def get_idle_quote(self):
        """Returns a time-based idle quote."""
        current_hour = time.localtime().tm_hour  # Get current hour

        if 5 <= current_hour < 12:  # Morning (5 AM - 12 PM)
            return random.choice([
                "Today feels like a good day\n to not get assassinated again.",
                "It's not too early for public debate.",
                "Have you reviewed the state finances yet?",
                "One day you're a statesman; \nnext day you're a desktop bird. \nC'est la vie.",
            ])
        elif 12 <= current_hour < 18:  # Afternoon (12 PM - 6 PM)
            return random.choice([
                "I suppose I could read your clipboard ... \noh, intriguing choice of words there.",
                "Bold of you to assume \nswans don't judge your open tabs.",
                "A moment of peace is rare. \nBest make use of it.",
                "This silence is suspicious. \nAre you actually working?",
            ])
        elif 18 <= current_hour < 23:  # Evening (6 PM - 11 PM)
            return random.choice([
                "If you are idle, why not engage in a proof? \nI have several favorites.",
                "Dinner? Do not look at me. \nHow very presumptuous of you.",
                "A good book might ease the mind at this hour. \nPreferably not a political one.",
                "I suppose I do not mind your company.",
                "Some insist philosophy leads to happiness. \nI remain unconvinced.",
                "Public opinion is ignorant and bigoted."
            ])
        else:  # Late Night (11 PM - 5 AM)
            return random.choice([
                "You remain awake. \nI can only assume this is deliberate.",
                "Mathematics at this hour is ill-advised, \nunless you intend to torment yourself.",
                "Is insomnia fashionable in your century?",
                "Cornelis said what he thought...It cost him dearly.",
                "Sir William claimed he retired from politics. \nI suspect he simply grew tired of negotiating with us."
            ])

    def trigger_idle_speech(self):
        """Shows an idle speech bubble if the swan hasn't spoken in a while."""
        idle_quote = self.get_idle_quote()  # ✅ Always fetches a new idle quote
        print(f"[DEBUG] Selected idle quote: {idle_quote}")

        self.show_speech_bubble(idle_quote, idle_speech=True)  # ✅ Passes `idle_speech=True`




    # Speech bubble
    def show_speech_bubble(self, quote=None, idle_speech=False):
        """Shows a speech bubble but prevents interruptions if the swan is already speaking."""
        
        if self.is_speaking:
            print("[DEBUG] Ignoring new speech - swan is still speaking.")
            return  # ❌ Prevents speech interruptions

        self.is_speaking = True  # ✅ starts speaking

        print(f"[DEBUG] 🎤 Speech bubble shown: {quote}")

        # Bubble Location 
        self.speech_bubble = SpeechBubble(self, quote)
        self.speech_bubble.spawn_near_swan(self.x(), self.y(), self.width(), self.height())
        self.speech_bubble.show()
        

        # ✅ Fixed 3-second duration for all speech
        self.bubble_timer = QTimer.singleShot(3000, self.hide_speech_bubble)

        # ✅ Only apply extra focus settings if it's idle speech
        if idle_speech:
            self.speech_bubble.setWindowFlags(
                Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.BypassWindowManagerHint
            )
            self.speech_bubble.show()
            self.speech_bubble.raise_()
            self.speech_bubble.update()



    def hide_speech_bubble(self):
        if self.speech_bubble:
            self.speech_bubble.setParent(None)
            self.speech_bubble.hide()
            self.speech_bubble.deleteLater()
            self.speech_bubble = None
            self.is_speaking = False
            print("[DEBUG] Finished speaking!")


    
    # idle animation
    def start_idle_animation(self):
        """Starts the idle animation loop with a random delay."""
        delay = random.randint(10000, 15000)  # Random delay between 10-15 sec
        self.idle_timer.start(delay)

    def tiny_float(self):
        """Makes the swan move up/down slightly, then resets."""
        if hasattr(self, "is_floating") and self.is_floating:
            return  # Prevent overlapping animations

        self.is_floating = True
        float_distance = random.choice([-2, 2])  # Random small movement up/down

        # Move the swan up/down slightly
        self.move(self.x(), self.y() + float_distance)

        # Reset position after 200ms
        QTimer.singleShot(200, lambda: self.reset_float(float_distance))

    def reset_float(self, float_distance):
        """Resets the swan's position after floating."""
        self.move(self.x(), self.y() - float_distance)  # Move back
        self.is_floating = False  # Ready for next float

        # Restart idle animation with a new random delay
        self.start_idle_animation()
    
    

# Speech Bubble Class
class SpeechBubble(QWidget):
    def __init__(self, parent, text):
        super().__init__(parent)

        # ✅ Prevents focus stealing
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |  # Marks it as a "tooltip" window (low priority)
            Qt.WindowType.BypassWindowManagerHint  # Prevents focus issues
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.raise_()  # ✅ Forces speech bubble to always be on top


        self.label = QLabel(text, self)
        self.label.setStyleSheet(
            "background: white; color: black; border: 2px solid black; border-radius: 5px; padding: 5px; font-size: 12px;"
        )
        self.label.adjustSize()
        self.resize(self.label.size())


    def spawn_near_swan(self, swan_x, swan_y, swan_width, swan_height):
        """Move speech bubble above the swan without overlapping."""
        
        screen = QApplication.primaryScreen().availableGeometry()  # ✅ Mac-friendly screen area

        # DEBUG PRINTING
        # print(f"[DEBUG] Screen Top: {screen.top()}, Screen Height: {screen.height()}")
        # print(f"[DEBUG] Swan Position -> X: {swan_x}, Y: {swan_y}")

        # Center horizontally
        bubble_x = swan_x + (swan_width // 2) - (self.width() // 2)

        # 🔥 NEW FIX: Adjust for macOS top bar
        bubble_y = max(swan_y - self.height() - 5, screen.top())  # ✅ Prevents negative values


        # 🛑 Prevent it from going off-screen on the left
        if bubble_x < 10:
            bubble_x = 10

        # 🛑 Prevent it from going off-screen on the right
        if bubble_x + self.width() > screen.width() - 10:
            bubble_x = screen.width() - self.width() - 10

        # FINAL DEBUG PRINT
        # print(f"[DEBUG] Final Bubble Position -> X: {bubble_x}, Y: {bubble_y}")
        # print("[DEBUG] --------------------------------------")

        # Move speech bubble to adjusted position
        self.move(bubble_x, bubble_y)




        

class StroopwafelWidget(QWidget):
    def __init__(self, parent, x, y):
        super().__init__(parent)
       
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |  # Prevents it from acting like a full app window
            Qt.WindowType.BypassWindowManagerHint  # Stops focus stealing
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "stroopwafel.png")

        self.pixmap = QPixmap(image_path).scaledToWidth(50, Qt.TransformationMode.SmoothTransformation)
        self.resize(50, 50)  # Adjust as needed
        self.move(x, y)

        self.dragging = False
        self.offset = QPoint()
    
        self.delete_timer = QTimer(self)  # ✅ Create a timer for disappearance
        self.delete_timer.setSingleShot(True)  # ✅ Ensure it only triggers once
        self.delete_timer.timeout.connect(self.fade_out)  # ✅ Connect it to fade_out()
        self.delete_timer.start(2000)  # ✅ Start the timer (2 seconds)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawPixmap(0, 0, self.pixmap)

    def mousePressEvent(self, event):
        """Handles when the Stroopwafel is clicked (attempting to feed the swan)."""
        if event.button() == Qt.MouseButton.LeftButton:
            
            # ✅ Stop the timer so it doesn't auto-disappear
            if self.delete_timer.isActive():
                self.delete_timer.stop()

            # ✅ Allow dragging now
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_x = event.globalPosition().toPoint().x() - self.offset.x()
            new_y = event.globalPosition().toPoint().y() - self.offset.y()
            self.move(new_x, new_y)

            # Check if it's over the swan (collision detection)
            if self.parent().geometry().intersects(self.geometry()):
                self.parent().feed_swan()
                self.close()  # Remove stroopwafel after feeding

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def fade_out(self):
        """Remove stroopwafel if ignored."""
        self.close()


# Run the application
app = QApplication(sys.argv)
swan = SwanWidget()
swan.show()
sys.exit(app.exec())




