"""
Splash screen for DSSAT Viewer using Tkinter
"""
import sys
import os
import logging
import tkinter as tk
from tkinter import Canvas, Toplevel, PhotoImage
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 450

# Colors
BACKGROUND_COLOR = "#FFFFFF"  # White
GRID_COLOR = "#E6E6E6"        # Light gray
AXIS_COLOR = "#646464"        # Dark gray
LINE_COLOR = "#FF8C00"        # Orange for simulated data
POINT_COLOR = "#FF8C00"       # Orange for observed data
Y_AXIS_LABEL_COLOR = "#0000FF"  # Blue for y-axis label

# Sample crop growth data (date, simulated value, observed value)
CROP_DATA = [
    ("Mar 24 1991", 1000, 1000),
    ("Apr 7", 1100, 1050),
    ("Apr 21", 1400, 1350),
    ("May 5", 3000, 2900),
    ("May 19", 5000, 4800),
    ("Jun 2", 7500, 6700),
    ("Jun 16", 10000, 7900)
]

class DSSATSplashScreen(Toplevel):
    def __init__(self, parent, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
        """Initialize splash screen with given dimensions"""
        logging.debug(f"Initializing DSSATSplashScreen with width={width} and height={height}")
        
        # Initialize the Toplevel widget
        super().__init__(parent)
        self.width = width
        self.height = height
        
        # Remove window decorations
        self.overrideredirect(True)
        
        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create canvas for drawing
        self.canvas = Canvas(self, width=width, height=height, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Draw all components
        self._draw_background_grid()
        self._draw_axes()
        self._draw_data()
        self._draw_labels()
        self._draw_legend()
        
        logging.debug("DSSATSplashScreen initialized successfully")

    def _draw_background_grid(self):
        """Draw grid lines"""
        # Graph area dimensions
        graph_width = self.width - 80 - 70  # Left and right margins
        graph_height = self.height - 100 - 80  # Top and bottom margins
        
        # Horizontal grid lines (y-axis)
        y_steps = 5  # Number of horizontal grid lines
        for i in range(y_steps + 1):
            y = 100 + (graph_height / y_steps) * i
            self.canvas.create_line(
                80, y, self.width - 70, y,
                fill=GRID_COLOR, width=1
            )
        
        # Vertical grid lines (x-axis)
        for i, (date, _, _) in enumerate(CROP_DATA):
            x_pos = 80 + (graph_width / (len(CROP_DATA) - 1)) * i
            self.canvas.create_line(
                x_pos, 100, x_pos, self.height - 80,
                fill=GRID_COLOR, width=1
            )

    def _draw_axes(self):
        """Draw axes with labels"""
        # Graph area dimensions
        graph_height = self.height - 100 - 80
        
        # X-axis (horizontal)
        self.canvas.create_line(
            80, self.height - 80, 
            self.width - 70, self.height - 80,
            fill=AXIS_COLOR, width=2
        )
        
        # Y-axis (vertical)
        self.canvas.create_line(
            80, 100, 
            80, self.height - 80,
            fill=AXIS_COLOR, width=2
        )
        
        # Y-axis labels (values)
        y_max = 10000
        y_steps = 5
        
        for i in range(y_steps + 1):
            y_value = y_max - (y_max / y_steps) * i
            y_pos = 100 + (graph_height / y_steps) * i
            
            if i == 0:
                label = "10k"
            else:
                label = f"{int(y_value/1000)}k"
                
            self.canvas.create_text(
                80 - 10, y_pos,
                text=label, fill=AXIS_COLOR,
                font=("Arial", 9), anchor="e"
            )
        
        # X-axis labels (dates)
        graph_width = self.width - 80 - 70
        for i, (date, _, _) in enumerate(CROP_DATA):
            x_pos = 80 + (graph_width / (len(CROP_DATA) - 1)) * i
            self.canvas.create_text(
                x_pos, self.height - 80 + 15,
                text=date, fill=AXIS_COLOR,
                font=("Arial", 9), anchor="n"
            )
            
        # Bold "DATE" label centered under x-axis
        self.canvas.create_text(
            self.width / 2, self.height - 40,
            text="DATE", fill=Y_AXIS_LABEL_COLOR,
            font=("Arial", 10, "bold"), anchor="n"
        )

    def _draw_data(self):
        """Draw crop growth data (simulated line and observed points)"""
        graph_width = self.width - 80 - 70
        graph_height = self.height - 100 - 80
        
        y_max = 10000  # Maximum y value
        
        # Prepare points for simulated data (line)
        sim_points = []
        obs_points = []
        
        for i, (_, sim_value, obs_value) in enumerate(CROP_DATA):
            x_pos = 80 + (graph_width / (len(CROP_DATA) - 1)) * i
            sim_y_pos = 100 + graph_height - (sim_value / y_max * graph_height)
            obs_y_pos = 100 + graph_height - (obs_value / y_max * graph_height)
            
            sim_points.append((x_pos, sim_y_pos))
            obs_points.append((x_pos, obs_y_pos))
        
        # Draw simulated data line
        for i in range(1, len(sim_points)):
            self.canvas.create_line(
                sim_points[i-1][0], sim_points[i-1][1],
                sim_points[i][0], sim_points[i][1],
                fill=LINE_COLOR, width=2
            )
        
        # Draw observed data points as squares
        for x, y in obs_points:
            self.canvas.create_rectangle(
                x - 4, y - 4, x + 4, y + 4,
                fill=POINT_COLOR, outline=""
            )

    def _draw_labels(self):
        """Draw title and y-axis label"""
        # Draw title
        self.canvas.create_text(
            self.width / 2, 20,
            text="DSSAT Visualization",
            fill="black", font=("Arial", 14, "bold"),
            anchor="n"
        )
        
        # Draw y-axis label text (rotated)
        self.canvas.create_text(
            25, self.height / 2,
            text="Tops wt kg/ha",
            fill=Y_AXIS_LABEL_COLOR, 
            font=("Arial", 10, "bold"),
            angle=90  # Tkinter supports text rotation
        )
        
        # Draw loading text
        self.canvas.create_text(
            self.width / 2, self.height - 30,
            text="Loading application...",
            fill="black", font=("Arial", 10),
            anchor="s"
        )

    def _draw_legend(self):
        """Draw legend showing simulated and observed data"""
        # Legend background
        legend_x = self.width - 70 - 120
        legend_y = 100 - 40
        legend_width = 110
        legend_height = 40
        
        self.canvas.create_rectangle(
            legend_x, legend_y,
            legend_x + legend_width, legend_y + legend_height,
            outline="#C8C8C8", fill="#FAFAFA"
        )
        
        # Line heights
        line1_y = legend_y + 15
        line2_y = legend_y + 30
        
        # Simulated Data - line
        self.canvas.create_line(
            legend_x + 10, line1_y,
            legend_x + 35, line1_y,
            fill=LINE_COLOR, width=2
        )
        
        # Simulated Data - text
        self.canvas.create_text(
            legend_x + 40, line1_y,
            text="Simulated",
            fill="black", font=("Arial", 9),
            anchor="w"
        )
        
        # Observed Data - point
        self.canvas.create_rectangle(
            legend_x + 21 - 4, line2_y - 4,
            legend_x + 21 + 4, line2_y + 4,
            fill=POINT_COLOR, outline=""
        )
        
        # Observed Data - text
        self.canvas.create_text(
            legend_x + 40, line2_y,
            text="Observed",
            fill="black", font=("Arial", 9),
            anchor="w"
        )

def show_splash(root):
    """Display the splash screen."""
    logging.debug("Displaying splash screen")
    splash = DSSATSplashScreen(root)
    return splash

if __name__ == "__main__":
    # Test the splash screen independently
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    splash = show_splash(root)
    root.update()
    
    # Simulate loading time
    time.sleep(3)
    print("Application loaded")
    
    splash.destroy()
    root.destroy()