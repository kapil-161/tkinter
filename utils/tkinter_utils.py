"""
Tkinter utility functions for DSSAT Viewer
"""
import tkinter as tk
from tkinter import ttk
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union

def configure_treeview_from_dataframe(tree: ttk.Treeview, df: pd.DataFrame, max_width: int = 200, 
                                     limit_rows: int = 1000, max_display_chars: int = 50) -> None:
    """Configure a Treeview widget based on a DataFrame.
    
    Args:
        tree (ttk.Treeview): The Treeview widget to configure
        df (pd.DataFrame): The DataFrame containing the data
        max_width (int, optional): Maximum column width in pixels. Defaults to 200.
        limit_rows (int, optional): Maximum number of rows to display. Defaults to 1000.
        max_display_chars (int, optional): Maximum characters to display per cell. Defaults to 50.
    """
    # Clear existing data
    for item in tree.get_children():
        tree.delete(item)
    
    # Clear existing columns
    tree['columns'] = []
    
    if df is None or df.empty:
        tree['columns'] = ['Message']
        tree['show'] = 'headings'
        tree.heading('Message', text='Message')
        tree.column('Message', width=400)
        tree.insert('', 'end', values=["No data available"])
        return
    
    # Configure columns
    tree['columns'] = list(df.columns)
    tree['show'] = 'headings'  # Hide the first column (ID)
    
    # Set column headings and widths
    for col in df.columns:
        tree.heading(col, text=str(col))
        
        # Calculate column width based on content (first 100 rows for performance)
        sample_df = df.head(100)
        max_content_width = max(
            len(str(col)),
            max([len(str(val)[:max_display_chars]) for val in sample_df[col].dropna()], default=0)
        )
        
        # Set column width (minimum 50, maximum specified by max_width)
        tree.column(col, width=min(max_width, max(50, max_content_width * 8)))
    
    # Add data rows (limit for performance)
    display_data = df.head(limit_rows)
    for i, row in display_data.iterrows():
        # Truncate long values for display
        values = [str(val)[:max_display_chars] for val in row]
        tree.insert('', 'end', text=str(i), values=values)
    
    # Add a message if data was truncated
    if len(df) > limit_rows:
        tree.insert('', 'end', values=["..."] * len(df.columns))
        tree.insert('', 'end', values=[f"Showing {limit_rows} of {len(df)} rows"] + [""] * (len(df.columns) - 1))

def center_window(window: tk.Tk, width: Optional[int] = None, height: Optional[int] = None) -> None:
    """Center a Tkinter window on the screen.
    
    Args:
        window (tk.Tk): The window to center
        width (Optional[int], optional): Window width. If None, uses current width. Defaults to None.
        height (Optional[int], optional): Window height. If None, uses current height. Defaults to None.
    """
    window.update_idletasks()
    
    # Use provided dimensions or current window size
    win_width = width if width is not None else window.winfo_width()
    win_height = height if height is not None else window.winfo_height()
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate position
    x = (screen_width - win_width) // 2
    y = (screen_height - win_height) // 2
    
    # Set window position
    window.geometry(f"{win_width}x{win_height}+{x}+{y}")

def configure_grid_weights(frame: Union[tk.Frame, ttk.Frame], columns: int = 1, rows: int = 1) -> None:
    """Configure grid weights for a frame to make it responsive.
    
    Args:
        frame (Union[tk.Frame, ttk.Frame]): The frame to configure
        columns (int, optional): Number of columns. Defaults to 1.
        rows (int, optional): Number of rows. Defaults to 1.
    """
    for i in range(columns):
        frame.columnconfigure(i, weight=1)
    for i in range(rows):
        frame.rowconfigure(i, weight=1)

def create_scrollable_frame(parent: Union[tk.Frame, ttk.Frame]) -> Tuple[ttk.Frame, ttk.Frame]:
    """Create a scrollable frame.
    
    Args:
        parent (Union[tk.Frame, ttk.Frame]): The parent widget
        
    Returns:
        Tuple[ttk.Frame, ttk.Frame]: Outer frame (with scrollbars) and inner frame (for content)
    """
    # Create outer frame that will contain the scrollbars and canvas
    outer_frame = ttk.Frame(parent)
    
    # Create canvas for scrolling
    canvas = tk.Canvas(outer_frame)
    
    # Create scrollbars
    vscrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
    hscrollbar = ttk.Scrollbar(outer_frame, orient="horizontal", command=canvas.xview)
    
    # Configure canvas
    canvas.configure(yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)
    
    # Create inner frame for content
    inner_frame = ttk.Frame(canvas)
    
    # Function to update canvas scroll region when inner frame size changes
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    # Bind frame configure event
    inner_frame.bind("<Configure>", on_frame_configure)
    
    # Create window in canvas
    canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
    
    # Function to update canvas window width when canvas size changes
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    # Bind canvas configure event
    canvas.bind("<Configure>", on_canvas_configure)
    
    # Grid layout
    canvas.grid(row=0, column=0, sticky="nsew")
    vscrollbar.grid(row=0, column=1, sticky="ns")
    hscrollbar.grid(row=1, column=0, sticky="ew")
    
    # Configure weights
    outer_frame.rowconfigure(0, weight=1)
    outer_frame.columnconfigure(0, weight=1)
    
    return outer_frame, inner_frame

def create_hover_tooltip(widget: tk.Widget, text: str) -> None:
    """Create a tooltip that appears when hovering over a widget.
    
    Args:
        widget (tk.Widget): The widget to add a tooltip to
        text (str): The tooltip text
    """
    tooltip = None
    
    def enter(event):
        nonlocal tooltip
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        # Create a toplevel window
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create label
        label = ttk.Label(tooltip, text=text, justify=tk.LEFT,
                         background="#ffffff", relief=tk.SOLID, borderwidth=1,
                         wraplength=300)
        label.pack(padx=2, pady=2)
    
    def leave(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None
    
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)

def apply_modern_style(root: tk.Tk) -> None:
    """Apply modern styling to Tkinter application.
    
    Args:
        root (tk.Tk): The root window
    """
    # Create custom style
    style = ttk.Style()
    
    # Use clam theme as base (works well on all platforms)
    style.theme_use('clam')
    
    # Configure common elements
    style.configure('TLabel', padding=3)
    style.configure('TButton', padding=6)
    style.configure('TEntry', padding=3)
    
    # Configure frame with border
    style.configure('Card.TFrame', relief='ridge', borderwidth=1)
    
    # Configure heading-style label
    style.configure('Heading.TLabel', font=('TkDefaultFont', 12, 'bold'))
    style.configure('Subheading.TLabel', font=('TkDefaultFont', 10, 'bold'))
    
    # Configure primary button
    style.configure('Accent.TButton', background='#007bff', foreground='white')
    
    # Configure treeview
    style.configure('Treeview', rowheight=25)
    style.configure('Treeview.Heading', font=('TkDefaultFont', 10, 'bold'))