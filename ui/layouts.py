"""
UI Layouts for DSSAT Viewer (Tkinter Version) with dynamic section sizing
"""
import tkinter as tk
from tkinter import ttk, scrolledtext as ScrolledText
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # Set the backend before importing pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

def create_content_layout(app, parent):
    """Create the main content area with notebook."""
    # Configure content area
    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=1)
    
    # Create notebook for tabs
    notebook = ttk.Notebook(parent)
    notebook.grid(row=0, column=0, sticky="nsew")
    
    # Create Time Series tab with improved layout
    time_series_frame = ttk.Frame(notebook, padding=(10, 10, 10, 20))  # Extra bottom padding for X-axis labels
    notebook.add(time_series_frame, text="Time Series")
    
    # Configure time series frame for proper expansion
    time_series_frame.columnconfigure(0, weight=1)
    time_series_frame.rowconfigure(0, weight=1)
    time_series_frame.rowconfigure(1, weight=0)  # Toolbar row
    
    # Create matplotlib figure with dynamic sizing
    time_series_fig = Figure(figsize=(8, 6), dpi=100)
    # Add more bottom margin for x-axis labels
    time_series_fig.subplots_adjust(bottom=0.15, right=0.85)  # Make room for scaling factor on right
    time_series_canvas = FigureCanvasTkAgg(time_series_fig, master=time_series_frame)
    time_series_canvas.draw()
    time_series_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
    
    # Configure Scatter Plot tab similarly
    scatter_frame = ttk.Frame(notebook, padding=(10, 10, 10, 20))  # Extra bottom padding
    notebook.add(scatter_frame, text="Scatter Plot")
    
    scatter_frame.columnconfigure(0, weight=1)
    scatter_frame.rowconfigure(0, weight=1)
    scatter_frame.rowconfigure(1, weight=0)  # Toolbar row
    
    scatter_fig = Figure(figsize=(8, 6), dpi=100)
    scatter_fig.subplots_adjust(bottom=0.15)  # Make room for x-axis labels
    scatter_canvas = FigureCanvasTkAgg(scatter_fig, master=scatter_frame)
    scatter_canvas.draw()
    scatter_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
    
    # Add toolbars with proper configuration
    time_series_toolbar_frame = ttk.Frame(time_series_frame)
    time_series_toolbar_frame.grid(row=1, column=0, sticky="ew")
    time_series_toolbar = NavigationToolbar2Tk(time_series_canvas, time_series_toolbar_frame)
    
    scatter_toolbar_frame = ttk.Frame(scatter_frame)
    scatter_toolbar_frame.grid(row=1, column=0, sticky="ew")
    scatter_toolbar = NavigationToolbar2Tk(scatter_canvas, scatter_toolbar_frame)
    
    # Create Data Preview tab
    data_frame = ttk.Frame(notebook, padding=10)
    notebook.add(data_frame, text="Data Preview")
    
    # Configure data frame
    data_frame.columnconfigure(0, weight=1)
    data_frame.rowconfigure(0, weight=1)
    
    # Create treeview for data preview with scrollbars
    data_frame_inner = ttk.Frame(data_frame)
    data_frame_inner.grid(row=0, column=0, sticky="nsew")
    
    data_tree = ttk.Treeview(data_frame_inner)
    
    # Add vertical and horizontal scrollbars
    data_vscroll = ttk.Scrollbar(data_frame_inner, orient="vertical", command=data_tree.yview)
    data_hscroll = ttk.Scrollbar(data_frame_inner, orient="horizontal", command=data_tree.xview)
    data_tree.configure(yscrollcommand=data_vscroll.set, xscrollcommand=data_hscroll.set)
    
    # Position widgets
    data_tree.grid(row=0, column=0, sticky="nsew")
    data_vscroll.grid(row=0, column=1, sticky="ns")
    data_hscroll.grid(row=1, column=0, sticky="ew")
    
    # Configure grid weights for scrolling
    data_frame_inner.columnconfigure(0, weight=1)
    data_frame_inner.rowconfigure(0, weight=1)
    
    # Create Metrics tab
    metrics_frame = ttk.Frame(notebook, padding=10)
    notebook.add(metrics_frame, text="Metrics")
    
    # Configure metrics frame
    metrics_frame.columnconfigure(0, weight=1)
    metrics_frame.rowconfigure(0, weight=1)
    
    # Create treeview for metrics with scrollbar
    metrics_tree = ttk.Treeview(metrics_frame)
    metrics_scroll = ttk.Scrollbar(metrics_frame, orient="vertical", command=metrics_tree.yview)
    metrics_tree.configure(yscrollcommand=metrics_scroll.set)
    
    metrics_tree.grid(row=0, column=0, sticky="nsew")
    metrics_scroll.grid(row=0, column=1, sticky="ns")
    
    # Store widgets in app for callbacks to access
    app.widgets['notebook'] = notebook
    app.widgets['time_series_fig'] = time_series_fig
    app.widgets['time_series_canvas'] = time_series_canvas
    app.widgets['time_series_toolbar'] = time_series_toolbar
    app.widgets['scatter_fig'] = scatter_fig
    app.widgets['scatter_canvas'] = scatter_canvas
    app.widgets['scatter_toolbar'] = scatter_toolbar
    app.widgets['data_tree'] = data_tree
    app.widgets['metrics_tree'] = metrics_tree
    
    # Store frames
    app.frames['time_series_frame'] = time_series_frame
    app.frames['scatter_frame'] = scatter_frame
    app.frames['data_frame'] = data_frame
    app.frames['metrics_frame'] = metrics_frame
    
    return notebook

