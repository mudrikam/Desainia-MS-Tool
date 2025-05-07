from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QSizePolicy, QSpacerItem, QGridLayout,
    QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont, QColor
import qtawesome as qta
import random  # For generating random percentage changes


class StatBox(QFrame):
    """A rounded box widget to display statistics."""
    
    def __init__(self, title, value, icon_name, color="#4A86E8"):
        super().__init__()
        
        # Set frame properties
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("statBox")
        self.setStyleSheet(f"""
            #statBox {{
                background-color: palette(light);
                border: 1px solid {color};
                border-radius: 15px;
            }}
        """)
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(0)  # Minimal spacing between layouts
        
        # Create header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        
        # Add icon
        icon = qta.icon(icon_name, color=color)
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(16, 16))
        header_layout.addWidget(icon_label)
        
        # Add title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(9)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {color};")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Add value with specific margins
        value_label = QLabel(str(value))
        value_font = QFont()
        value_font.setPointSize(28)
        value_font.setWeight(600)  # Semi-bold
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"""
            color: {color};
            margin-top: 0px;
            margin-bottom: 0px;
            padding-top: 0px;
            padding-bottom: 0px;
        """)
        
        # Add to main layout
        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        
        # Set size policy but no minimum height
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)


class IncomeBox(QFrame):
    """A rounded box widget to display income statistics with system colors."""
    
    def __init__(self, title, value, icon_name):
        super().__init__()
        
        # Set frame properties
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("incomeBox")
        self.setStyleSheet("""
            #incomeBox {
                background-color: palette(light);
                border: none;
                border-radius: 15px;
            }
        """)
        
        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(0)  # Minimal spacing between layouts
        
        # Create header with title only (no icon)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        
        # Add title - left aligned
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(9)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: rgba(127, 127, 127, 1);")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Format the value with IDR instead of Rp
        formatted_value = f"IDR {value:,}".replace(',', '.')
        
        # Add value with specific margins - left aligned
        value_label = QLabel(formatted_value)
        value_font = QFont()
        value_font.setPointSize(12)
        value_font.setWeight(600)  # Semi-bold
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Use green color for "Current Income" text
        value_color = "#4CAF50" if title == "Current Income" else "palette(text)"
        value_label.setStyleSheet(f"""
            color: {value_color};
            margin-top: 0px;
            margin-bottom: 0px;
            padding-top: 0px;
            padding-bottom: 0px;
        """)
        
        # Generate random percentage for demo (between -15% and +15%)
        percentage = random.uniform(-15, 15)
        is_positive = percentage >= 0
        percentage_abs = abs(percentage)
        
        # Create percentage indicator with up/down arrow
        if is_positive:
            arrow_icon = "fa5s.arrow-up"
            color = "#4CAF50"  # Green for positive
            percentage_text = f"↑ {percentage_abs:.1f}%"
        else:
            arrow_icon = "fa5s.arrow-down"
            color = "#F44336"  # Red for negative
            percentage_text = f"↓ {percentage_abs:.1f}%"
            
        percentage_label = QLabel(percentage_text)
        percentage_font = QFont()
        percentage_font.setPointSize(9)
        percentage_label.setFont(percentage_font)
        percentage_label.setStyleSheet(f"color: {color}; margin-top: 2px;")
        percentage_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Add to main layout
        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        layout.addWidget(percentage_label)
        
        # Set size policy but no minimum height
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)


class AttendanceStats(QWidget):
    """A simple widget to display attendance statistics without borders or background."""
    
    def __init__(self, title, value, icon_name, color="#555555"):
        super().__init__()
        
        # Setup layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 1, 5, 1)  # Reduced vertical margins for compactness
        layout.setSpacing(8)
        
        # Add icon
        icon = qta.icon(icon_name, color=color)
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(14, 14))  # Smaller icon
        layout.addWidget(icon_label)
        
        # Add title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(8)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {color};")
        layout.addWidget(title_label)
        
        # Add spacer
        layout.addStretch()
        
        # Add value
        value_label = QLabel(str(value))
        value_font = QFont()
        value_font.setPointSize(10)
        value_font.setWeight(600)  # Semi-bold
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)


