from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QLineEdit, QGridLayout, QSizePolicy,
                           QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QDateTime, pyqtSignal, QEvent
from PyQt6.QtGui import QFont, QColor
import json
import os
from PyQt6.QtWidgets import QApplication
from App.core.user._user_session_handler import session  # Import session handler
from App.core.database._db_user_attendance import attendance_db  # Import attendance database


class AttendanceTool(QWidget):
    """Attendance tracking tool for team members."""
    login_required = pyqtSignal()  # Signal to emit when login is required
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_checked_in = False
        self.pin = ""
        
        # Get language setting from config
        self.app = QApplication.instance()
        self.config = self.load_config()
        self.language = self.config.get("application", {}).get("language", "en")
        
        # Set up the main layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Create left panel (time and user info) - removed padding/margins
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        left_panel.setStyleSheet("""
            background-color: palette(base);
            border-radius: 8px;
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)  # Add minimal padding
        left_layout.setSpacing(2)  # Very compact spacing
        
        # Create a vertical spacer to push content toward vertical center
        left_layout.addStretch(1)
        
        # Current time display (large) - removed margins
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            font-size: 64px;
            font-weight: bold;
            color: palette(text);
        """)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Current date display - removed margins
        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            font-size: 18px;
            color: palette(text);
            margin-bottom: 5px;
        """)
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Set up timer to update date and time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Update every second
        self.update_datetime()  # Initial update
        
        # User info display - getting from session handler
        self.name_value = QLabel()
        self.name_value.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: palette(text);
            padding-top: 5px;
        """)
        self.name_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.dept_value = QLabel()
        self.dept_value.setStyleSheet("""
            font-size: 18px;
            color: palette(text);
            padding-bottom: 5px;
        """)
        self.dept_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Update user info from session handler
        self.update_user_info()
        
        # Check if the user is logged in, if not emit login_required signal
        if not session.is_logged_in():
            QTimer.singleShot(300, self.login_required.emit)  # Emit after a short delay
        
        # Add widgets to left panel
        left_layout.addWidget(self.time_label)
        left_layout.addWidget(self.date_label)
        
        # Add spacing between date and name
        spacer = QLabel()
        spacer.setMinimumHeight(20)  # Add space between date and name
        left_layout.addWidget(spacer)
        
        left_layout.addWidget(self.name_value)
        left_layout.addWidget(self.dept_value)
        
        # Add another stretch to balance the vertical centering
        left_layout.addStretch(1)
        
        # Create right panel (PIN input and numpad)
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Shape.StyledPanel)
        right_panel.setStyleSheet("""
            background-color: palette(base);
            border-radius: 8px;
            padding: 15px;
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # PIN display
        pin_label = QLabel("Enter PIN:")
        pin_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        pin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Modified PIN input to allow keyboard input
        self.pin_display = PinInputField(self)
        self.pin_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_display.setStyleSheet("""
            font-size: 24px;
            padding: 10px;
            background-color: palette(base);
            border: 1px solid palette(mid);
            border-radius: 5px;
            margin-bottom: 15px;
        """)
        # Connect the PIN input signals to our handler methods
        self.pin_display.digitAdded.connect(self.add_pin_digit)
        self.pin_display.backspacePressed.connect(self.backspace_pin)
        self.pin_display.escapePressed.connect(self.clear_pin)
        self.pin_display.enterPressed.connect(self.toggle_check_status)
        self.pin_display.setFocus()  # Set focus to PIN input field by default
        
        # Create numpad
        numpad_layout = QGridLayout()
        numpad_layout.setSpacing(10)
        
        # Add number buttons
        button_style = """
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.05);
                color: rgba(127, 127, 127, 1);
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 8px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.15);
            }
        """
        
        # Create number buttons 1-9
        for i in range(3):
            for j in range(3):
                num = i * 3 + j + 1
                button = QPushButton(str(num))
                button.setStyleSheet(button_style)
                button.clicked.connect(lambda _, digit=num: self.add_pin_digit(str(digit)))
                numpad_layout.addWidget(button, i, j)
        
        # Create 0 button and clear button
        zero_button = QPushButton("0")
        zero_button.setStyleSheet(button_style)
        zero_button.clicked.connect(lambda: self.add_pin_digit("0"))
        numpad_layout.addWidget(zero_button, 3, 1)
        
        # Del button now clears the PIN (switched with Clear)
        del_button = QPushButton("Del")
        del_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.05);
                color: rgba(127, 127, 127, 1);
                border: 1px solid #ff9800;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.15);
            }
        """)
        del_button.clicked.connect(self.clear_pin)  # Del now clears the PIN
        numpad_layout.addWidget(del_button, 3, 0, 1, 1)
        
        # Backspace button removes the last digit (function didn't change)
        backspace_button = QPushButton("←")
        backspace_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.05);
                color: rgba(127, 127, 127, 1);
                border: 1px solid #f44336;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.15);
            }
        """)
        backspace_button.clicked.connect(self.backspace_pin)
        numpad_layout.addWidget(backspace_button, 3, 2, 1, 1)
        
        # Check-in/Check-out button
        self.check_button = QPushButton("CHECK IN")
        self.check_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.check_button.clicked.connect(self.toggle_check_status)
        
        # Add widgets to right panel
        right_layout.addWidget(pin_label)
        right_layout.addWidget(self.pin_display)
        right_layout.addLayout(numpad_layout)
        right_layout.addWidget(self.check_button)
        right_layout.addStretch()
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)  # 1 part of the width
        main_layout.addWidget(right_panel, 1)  # 1 part of the width
        
        # Force focus to PIN field when shown
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Install event filter at application level to capture ALL keyboard events
        self.app.installEventFilter(self)
        
        # Now that all UI elements are created, check attendance status
        self.check_current_attendance_status()

    def load_config(self):
        """Load the application configuration from config.json."""        
        try:
            config_path = os.path.join(self.app.BASE_DIR.get_path('App'), 'config', 'config.json')
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"application": {"language": "en"}}

    def get_indonesian_day_name(self, day_number):
        """Convert Qt day number to Indonesian day name."""        
        # Qt days are 1-7 where 1 is Monday
        indonesian_days = {
            1: "Senin",
            2: "Selasa",
            3: "Rabu",
            4: "Kamis",
            5: "Jumat",
            6: "Sabtu",
            7: "Minggu"
        }
        return indonesian_days.get(day_number, "")
    
    def get_indonesian_month_name(self, month_number):
        """Convert month number (1-12) to Indonesian month name."""        
        # Month numbers are 1-12
        indonesian_months = {
            1: "Januari",
            2: "Februari",
            3: "Maret",
            4: "April",
            5: "Mei",
            6: "Juni",
            7: "Juli",
            8: "Agustus",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Desember"
        }
        return indonesian_months.get(month_number, "")

    def showEvent(self, event):
        """Called when the widget is shown."""
        # Force focus to PIN field when shown
        QTimer.singleShot(100, self.pin_display.setFocus)
        
        # Always refresh user info and attendance status when the widget is shown
        # This ensures the widget shows current user data after login/logout
        QTimer.singleShot(100, self.update_user_info)
        QTimer.singleShot(150, self.check_current_attendance_status)
        
        super().showEvent(event)
    
    def focusInEvent(self, event):
        """Called when the widget receives focus."""        
        # Always force focus to PIN field
        self.pin_display.setFocus()
        super().focusInEvent(event)

    def eventFilter(self, obj, event):
        """
        Global event filter to capture ALL keyboard input anywhere in the application
        when this attendance widget is visible.
        """
        # Only process events when this widget is visible
        if not self.isVisible():
            return False
            
        if event.type() == QEvent.Type.KeyPress:
            # Capture number keys (0-9) pressed anywhere
            key = event.key()
            
            # Process numeric keys (0-9)
            if Qt.Key.Key_0 <= key <= Qt.Key_9:
                # Set focus to PIN field and manually add the digit
                self.pin_display.setFocus()
                self.add_pin_digit(chr(key))
                return True  # Consume the event
                
            # Process control keys (Delete, Backspace, Enter)
            elif key == Qt.Key.Key_Delete:
                self.clear_pin()
                return True
            elif key == Qt.Key.Key_Backspace:
                self.backspace_pin()
                return True
            elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.toggle_check_status()
                return True
                
        # Pass all other events to the parent
        return super().eventFilter(obj, event)
    
    def update_datetime(self):
        """Update the date and time display."""        
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss"))
        
        # Format date based on language setting
        if self.language == "id":
            # Indonesian format
            day_name = self.get_indonesian_day_name(now.date().dayOfWeek())
            day = now.date().day()
            month_name = self.get_indonesian_month_name(now.date().month())
            year = now.date().year()
            self.date_label.setText(f"{day_name}, {day} {month_name} {year}")
        else:
            # English format (default)
            self.date_label.setText(now.toString("dddd, MMMM d, yyyy"))
    
    def add_pin_digit(self, digit):
        """Add a digit to the PIN display."""        
        if len(self.pin) < 6:  # Limit PIN to 6 digits
            self.pin += digit
            self.pin_display.setText("*" * len(self.pin))
            
            # If PIN reaches 6 digits (max length), automatically focus on check button
            if len(self.pin) == 6:
                self.check_button.setFocus()
    
    def clear_pin(self):
        """Clear the PIN."""        
        self.pin = ""
        self.pin_display.clear()
        self.pin_display.setFocus()  # Return focus to PIN field
    
    def backspace_pin(self):
        """Remove the last digit from the PIN."""        
        if self.pin:
            self.pin = self.pin[:-1]
            self.pin_display.setText("*" * len(self.pin))
    
    def check_current_attendance_status(self):
        """Check the current attendance status from the database."""        
        if not session.is_logged_in():
            return
            
        try:
            # Get current user ID from session
            user_id = session.get_user_id()
            if not user_id:
                print("No user ID found in session")
                return
                
            # Get latest attendance record for today for the CURRENT user
            latest_record = attendance_db.get_latest_attendance_record(user_id)
            
            # If record exists and has check-in time but no check-out time, user is checked in
            if latest_record and latest_record.get('check_in_time') and not latest_record.get('check_out_time'):
                self.is_checked_in = True
                
                # Update button to show CHECK OUT
                self.check_button.setText("CHECK OUT")
                self.check_button.setStyleSheet("""
                    QPushButton {
                        font-size: 18px;
                        font-weight: bold;
                        background-color: #f44336; /* Red color for check-out */
                        color: white;
                        border-radius: 8px;
                        margin-top: 15px;
                    }
                    QPushButton:hover {
                        background-color: #d32f2f;
                    }
                """)
            else:
                self.is_checked_in = False
                
                # Update button to show CHECK IN
                self.check_button.setText("CHECK IN")
                self.check_button.setStyleSheet("""
                    QPushButton {
                        font-size: 18px;
                        font-weight: bold;
                        background-color: #4CAF50; /* Green color for check-in */
                        color: white;
                        border-radius: 8px;
                        margin-top: 15px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
        except Exception as e:
            print(f"Failed to check attendance status: {e}")
    
    def toggle_check_status(self):
        """Process check-in or check-out based on current status."""        
        if not session.is_logged_in():
            QMessageBox.warning(self, "Login Required", 
                                "You must be logged in to use the attendance tool.")
            QTimer.singleShot(300, self.login_required.emit)
            return
            
        # Verify PIN before proceeding
        if not self.pin:
            QMessageBox.warning(self, "PIN Required", "Please enter your attendance PIN.")
            self.pin_display.setFocus()
            return
            
        # Verify the PIN with the database
        if not attendance_db.verify_attendance_pin(self.pin):
            QMessageBox.warning(self, "Invalid PIN", 
                               "The PIN you entered is invalid. Please try again.")
            self.clear_pin()
            return
            
        # PIN verified, proceed with check-in or check-out
        try:
            success = False
            
            if self.is_checked_in:
                # Process check-out
                success = attendance_db.check_out()
                if success:
                    QMessageBox.information(self, "Check Out Successful", 
                                          "You have successfully checked out.")
                    self.is_checked_in = False
                    self.check_button.setText("CHECK IN")
                    self.check_button.setStyleSheet("""
                        QPushButton {
                            font-size: 18px;
                            font-weight: bold;
                            background-color: #4CAF50; /* Green color for check-in */
                            color: white;
                            border-radius: 8px;
                            margin-top: 15px;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                    """)
                else:
                    QMessageBox.warning(self, "Check Out Failed", 
                                       "Failed to check out. Please try again or contact support.")
            else:
                # Process check-in
                success = attendance_db.check_in()
                if success:
                    QMessageBox.information(self, "Check In Successful", 
                                          "You have successfully checked in.")
                    self.is_checked_in = True
                    self.check_button.setText("CHECK OUT")
                    self.check_button.setStyleSheet("""
                        QPushButton {
                            font-size: 18px;
                            font-weight: bold;
                            background-color: #f44336; /* Red color for check-out */
                            color: white;
                            border-radius: 8px;
                            margin-top: 15px;
                        }
                        QPushButton:hover {
                            background-color: #d32f2f;
                        }
                    """)
                else:
                    QMessageBox.warning(self, "Check In Failed", 
                                      "Failed to check in. You may have already checked in today.")
                                      
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            
        # After checking in/out, clear the PIN and focus back on PIN field
        self.clear_pin()
    
    def update_user_info(self):
        """Update user information from session handler."""        
        if session.is_logged_in():
            # Get full name from session handler
            fullname = session.get_fullname() or session.get_username() or "Unknown"
            self.name_value.setText(fullname)
            
            # Get complete user data from session handler
            user_data = session.get_user_data()
            
            # Mendapatkan departemen dari user data yang ada di session
            # tanpa perlu mengakses database sama sekali
            if user_data:
                # Coba cari departemen di berbagai field yang mungkin ada
                department = None
                
                # Opsi 1: Field 'department' langsung
                if 'department' in user_data:
                    department = user_data['department']
                
                # Opsi 2: Field 'dept' 
                elif 'dept' in user_data:
                    department = user_data['dept']
                    
                # Opsi 3: Field 'user_detail' yang berisi department
                elif 'user_detail' in user_data and isinstance(user_data['user_detail'], dict):
                    if 'department' in user_data['user_detail']:
                        department = user_data['user_detail']['department']
                
                # Fallback ke role jika tidak ada department
                if not department:
                    department = session.get_role() or "User"
                
                # Tampilkan departemen (capitalize untuk tampilan yang lebih baik)
                department = department.capitalize()
                self.dept_value.setText(department)
            else:
                # Fallback ke role jika tidak ada data user
                role = session.get_role() or "User"
                self.dept_value.setText(role.capitalize())
                
            # Always check attendance status when user info is updated
            # This is crucial for handling user switching correctly
            QTimer.singleShot(100, self.check_current_attendance_status)
        else:
            self.name_value.setText("Please login first")
            self.dept_value.setText("Not authenticated")
            
            # Emit login required signal if not logged in
            QTimer.singleShot(300, self.login_required.emit)


# Custom PIN input field that handles keyboard events
class PinInputField(QLineEdit):
    """Custom PIN input field that emits signals for key events."""
    
    # Define custom signals
    digitAdded = pyqtSignal(str)  # Signal for when a digit is pressed
    backspacePressed = pyqtSignal()  # Signal for when backspace is pressed
    escapePressed = pyqtSignal()  # Signal for when escape is pressed
    enterPressed = pyqtSignal()  # Signal for when enter is pressed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)  # We'll handle input manually
        self.setEchoMode(QLineEdit.EchoMode.Password)
    
    def keyPressEvent(self, event):
        """Handle key press events in the PIN field."""        
        key = event.key()
        
        # Handle numeric keys (0-9)
        if Qt.Key.Key_0 <= key <= Qt.Key_9:
            self.digitAdded.emit(chr(key))
        # Handle backspace key
        elif key == Qt.Key.Key_Backspace:
            self.backspacePressed.emit()
        # Handle delete key for clearing
        elif key == Qt.Key.Key_Delete:
            self.escapePressed.emit()
        # Handle escape key (for clearing)
        elif key == Qt.Key.Key_Escape:
            self.escapePressed.emit()
        # Handle enter key (for submit)
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Emit signal
            self.enterPressed.emit()
            # Directly click the check button
            if self.parent() and hasattr(self.parent(), 'check_button'):
                self.parent().check_button.click()
        
        # Skip parent implementation (we're handling all input manually)
        event.accept()