def show_help(app):
    """Show help dialog."""
    help_window = tk.Toplevel(app.root)
    help_window.title("DSSAT Viewer Help")
    help_window.geometry("600x400")
    help_window.transient(app.root)  # Set to be always on top of the main window
    help_window.grab_set()  # Modal window
    
    # Apply theme background
    help_window.configure(bg=app.theme.get_color('background'))
    
    # Create scrollable text area
    help_text = ScrolledText.ScrolledText(help_window, wrap=tk.WORD, width=80, height=20)
    help_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    # Add help content
    help_content = """
    # DSSAT Viewer Help
    
    ## Overview
    
    DSSAT Viewer is a visualization tool for DSSAT crop model output data. This application provides an interface to run DSSAT simulations and visualize the results through time series and scatter plots.
    
    ## Getting Started
    
    1. Select a crop from the dropdown list
    2. Select an experiment file
    3. Select one or more treatments
    4. Click "Run Treatment" button
    5. Select output file(s) to view
    6. Select X and Y variables for plotting
    7. Click "Refresh Plot" to update the visualization
    
    ## Features
    
    - Run DSSAT simulations for different crops and treatments
    - View time series plots of simulated and observed data
    - Compare simulated vs. measured values through scatter plots
    - View performance metrics (RMSE, d-stat, etc.)
    - Explore data in tabular format
    
    ## Tips
    
    - You can select multiple output files to view combined data
    - You can select multiple Y variables to plot on the same graph
    - Switch between Time Series and Scatter Plot tabs to view different visualizations
    - Use the Data Preview tab to see the raw data
    - Use the Metrics tab to evaluate simulation performance
    """
    
    help_text.insert(tk.END, help_content)
    help_text.config(state=tk.DISABLED)  # Make read-only
    
    # Add close button
    close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
    close_button.pack(pady=10)

