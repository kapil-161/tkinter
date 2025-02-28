"""
DSSAT Viewer - Main entry point (Tkinter version)
"""
import sys
import os
import warnings
import traceback
import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# Import theme
from ui.theme import DSSATTheme

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add constants for window dimensions and positioning
WINDOW_CONFIG = {
    'width': 1200,
    'height': 800,
    'min_width': 800,
    'min_height': 600
}

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Add the project root directory to the Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

def center_window(window):
    """Center a Tkinter window on the screen."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

# Import splash screen function
from splash_screen import show_splash

if __name__ == "__main__":
    try:
        # Create root window for application but don't show it yet
        root = tk.Tk()
        root.withdraw()  # Hide the root window initially
        
        # Apply theme
        theme = DSSATTheme()
        theme.apply(root)
        
        # Show splash screen
        splash = show_splash(root)
        root.update()  # Process events to ensure splash is displayed
        
        # Initialize main application
        try:
            from ui.app import DSSATViewer
            
            # Initialize the application with the root window
            viewer = DSSATViewer(root)
            
            # Configure window
            root.geometry(f"{WINDOW_CONFIG['width']}x{WINDOW_CONFIG['height']}")
            root.minsize(WINDOW_CONFIG['min_width'], WINDOW_CONFIG['min_height'])
            root.title("DSSAT Viewer")
            
            # Center window
            center_window(root)
            
            # Close splash and show main window
            splash.destroy()
            root.deiconify()  # Show the main window
            
            # Start the main loop
            root.mainloop()
            
        except Exception as e:
            splash.destroy()
            logging.error(f"Error during initialization: {e}", exc_info=True)
            messagebox.showerror("Initialization Error", f"Error starting application:\n{str(e)}")
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"Error during startup: {e}", exc_info=True)
        messagebox.showerror("Startup Error", f"Failed to start DSSAT Viewer:\n{str(e)}")
        sys.exit(1)