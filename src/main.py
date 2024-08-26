import sys
import math
from queue import PriorityQueue
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QColorDialog, QLabel, QSpinBox, QStyle, QStyleOption, QDialog,
                             QSlider)
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt5.QtCore import Qt, QTimer, QRectF

class Node:
    def __init__(self, position, g=0, h=0):
        self.position = position
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

class ColorScheme:
    def __init__(self):
        self.background = QColor(0, 0, 0)
        self.grid_lines = QColor(40, 40, 40)
        self.start = QColor(0, 255, 0)
        self.goal = QColor(255, 0, 0)
        self.obstacle = QColor(128, 128, 128)
        self.open_set = QColor(0, 255, 255)
        self.closed_set = QColor(255, 165, 0)
        self.path = QColor(255, 255, 0)
        self.to_node = QColor(255, 0, 255)

class StylizedWidget(QWidget):
    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

class GridWidget(StylizedWidget):
    def __init__(self, rows, cols, cell_size, color_scheme):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.color_scheme = color_scheme
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.start = None
        self.goal = None
        self.to_nodes = []
        self.path = []
        self.open_set = PriorityQueue()
        self.closed_set = set()
        self.open_set_positions = set()
        self.current_node = None
        self.f_values = {}
        self.g_values = {}
        self.h_values = {}

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), self.color_scheme.background)

        # Draw grid
        painter.setPen(QPen(self.color_scheme.grid_lines, 1))
        for row in range(self.rows + 1):
            painter.drawLine(0, row * self.cell_size, self.cols * self.cell_size, row * self.cell_size)
        for col in range(self.cols + 1):
            painter.drawLine(col * self.cell_size, 0, col * self.cell_size, self.rows * self.cell_size)

        # Draw cells
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.cell_size
                y = row * self.cell_size
                if self.grid[row][col] == 1:
                    painter.fillRect(x, y, self.cell_size, self.cell_size, self.color_scheme.obstacle)
                elif (row, col) in self.closed_set:
                    painter.fillRect(x, y, self.cell_size, self.cell_size, self.color_scheme.closed_set)
                elif any(node[1].position == (row, col) for node in self.open_set.queue):
                    painter.fillRect(x, y, self.cell_size, self.cell_size, self.color_scheme.open_set)

        # Draw path
        if self.path:
            painter.setPen(QPen(self.color_scheme.path, 3))
            for i in range(len(self.path) - 1):
                start = self.path[i]
                end = self.path[i + 1]
                painter.drawLine(
                    start[1] * self.cell_size + self.cell_size // 2,
                    start[0] * self.cell_size + self.cell_size // 2,
                    end[1] * self.cell_size + self.cell_size // 2,
                    end[0] * self.cell_size + self.cell_size // 2
                )

        # Draw special nodes
        if self.start:
            self.draw_special_node(painter, self.start, self.color_scheme.start)
        if self.goal:
            self.draw_special_node(painter, self.goal, self.color_scheme.goal)
        for to_node in self.to_nodes:
            self.draw_special_node(painter, to_node, self.color_scheme.to_node)

        # Draw f, g, and h values
        painter.setFont(QFont('Arial', 8))
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.cell_size
                y = row * self.cell_size
                if (row, col) in self.f_values:
                    painter.setPen(QPen(Qt.white))
                    painter.drawText(QRectF(x, y, self.cell_size, self.cell_size / 3), 
                                     Qt.AlignCenter, f"f:{self.f_values[(row, col)]:.1f}")
                    painter.drawText(QRectF(x, y + self.cell_size / 3, self.cell_size / 2, self.cell_size / 3), 
                                     Qt.AlignCenter, f"g:{self.g_values[(row, col)]:.1f}")
                    painter.drawText(QRectF(x + self.cell_size / 2, y + self.cell_size / 3, self.cell_size / 2, self.cell_size / 3), 
                                     Qt.AlignCenter, f"h:{self.h_values[(row, col)]:.1f}")

    def draw_special_node(self, painter, position, color):
        x, y = position
        center_x = (y + 0.5) * self.cell_size
        center_y = (x + 0.5) * self.cell_size
        radius = self.cell_size * 0.4

        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2))

    def mousePressEvent(self, event):
        self.handle_mouse_event(event)

    def mouseMoveEvent(self, event):
        self.handle_mouse_event(event)

    def handle_mouse_event(self, event):
        col = event.x() // self.cell_size
        row = event.y() // self.cell_size
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if event.buttons() & Qt.LeftButton:
                self.grid[row][col] = 1
            elif event.buttons() & Qt.RightButton:
                self.grid[row][col] = 0
            self.update()

class StylizedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FF7F50;
                color: black;
                border: none;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #FF6347;
            }
            QPushButton:pressed {
                background-color: #FF4500;
            }
        """)

class ColorSettingsDialog(QDialog):
    def __init__(self, color_scheme, parent=None):
        super().__init__(parent)
        self.color_scheme = color_scheme
        self.setWindowTitle("Color Settings")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout()
        self.setLayout(layout)

        color_attrs = [attr for attr in dir(self.color_scheme) if not attr.startswith("__") and isinstance(getattr(self.color_scheme, attr), QColor)]

        for row, attr in enumerate(color_attrs):
            label = QLabel(attr.replace("_", " ").title())
            button = QPushButton()
            button.setStyleSheet(f"background-color: {getattr(self.color_scheme, attr).name()}")
            button.clicked.connect(lambda checked, a=attr: self.change_color(a))

            layout.addWidget(label, row, 0)
            layout.addWidget(button, row, 1)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        layout.addWidget(save_button, len(color_attrs), 0, 1, 2)

    def change_color(self, attr):
        color = QColorDialog.getColor(getattr(self.color_scheme, attr), self)
        if color.isValid():
            setattr(self.color_scheme, attr, color)
            self.sender().setStyleSheet(f"background-color: {color.name()}")

class AStarVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A* Pathfinding Visualization")
        self.setGeometry(100, 100, 1000, 700)
        self.color_scheme = ColorScheme()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QHBoxLayout()
        main_widget.setLayout(layout)

        self.grid_widget = GridWidget(35, 50, 15, self.color_scheme)
        layout.addWidget(self.grid_widget, 4)

        button_layout = QVBoxLayout()
        layout.addLayout(button_layout, 1)

        self.start_button = StylizedButton("Set Start")
        self.goal_button = StylizedButton("Set Goal")
        self.to_node_button = StylizedButton("Add To-Node")
        self.visualize_button = StylizedButton("Visualize")
        self.reset_button = StylizedButton("Reset")
        self.settings_button = StylizedButton("Settings")

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.goal_button)
        button_layout.addWidget(self.to_node_button)
        button_layout.addWidget(self.visualize_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.settings_button)

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(50)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(self.update_speed)

        button_layout.addWidget(QLabel("Visualization Speed"))
        button_layout.addWidget(self.speed_slider)
        
        button_layout.addStretch(1)

        self.start_button.clicked.connect(self.set_start)
        self.goal_button.clicked.connect(self.set_goal)
        self.to_node_button.clicked.connect(self.add_to_node)
        self.visualize_button.clicked.connect(self.visualize)
        self.reset_button.clicked.connect(self.reset)
        self.settings_button.clicked.connect(self.open_settings)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.astar_step)

        self.setStyleSheet("""
            QMainWindow {
                background-color: black;
            }
            QLabel {
                color: #FF7F50;
            }
        """)

    def set_start(self):
        self.grid_widget.start = None
        self.grid_widget.setCursor(Qt.CrossCursor)
        self.grid_widget.mousePressEvent = self.set_start_pos

    def set_start_pos(self, event):
        col = event.x() // self.grid_widget.cell_size
        row = event.y() // self.grid_widget.cell_size
        if 0 <= row < self.grid_widget.rows and 0 <= col < self.grid_widget.cols:
            self.grid_widget.start = (row, col)
            self.grid_widget.setCursor(Qt.ArrowCursor)
            self.grid_widget.mousePressEvent = self.grid_widget.mousePressEvent
            self.grid_widget.update()

    def set_goal(self):
        self.grid_widget.goal = None
        self.grid_widget.setCursor(Qt.CrossCursor)
        self.grid_widget.mousePressEvent = self.set_goal_pos

    def set_goal_pos(self, event):
        col = event.x() // self.grid_widget.cell_size
        row = event.y() // self.grid_widget.cell_size
        if 0 <= row < self.grid_widget.rows and 0 <= col < self.grid_widget.cols:
            self.grid_widget.goal = (row, col)
            self.grid_widget.setCursor(Qt.ArrowCursor)
            self.grid_widget.mousePressEvent = self.grid_widget.mousePressEvent
            self.grid_widget.update()

    def add_to_node(self):
        if len(self.grid_widget.to_nodes) < 3:
            self.grid_widget.setCursor(Qt.CrossCursor)
            self.grid_widget.mousePressEvent = self.set_to_node_pos
        else:
            print("Maximum number of to-nodes (3) reached")

    def set_to_node_pos(self, event):
        col = event.x() // self.grid_widget.cell_size
        row = event.y() // self.grid_widget.cell_size
        if 0 <= row < self.grid_widget.rows and 0 <= col < self.grid_widget.cols:
            self.grid_widget.to_nodes.append((row, col))
            self.grid_widget.setCursor(Qt.ArrowCursor)
            self.grid_widget.mousePressEvent = self.grid_widget.mousePressEvent
            self.grid_widget.update()
                          
    def visualize(self):
        if not self.grid_widget.start or not self.grid_widget.goal:
            print("Please set both start and goal positions before visualizing.")
            return

        self.grid_widget.open_set = PriorityQueue()
        start_node = Node(self.grid_widget.start, h=self.heuristic(self.grid_widget.start, self.grid_widget.goal))
        start_node.parent = None  # Explicitly set parent to None
        self.grid_widget.open_set.put((start_node.f, start_node))
        self.grid_widget.closed_set = set()
        self.grid_widget.path = []
        self.grid_widget.f_values = {}
        self.grid_widget.g_values = {}
        self.grid_widget.h_values = {}
        self.current_target = 0
        self.update_speed()
        self.timer.start()

    def reset(self):
        self.grid_widget.grid = [[0 for _ in range(self.grid_widget.cols)] for _ in range(self.grid_widget.rows)]
        self.grid_widget.start = None
        self.grid_widget.goal = None
        self.grid_widget.to_nodes = []
        self.grid_widget.path = []
        self.grid_widget.open_set = PriorityQueue()
        self.grid_widget.closed_set.clear()
        self.grid_widget.f_values.clear()
        self.grid_widget.g_values.clear()
        self.grid_widget.h_values.clear()
        self.grid_widget.update()
        self.timer.stop()

    def open_settings(self):
        dialog = ColorSettingsDialog(self.color_scheme, self)
        if dialog.exec_():
            self.grid_widget.update()

    def update_speed(self):
        self.timer.setInterval(1000 // self.speed_slider.value())

    def heuristic(self, a, b):
        return max(abs(b[0] - a[0]), abs(b[1] - a[1]))  # Chebyshev distance

    def get_neighbors(self, node):
        x, y = node.position
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_widget.rows and 0 <= ny < self.grid_widget.cols:
                if self.grid_widget.grid[nx][ny] == 0:
                    cost = 1 if dx == 0 or dy == 0 else 1.414  # Diagonal movement costs more
                    neighbors.append(Node((nx, ny), g=node.g + cost))
        return neighbors

    def reconstruct_path(self, current):
        path = []
        while current:
            path.append(current.position)
            current = current.parent
        return path[::-1]  # Reverse the path to get start to end

    def astar_step(self):
        if self.grid_widget.open_set.empty():
            self.timer.stop()
            return

        current = self.grid_widget.open_set.get()[1]
        self.grid_widget.closed_set.add(current.position)

        targets = self.grid_widget.to_nodes + [self.grid_widget.goal]
        current_target = targets[self.current_target]

        if current.position == current_target:
            partial_path = self.reconstruct_path(current)
            self.grid_widget.path.extend(partial_path)
            
            self.current_target += 1
            if self.current_target >= len(targets):
                self.timer.stop()
                self.grid_widget.update()
                return
            
            self.grid_widget.open_set = PriorityQueue()
            start_node = Node(current.position, h=self.heuristic(current.position, targets[self.current_target]))
            start_node.parent = None  # Explicitly set parent to None
            self.grid_widget.open_set.put((start_node.f, start_node))
            self.grid_widget.closed_set.clear()
            return

        for neighbor in self.get_neighbors(current):
            if neighbor.position in self.grid_widget.closed_set:
                continue

            tentative_g = neighbor.g  # Use the cost calculated in get_neighbors

            if neighbor.position not in self.grid_widget.open_set_positions:
                neighbor.g = tentative_g
                neighbor.h = self.heuristic(neighbor.position, current_target)
                neighbor.f = neighbor.g + neighbor.h
                neighbor.parent = current
                self.grid_widget.open_set.put((neighbor.f, neighbor))
                self.grid_widget.open_set_positions.add(neighbor.position)
                
                # Update f, g, h values for visualization
                self.grid_widget.f_values[neighbor.position] = neighbor.f
                self.grid_widget.g_values[neighbor.position] = neighbor.g
                self.grid_widget.h_values[neighbor.position] = neighbor.h
            else:
                # Find the existing neighbor in the open set
                existing_neighbor = next((node for node in self.grid_widget.open_set.queue if node[1].position == neighbor.position), None)
                if existing_neighbor and tentative_g < existing_neighbor[1].g:
                    self.grid_widget.open_set.queue.remove(existing_neighbor)
                    self.grid_widget.open_set_positions.remove(existing_neighbor[1].position)
                    existing_neighbor[1].g = tentative_g
                    existing_neighbor[1].f = tentative_g + existing_neighbor[1].h
                    existing_neighbor[1].parent = current
                    self.grid_widget.open_set.put(existing_neighbor)
                    self.grid_widget.open_set_positions.add(existing_neighbor[1].position)
                    
                    # Update f, g values for visualization
                    self.grid_widget.f_values[existing_neighbor[1].position] = existing_neighbor[1].f
                    self.grid_widget.g_values[existing_neighbor[1].position] = existing_neighbor[1].g

        self.grid_widget.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AStarVisualizer()
    window.show()
    sys.exit(app.exec_())