def create_app_layout(app):
    """Create the main application layout."""
    # Store root for convenience
    root = app.root
    
    # Configure main grid layout for responsiveness
    root.columnconfigure(0, weight=0)  # Sidebar column - fixed width
    root.columnconfigure(1, weight=1)  # Content column - expandable
    root.rowconfigure(0, weight=0)     # Toolbar row - fixed height
    root.rowconfigure(1, weight=1)     # Content row - expandable
    root.rowconfigure(2, weight=0)     # Status bar row - fixed height
    
    # Create toolbar
    toolbar_frame = ttk.Frame(root, style='Toolbar.TFrame', height=40)
    toolbar_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    
    # Add application title to toolbar
    title_label = ttk.Label(toolbar_frame, text="DSSAT Viewer", 
                          style='Heading.TLabel',
                          foreground=app.theme.get_color('text_on_primary'),
                          background=app.theme.get_color('primary'))
    title_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    # Add help button to toolbar
    help_button = ttk.Button(toolbar_frame, text="Help", command=lambda: show_help(app))
    help_button.pack(side=tk.RIGHT, padx=10, pady=5)
    
    # Create main frames with improved configuration
    sidebar_frame = ttk.Frame(root, width=250, padding=5)
    sidebar_frame.grid(row=1, column=0, sticky="nsew")
    sidebar_frame.grid_propagate(False)  # Prevent frame from shrinking
    
    # Enhanced content frame configuration
    content_frame = ttk.Frame(root, padding=10)
    content_frame.grid(row=1, column=1, sticky="nsew")
    content_frame.columnconfigure(0, weight=1)  # Make column expandable
    content_frame.rowconfigure(0, weight=1)     # Make row expandable
    
    # Ensure minimum size for content area
    content_frame.configure(width=600, height=400)  # Set minimum dimensions
    
    # Store frames in app for reference
    app.frames['toolbar_frame'] = toolbar_frame
    app.frames['sidebar_frame'] = sidebar_frame
    app.frames['content_frame'] = content_frame
    
    # Create sidebar elements with collapsible sections
    create_sidebar_layout(app, sidebar_frame)
    
    # Create main content area with notebook
    create_content_layout(app, content_frame)
    
    # Create status bar
    status_frame = ttk.Frame(root, relief=tk.SUNKEN, padding=(2, 1))
    status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    
    status_var = tk.StringVar(value="Ready")
    status_label = ttk.Label(status_frame, textvariable=status_var, anchor="w")
    status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Add version info to status bar
    version_label = ttk.Label(status_frame, text="DSSAT Viewer v1.0", font=app.theme.get_font('small'))
    version_label.pack(side=tk.RIGHT, padx=5)
    
    # Store status variables in app
    app.widgets['status_var'] = status_var
    
    # Create progress bar in status bar
    progress_var = tk.DoubleVar(value=0)
    progress_bar = ttk.Progressbar(
        status_frame, 
        orient="horizontal", 
        length=200, 
        mode="determinate",
        variable=progress_var
    )
    progress_bar.pack(side=tk.RIGHT, padx=5)
    
    # Store progress bar in app
    app.widgets['progress_var'] = progress_var
    app.widgets['progress_bar'] = progress_bar
    
    # Hide progress bar initially
    progress_bar.pack_forget()

def create_collapsible_section(parent, title, initial_state=True):
    """Create a collapsible section frame.
    
    Args:
        parent: Parent widget
        title: Section title
        initial_state: True for expanded, False for collapsed
        
    Returns:
        (frame, content_frame, is_expanded): Tuple containing main frame, 
                                           content frame, and expansion state variable
    """
    # Create main frame
    frame = ttk.LabelFrame(parent, text=title)
    
    # Create content frame that will be shown/hidden
    content_frame = ttk.Frame(frame)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    # Create variable to track expansion state
    is_expanded = tk.BooleanVar(value=initial_state)
    
    # Store the variable for later use
    frame.is_expanded = is_expanded
    
    return frame, content_frame, is_expanded