class AttendanceRecordsTable(QTableWidget):
    """Table widget to display user attendance records."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set table properties
        self.setShowGrid(False)  # No grid lines
        self.setAlternatingRowColors(False)  # We'll handle this with custom styling
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.verticalHeader().setVisible(False)  # Hide row numbers
        self.setFrameShape(QFrame.Shape.NoFrame)  # No border around table
        
        # Hide the horizontal header
        self.horizontalHeader().setVisible(False)
        
        # Set spacing between rows
        self.verticalHeader().setDefaultSectionSize(40)  # Row height
        self.verticalHeader().setMinimumSectionSize(40)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        
        # Add spacing between rows
        self.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: transparent;
                selection-background-color: transparent;
                outline: none;
            }
            QTableWidget::item {
                border: none;
                padding: 5px;
                margin-bottom: 2px;
            }
            QHeaderView::section {
                background-color: transparent;
                border: none;
                padding: 5px;
                font-weight: bold;
                color: palette(text);
            }
            QTableWidget::item:selected {
                background-color: transparent;
                color: palette(text);
            }
        """)
        
        # Set up columns
        self.setColumnCount(3)
        
        # Set column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)    # Date column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Status column
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Notes column
        self.setColumnWidth(0, 100)  # Set date column width
        self.setColumnWidth(1, 80)   # Set status column width
        
        # Load dummy data
        self._load_dummy_data()
    
    def _load_dummy_data(self):
        """Load dummy attendance data for demonstration."""
        # Status options and colors
        statuses = [
            {"text": "Present", "color": "#4CAF50"},
            {"text": "Absent", "color": "#F44336"},
            {"text": "Sick", "color": "#FF9800"},
            {"text": "Permission", "color": "#2196F3"},
            {"text": "Late", "color": "#FFC107"}
        ]
        
        # Notes options
        notes = [
            "",
            "Work from home",
            "Doctor's appointment",
            "Family event",
            "Traffic jam",
            "System issue"
        ]
        
        # Get current date
        current_date = QDateTime.currentDateTime().date()
        
        # Generate rows (for past 14 days)
        self.setRowCount(14)
        
        for i in range(14):
            # Calculate date (going backward from current date)
            date = current_date.addDays(-i)
            date_str = date.toString("yyyy-MM-dd")
            
            # Skip weekends (just to make it more realistic)
            day_of_week = date.dayOfWeek()
            if day_of_week in [6, 7]:  # Saturday or Sunday
                status_idx = 1 if day_of_week == 6 else 1  # Absent on weekends
                note = "Weekend"
            else:
                # Random status for weekdays (weighted toward "Present")
                weights = [70, 5, 10, 10, 5]  # Present, Absent, Sick, Permission, Late
                status_idx = random.choices(range(len(statuses)), weights=weights, k=1)[0]
                
                # Random note (more likely to be empty)
                note = random.choice([notes[0]] * 5 + notes[1:])
            
            # Create custom widgets for each cell to make rounded rows
            # Create row container widget
            row_widget = QWidget()
            row_widget.setObjectName(f"row_{i}")
            row_widget.setStyleSheet(f"""
                #row_{i} {{
                    background-color: palette(light);
                    border-radius: 10px;
                }}
            """)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(10, 5, 10, 5)
            row_layout.setSpacing(10)
            
            # Date label
            date_label = QLabel(date_str)
            
            # Status label with color
            status = statuses[status_idx]
            status_label = QLabel(status["text"])
            status_label.setStyleSheet(f"color: {status['color']}; font-weight: 600;")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Note label
            note_label = QLabel(note)
            note_label.setStyleSheet("color: palette(text);")
            
            # Add labels to row layout
            row_layout.addWidget(date_label, 1)
            row_layout.addWidget(status_label, 1)
            row_layout.addWidget(note_label, 3)
            
            # Add row widget to table
            self.setCellWidget(i, 0, row_widget)
            
            # Hide other cells (we're using a single widget spanning all columns)
            self.setSpan(i, 0, 1, 3)
            
        # Set row heights with spacing
        for row in range(self.rowCount()):
            self.setRowHeight(row, 40)


