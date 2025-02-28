"""
DSSAT Viewer Application (Tkinter Version)
"""
import sys
import os
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import time

# Import theme
from ui.theme import DSSATTheme

# Add project root to Python path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_dir)

# Import necessary modules
from utils.dssat_paths import initialize_dssat_paths
import config
from ui.layouts import create_app_layout
from ui.callbacks import DSSATCallbacks

# Configure logging
logger = logging.getLogger(__name__)

class DSSATViewer:
    """Main DSSAT visualization application.
    
    A Tkinter-based application for visualizing DSSAT simulation results.
    
    Attributes:
        root (tk.Tk): The main Tkinter window
        frames (dict): Dictionary of frames for different application sections
        widgets (dict): Dictionary of UI widgets for callbacks to access
        callbacks (DSSATCallbacks): Callbacks handler for UI interactions
    """
    
    def __init__(self, root):
        """Initialize the DSSAT Viewer application.
        
        Args:
            root (tk.Tk): The main Tkinter window
        """
        try:
            self.root = root
            
            # Initialize DSSAT paths
            initialize_dssat_paths()
            
            # Create frames dictionary to store different parts of the UI
            self.frames = {}
            
            # Dictionary to hold references to widgets
            self.widgets = {}
            
            # Initialize theme
            self.theme = DSSATTheme()
            
            # Setup UI
            self.setup_ui()
            
            # Setup callbacks
            self.callbacks = DSSATCallbacks(self)
            
            # Register window close handler
            self.root.protocol("WM_DELETE_WINDOW", self.handle_close)
            
            logger.info("DSSATViewer initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing DSSATViewer: {e}", exc_info=True)
            messagebox.showerror("Initialization Error", f"Error initializing application:\n{str(e)}")
            raise

    def setup_ui(self):
        """Create and configure the application UI."""
        try:
            # Set minimum window size
            self.root.minsize(800, 600)
            
            # Setup the main UI components
            create_app_layout(self)
            
            # Configure main window grid layout
            self.root.columnconfigure(0, weight=0, minsize=200)  # Sidebar - fixed width
            self.root.columnconfigure(1, weight=1, minsize=400)  # Content - expandable
            
            self.root.rowconfigure(0, weight=0, minsize=40)   # Toolbar - fixed height
            self.root.rowconfigure(1, weight=1, minsize=300)  # Main content - expandable
            self.root.rowconfigure(2, weight=0, minsize=25)   # Status bar - fixed height
            
            # Configure status bar if it exists
            if 'status_bar' in self.widgets:
                self.widgets['status_bar'].configure(
                    relief=tk.SUNKEN,
                    padding=(5, 2)
                )
            
            # Make UI responsive
            self.setup_window_resize_handlers()
            
            logger.info("UI setup completed successfully - Window size: %dx%d", 
                       self.root.winfo_width(), 
                       self.root.winfo_height())
            
        except Exception as e:
            logger.error(f"Error setting up UI: {e}", exc_info=True)
            raise

    def setup_window_resize_handlers(self):
        """Configure handlers for window resizing."""
        def on_window_resize(event):
            # Update all plot canvases based on window size
            for canvas_type in ['time_series_canvas', 'scatter_canvas']:
                if canvas_type in self.widgets:
                    # Use after() to prevent rapid multiple resizes
                    self.root.after(100, lambda ct=canvas_type: self.update_plot_canvas_size(ct))
        
        # Bind to Configure event
        self.root.bind("<Configure>", on_window_resize)

    def update_plot_canvas_size(self, canvas_type):
        """Update the plot canvas size based on available space.
        
        Args:
            canvas_type (str): Type of canvas to update ('time_series_canvas' or 'scatter_canvas')
        """
        frame_type = canvas_type.replace('canvas', 'frame')
        fig_type = canvas_type.replace('canvas', 'fig')
        
        if frame_type in self.frames and canvas_type in self.widgets:
            # Get the frame's current size
            frame_width = self.frames[frame_type].winfo_width()
            frame_height = self.frames[frame_type].winfo_height()
            
            # Update figure size if frame is large enough
            if frame_width > 100 and frame_height > 100:
                figure = self.widgets[fig_type]
                
                # Calculate new size in inches (DPI-aware)
                dpi = figure.get_dpi()
                width_inches = (frame_width - 40) / dpi  # Account for padding
                height_inches = (frame_height - 40) / dpi
                
                # Update figure size and redraw
                figure.set_size_inches(width_inches, height_inches)
                self.widgets[canvas_type].draw_idle()

    def show_message(self, message_type, message):
        """Show a message to the user.
        
        Args:
            message_type (str): Type of message ('info', 'warning', 'error', or 'success')
            message (str): Message to display
        """
        if message_type == 'info':
            messagebox.showinfo("Information", message)
        elif message_type == 'warning':
            messagebox.showwarning("Warning", message)
        elif message_type == 'error':
            messagebox.showerror("Error", message)
        elif message_type == 'success':
            # Create custom success dialog or use info dialog
            messagebox.showinfo("Success", message)

    def run_long_task(self, task_func, progress_var=None, success_callback=None, error_callback=None):
        """Run a long task in a separate thread.
        
        Args:
            task_func (callable): Function to run in the thread
            progress_var (tk.StringVar, optional): Variable to update with progress
            success_callback (callable, optional): Function to call on success
            error_callback (callable, optional): Function to call on error
        """
        def thread_function():
            try:
                # Run the task
                result = task_func()
                
                # Call success callback in the main thread
                if success_callback:
                    self.root.after(0, lambda: success_callback(result))
                    
            except Exception as e:
                logger.error(f"Error in task: {e}", exc_info=True)
                
                # Call error callback in the main thread
                if error_callback:
                    self.root.after(0, lambda: error_callback(str(e)))
                else:
                    self.root.after(0, lambda: self.show_message("error", f"Error: {str(e)}"))
        
        # Create and start the thread
        task_thread = threading.Thread(target=thread_function)
        task_thread.daemon = True
        task_thread.start()

    def handle_close(self):
        """Handle application close event."""
        try:
            logger.info("Shutting down application...")
            self.root.destroy()
            logger.info("Application shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)
            sys.exit(1)