class AutoSizingListbox(tk.Frame):
    """A listbox that automatically adjusts its height based on the number of items.
    
    Attributes:
        listbox: The contained listbox widget
        scrollbar: The scrollbar widget
        max_items: Maximum number of items to display before enabling scrollbar
    """
    
    def __init__(self, parent, selectmode=tk.SINGLE, exportselection=0, max_items=10, **kwargs):
        """Initialize the auto-sizing listbox.
        
        Args:
            parent: Parent widget
            selectmode: Selection mode for the listbox
            exportselection: Whether to export selection
            max_items: Maximum items to show before enabling scrollbar
            **kwargs: Additional arguments for the frame
        """
        super().__init__(parent, **kwargs)
        
        self.max_items = max_items
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create listbox and scrollbar
        self.listbox = tk.Listbox(self, selectmode=selectmode, exportselection=exportselection)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=self.scrollbar.set)
        
        # Place widgets
        self.listbox.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Track item count
        self._item_count = 0
        
        # Bind events
        self.listbox.bind("<<ListboxSelect>>", self._on_selection_changed)
        
    def insert(self, index, *elements):
        """Insert items into the listbox and adjust height.
        
        Args:
            index: Position to insert
            *elements: Items to insert
        """
        self.listbox.insert(index, *elements)
        self._update_height()
        
    def delete(self, first, last=None):
        """Delete items from the listbox and adjust height.
        
        Args:
            first: First index to delete
            last: Last index to delete (optional)
        """
        self.listbox.delete(first, last)
        self._update_height()
        
    def get(self, first, last=None):
        """Get items from the listbox.
        
        Args:
            first: First index to get
            last: Last index to get (optional)
            
        Returns:
            Selected item(s)
        """
        return self.listbox.get(first, last)
        
    def curselection(self):
        """Get current selection indices.
        
        Returns:
            Tuple of selected indices
        """
        return self.listbox.curselection()
        
    def selection_set(self, first, last=None):
        """Set selection.
        
        Args:
            first: First index to select
            last: Last index to select (optional)
        """
        self.listbox.selection_set(first, last)
        
    def selection_clear(self, first, last=None):
        """Clear selection.
        
        Args:
            first: First index to clear
            last: Last index to clear (optional)
        """
        self.listbox.selection_clear(first, last)
        
    def size(self):
        """Get the number of items in the listbox.
        
        Returns:
            Number of items
        """
        return self.listbox.size()
        
    def _update_height(self):
        """Update the listbox height based on number of items."""
        # Get number of items
        item_count = self.listbox.size()
        
        # Update height
        if item_count > 0:
            # Set height to minimum of item count and max items
            new_height = min(item_count, self.max_items)
            self.listbox.configure(height=new_height)
        else:
            # Set minimum height
            self.listbox.configure(height=1)
            
    def _on_selection_changed(self, event):
        """Handle selection changed event."""
        # Forward the event
        self.event_generate("<<ListboxSelect>>")
        
    def bind(self, sequence, func, add=None):
        """Bind an event to the frame or the listbox.
        
        Args:
            sequence: Event sequence
            func: Callback function
            add: Add flag
        """
        if sequence == "<<ListboxSelect>>":
            # For listbox selection events, bind to the frame
            return super().bind(sequence, func, add)
        else:
            # For other events, bind to the listbox
            return self.listbox.bind(sequence, func, add)