class UserDashboardWidget(QWidget):
    """Widget for the dashboard tab in the user dashboard."""
    
    def __init__(self, parent=None, username="User", app=None):
        super().__init__(parent)
        self.username = username
        self.app = app
        
        # Initialize UI
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface for the dashboard."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget to hold all dashboard elements
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Add stats boxes in a horizontal layout
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Create stat boxes with dummy data
        ongoing_box = StatBox("Ongoing", 12, "fa5s.clock", "#4A86E8")
        remaining_box = StatBox("Remaining", 48, "fa5s.tasks", "#FF9900")
        finished_box = StatBox("Finished", 36, "fa5s.check-circle", "#009E60")
        
        # Add stat boxes to layout
        stats_layout.addWidget(ongoing_box)
        stats_layout.addWidget(remaining_box)
        stats_layout.addWidget(finished_box)
        
        # Add income boxes in a horizontal layout
        income_layout = QHBoxLayout()
        income_layout.setSpacing(15)
        
        # Create income boxes with dummy data
        current_income = IncomeBox("Current Income", 12500000, "fa5s.money-bill-wave")
        monthly_average = IncomeBox("Monthly Average", 150000000, "fa5s.chart-line")
        total_to_date = IncomeBox("Total to Date", 3500000, "fa5s.calculator")
        deductions = IncomeBox("Deductions", 2150000, "fa5s.hand-holding-usd")
        
        # Add income boxes to layout
        income_layout.addWidget(current_income)
        income_layout.addWidget(monthly_average)
        income_layout.addWidget(total_to_date)
        income_layout.addWidget(deductions)
        
        # Create a two-column layout for the bottom section
        two_column_layout = QHBoxLayout()
        two_column_layout.setSpacing(20)
        
        # Left column (main content area)
        left_column = QFrame()
        left_column.setFrameShape(QFrame.Shape.StyledPanel)
        left_column.setObjectName("recordsPanel")
        left_column.setStyleSheet("""
            #recordsPanel {
                background-color: palette(light);
                border-radius: 10px;
            }
        """)
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(10, 10, 10, 10)  # Match the right column's 10px padding
        
        # Add attendance records section to left column
        attendance_header_layout = QHBoxLayout()
        
        # Attendance Records title (left-aligned)
        attendance_records_title = QLabel("Attendance Records")
        attendance_records_title_font = QFont()
        attendance_records_title_font.setPointSize(10)
        attendance_records_title_font.setWeight(600)
        attendance_records_title.setFont(attendance_records_title_font)
        attendance_records_title.setContentsMargins(5, 0, 0, 5)
        attendance_header_layout.addWidget(attendance_records_title)
        
        # Add current month/year (right-aligned)
        current_date = QDateTime.currentDateTime().date()
        month_year = current_date.toString("MMMM/yyyy")  # Format as "May/2025"
        
        month_year_label = QLabel(month_year)
        month_year_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        month_year_label.setStyleSheet("color: palette(text);")
        month_year_font = QFont()
        month_year_font.setPointSize(9)
        month_year_label.setFont(month_year_font)
        attendance_header_layout.addWidget(month_year_label)
        
        # Add header layout to left column
        left_layout.addLayout(attendance_header_layout)
        
        # Create attendance records table
        attendance_records_table = AttendanceRecordsTable()
        
        # Add to left layout
        left_layout.addWidget(attendance_records_table, 1)  # Give table a stretch factor
        
        # Right column (attendance - smaller width)
        right_column = QFrame()
        right_column.setFrameShape(QFrame.Shape.StyledPanel)
        right_column.setObjectName("attendancePanel")
        right_column.setStyleSheet("""
            #attendancePanel {
                background-color: palette(light);
                border-radius: 10px;
            }
        """)
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(5)  # Reduce spacing for compactness
        
        # Create attendance section title
        attendance_title = QLabel("Attendance")
        attendance_title_font = QFont()
        attendance_title_font.setPointSize(10)
        attendance_title_font.setWeight(600)
        attendance_title.setFont(attendance_title_font)
        
        # Add attendance title to right column
        right_layout.addWidget(attendance_title)
        
        # Create attendance stats with dummy data and icons
        present_stats = AttendanceStats("Present", 87, "fa5s.user-check", "#4CAF50")
        absent_stats = AttendanceStats("Absent", 5, "fa5s.user-times", "#F44336")
        sick_stats = AttendanceStats("Sick", 3, "fa5s.procedures", "#FF9800")
        permission_stats = AttendanceStats("Permission", 2, "fa5s.clipboard-check", "#2196F3")
        
        # Use theme-friendly colors for the bottom stats using palette colors
        total_workdays_stats = AttendanceStats("Total Workdays", 100, "fa5s.calendar-alt", "palette(text)")
        avg_hours_stats = AttendanceStats("Avg Hours/Day", 7.5, "fa5s.clock", "palette(text)")
        total_hours_stats = AttendanceStats("Total Hours", 750, "fa5s.hourglass-half", "palette(text)")
        
        # Add attendance stats directly to right layout
        right_layout.addWidget(present_stats)
        right_layout.addWidget(absent_stats)
        right_layout.addWidget(sick_stats)
        right_layout.addWidget(permission_stats)
        right_layout.addWidget(total_workdays_stats)
        right_layout.addWidget(avg_hours_stats)
        right_layout.addWidget(total_hours_stats)
        
        # Add stretch to push everything to the top
        right_layout.addStretch()
        
        # Add columns to two-column layout with adjusted ratios (right column smaller)
        two_column_layout.addWidget(left_column, 4)  # 80% width
        two_column_layout.addWidget(right_column, 1)  # 20% width
        
        # Add layouts to content layout
        content_layout.addLayout(stats_layout)
        content_layout.addLayout(income_layout)
        content_layout.addLayout(two_column_layout, 1)  # Give it a stretch factor
        
        # Add spacer to push content to the top
        content_layout.addStretch()
        
        # Set the content widget as the scroll area's widget
        scroll_area.setWidget(content_widget)
        
        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)
    
    def refresh_data(self):
        """Refresh the dashboard data."""
        # In a real implementation, this would update the numbers from a database
        pass
    
    def update_username(self, username):
        """Update the displayed username.""" 
        self.username = username