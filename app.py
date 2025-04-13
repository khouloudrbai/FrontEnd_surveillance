import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFileDialog, QListWidget,
    QStackedWidget, QScrollArea, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Interface App")
        self.resize(800, 600)
        self.setStyleSheet("""
    QWidget {
        color: black;
        background: lightgray;
    }
    QHBoxLayout{
          color: black;
        background: white;
    }  
    QScrollArea{color: black;
        background: white;}
    QListWidget   {color: black;
        background: white;}
    QStackedWidget{color: black;
        background: white;}
    QLabel{color: black;
       }    
    QPushButton{color: black;
        background: white;
    }                                                                               
""")
      
        # Main Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Sidebar Container (Navigation + Logo)
        sidebar_container = QWidget()
        sidebar_container.setFixedWidth(180)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar_container.setLayout(sidebar_layout)

        # Logo at the top
        logo_label = QLabel()
        try:
            logo_pixmap = QPixmap("logo.png") 
            if logo_pixmap.isNull():
                raise Exception("Logo image not found or invalid")
            logo_label.setPixmap(logo_pixmap.scaled(150, 50, Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Create a placeholder if logo fails to load
            from PyQt6.QtGui import QPainter, QColor
            placeholder = QPixmap(150, 50)
            placeholder.fill(Qt.GlobalColor.white)
            painter = QPainter(placeholder)
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(placeholder.rect(), Qt.AlignmentFlag.AlignCenter, "APP LOGO")
            painter.end()
            logo_label.setPixmap(placeholder)
            
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("background: white; padding: 10px;")
        sidebar_layout.addWidget(logo_label)

        # Navigation List
        self.sidebar = QListWidget()
        self.sidebar.addItems(["File Processor", "Settings", "About"])
        self.sidebar.currentRowChanged.connect(self.switch_interface)
        
        # Add styling to the sidebar
        self.sidebar.setStyleSheet("""
            QListWidget {
                border: none;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
            QListWidget::item:selected {
                background: #0078d7;
                color: white;
            }
        """)
        
        sidebar_layout.addWidget(self.sidebar)
        
        # Add the sidebar container to main layout
        main_layout.addWidget(sidebar_container)

        # Stacked Widget (Multiple Interfaces)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Interface 1: File Processor
        self.create_file_processor_interface()

        # Interface 2: Settings (Placeholder)
        settings_tab = QLabel("Settings Panel")
        settings_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stacked_widget.addWidget(settings_tab)

        # Interface 3: About (Placeholder)
        about_tab = QLabel("About Panel")
        about_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stacked_widget.addWidget(about_tab)

    def create_file_processor_interface(self):
        """First interface with file input/output"""
        self.file_tab = QWidget()
        layout = QVBoxLayout()
        self.file_tab.setLayout(layout)

        # File Input Section
        file_group = QWidget()
        file_layout = QHBoxLayout()
        file_group.setLayout(file_layout)

        self.file_label = QLabel("No file selected")
        file_btn = QPushButton("Browse File")
        file_btn.clicked.connect(self.open_file_dialog)

        file_layout.addWidget(self.file_label)
        file_layout.addWidget(file_btn)

        # Output Display Area (will contain either text or table)
        self.output_area = QScrollArea()
        self.output_area.setWidgetResizable(True)
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_area.setWidget(self.output_display)

        # Process Button
        process_btn = QPushButton("Process File")
        process_btn.clicked.connect(self.process_file)

        layout.addWidget(file_group)
        layout.addWidget(self.output_area)
        layout.addWidget(process_btn)

        self.stacked_widget.addWidget(self.file_tab)

    def open_file_dialog(self):
        """Open file dialog and display Excel contents as table"""
        file, _ = QFileDialog.getOpenFileName(
            self, "Open Excel File", "", "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if file:
            self.file_label.setText(file)
            try:
                # Read Excel file
                df = pd.read_excel(file)
                
                # Create table widget
                table = QTableWidget()
                table.setRowCount(df.shape[0])
                table.setColumnCount(df.shape[1])
                
                # Set headers
                table.setHorizontalHeaderLabels(df.columns.astype(str))
                
                # Populate data
                for row in range(df.shape[0]):
                    for col in range(df.shape[1]):
                        item = QTableWidgetItem(str(df.iat[row, col]))
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        table.setItem(row, col, item)
                
                # Resize columns to content
                table.resizeColumnsToContents()
                
                # Clear and display table
                self.output_area.takeWidget()
                self.output_area.setWidget(table)
                self.output_display = table
                
                # Show success message
                self.statusBar().showMessage(f"Loaded {file} - {df.shape[0]} rows × {df.shape[1]} columns", 5000)
                
            except Exception as e:
                # Fallback to text display if error occurs
                self.output_display = QTextEdit()
                self.output_display.setReadOnly(True)
                self.output_area.setWidget(self.output_display)
                self.output_display.append(f"Error reading {file}:\n{str(e)}")
                self.statusBar().showMessage(f"Error loading file", 5000)

    def process_file(self):
        """Read and display Excel file contents"""
        filepath = self.file_label.text()
        
        if filepath == "No file selected":
            self.output_display.append("Please select a file first!")
            return
            
        if not filepath.lower().endswith(('.xlsx', '.xls')):
            self.output_display.append("Please select an Excel file (.xlsx, .xls)")
            return

        try:
            # Read Excel file
            df = pd.read_excel(filepath)
            
            # Create table widget
            table = QTableWidget()
            table.setRowCount(df.shape[0])
            table.setColumnCount(df.shape[1])
            
            # Set headers
            table.setHorizontalHeaderLabels(df.columns.astype(str))
            
            # Populate data
            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    item = QTableWidgetItem(str(df.iat[row, col]))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make non-editable
                    table.setItem(row, col, item)
            
            # Resize columns to content
            table.resizeColumnsToContents()
            
            # Replace current output with table
            self.output_area.takeWidget()  # Remove previous widget
            self.output_area.setWidget(table)
            self.output_display = table  # Keep reference
            
            # Add status message
            self.statusBar().showMessage(f"Loaded {df.shape[0]} rows, {df.shape[1]} columns", 3000)
            
        except Exception as e:
            self.output_display = QTextEdit()
            self.output_display.setReadOnly(True)
            self.output_area.setWidget(self.output_display)
            self.output_display.append(f"Error reading file: {str(e)}")

    def switch_interface(self, index):
        """Change between interfaces"""
        self.stacked_widget.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())