def create_sidebar_layout(app, parent):
    """Create the sidebar layout with sections that auto-adjust to content."""
    # Configure sidebar to be responsive
    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=1)
    
    # Create scrollable container for sidebar content
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    # Configure scrolling
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    # Create window in canvas
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
    # Configure canvas to expand with frame
    def _configure_canvas(event):
        # Update the width of the canvas window
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas.bind("<Configure>", _configure_canvas)
    canvas.configure(yscrollcommand=scrollbar.grid)
    
    # Place scrollable components
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    
    # Configure the scrollable frame - it will contain all sidebar widgets
    scrollable_frame.columnconfigure(0, weight=1)
    
    row = 0
    
    # 1. Crop Selection
    ttk.Label(scrollable_frame, text="Select Crop").grid(row=row, column=0, sticky="w", pady=(5, 0), padx=5)
    row += 1
    
    folder_var = tk.StringVar()
    folder_combo = ttk.Combobox(scrollable_frame, textvariable=folder_var, state="readonly")
    folder_combo.grid(row=row, column=0, sticky="ew", pady=(0, 10), padx=5)
    row += 1
    
    # 2. Experiment Selection
    ttk.Label(scrollable_frame, text="Select Experiment").grid(row=row, column=0, sticky="w", pady=(5, 0), padx=5)
    row += 1
    
    experiment_var = tk.StringVar()
    experiment_combo = ttk.Combobox(scrollable_frame, textvariable=experiment_var, state="readonly")
    experiment_combo.grid(row=row, column=0, sticky="ew", pady=(0, 10), padx=5)
    row += 1
    
    # 3. Treatment Selection (auto-sizing)
    treatment_frame = ttk.LabelFrame(scrollable_frame, text="Select Treatments")
    treatment_frame.grid(row=row, column=0, sticky="ew", pady=5, padx=5)
    treatment_frame.columnconfigure(0, weight=1)
    
    # Create auto-sizing listbox for treatments
    treatment_listbox = AutoSizingListbox(
        treatment_frame,
        selectmode=tk.MULTIPLE,
        exportselection=0,
        max_items=8  # Maximum items to show before scrolling
    )
    treatment_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=5)
    
    row += 1
    
    # 4. Run Treatment Button
    run_button = ttk.Button(
        scrollable_frame,
        text="Run Treatment",
        style="Accent.TButton"
    )
    run_button.grid(row=row, column=0, sticky="ew", pady=10, padx=5)
    row += 1
    
    # 5. Separator
    ttk.Separator(scrollable_frame, orient="horizontal").grid(
        row=row, column=0, sticky="ew", pady=5, padx=5
    )
    row += 1
    
    # 6. Output Files Section (auto-sizing)
    output_frame = ttk.LabelFrame(scrollable_frame, text="Output Files")
    output_frame.grid(row=row, column=0, sticky="ew", pady=5, padx=5)
    output_frame.columnconfigure(0, weight=1)
    output_frame.grid_remove()  # Initially hidden
    
    # Create auto-sizing listbox for output files
    output_listbox = AutoSizingListbox(
        output_frame,
        selectmode=tk.MULTIPLE,
        exportselection=0,
        max_items=6  # Maximum items to show before scrolling
    )
    output_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=5)
    
    row += 1
    
    # 7. Variables Section
    variables_frame = ttk.LabelFrame(scrollable_frame, text="Variables")
    variables_frame.grid(row=row, column=0, sticky="ew", pady=5, padx=5)
    variables_frame.columnconfigure(0, weight=1)
    variables_frame.grid_remove()  # Initially hidden
    
    # X Variable
    ttk.Label(variables_frame, text="X Variable:").grid(
        row=0, column=0, sticky="w", pady=(5, 2), padx=5
    )
    
    x_var = tk.StringVar()
    x_combo = ttk.Combobox(variables_frame, textvariable=x_var, state="readonly")
    x_combo.grid(row=1, column=0, sticky="ew", pady=(0, 10), padx=5)
    
    # Y Variables (auto-sizing)
    ttk.Label(variables_frame, text="Y Variables:").grid(
        row=2, column=0, sticky="w", pady=(5, 2), padx=5
    )
    
    # Create auto-sizing listbox for Y variables
    y_listbox = AutoSizingListbox(
        variables_frame,
        selectmode=tk.MULTIPLE,
        exportselection=0,
        max_items=14  # Maximum items to show before scrolling
    )
    y_listbox.grid(row=3, column=0, sticky="ew", pady=5, padx=5)
    
    # Refresh button
    refresh_button = ttk.Button(
        variables_frame,
        text="Refresh Plot",
        style="Accent.TButton"
    )
    refresh_button.grid(row=4, column=0, sticky="ew", pady=10, padx=5)
    
    row += 1
    
    # Store widgets in app for callbacks to access
    app.widgets['folder_combo'] = folder_combo
    app.widgets['folder_var'] = folder_var
    app.widgets['experiment_combo'] = experiment_combo
    app.widgets['experiment_var'] = experiment_var
    app.widgets['treatment_listbox'] = treatment_listbox
    app.widgets['run_button'] = run_button
    app.widgets['output_frame'] = output_frame
    app.widgets['output_listbox'] = output_listbox
    app.widgets['variables_frame'] = variables_frame
    app.widgets['x_combo'] = x_combo
    app.widgets['x_var'] = x_var
    app.widgets['y_listbox'] = y_listbox
    app.widgets['refresh_button'] = refresh_button
    app.widgets['sidebar_canvas'] = canvas
    
    # Add methods to treatment_listbox and y_listbox to dynamically update their size
    def update_treatment_listbox():
        """Ensure the treatment listbox is updated when items are added."""
        treatment_listbox._update_height()
    
    def update_output_listbox():
        """Ensure the output listbox is updated when items are added."""
        output_listbox._update_height()
        
    def update_y_listbox():
        """Ensure the Y variables listbox is updated when items are added."""
        y_listbox._update_height()
    
    # Add the methods to the app for use in callbacks
    app.update_treatment_listbox = update_treatment_listbox
    app.update_output_listbox = update_output_listbox
    app.update_y_listbox = update_y_listbox