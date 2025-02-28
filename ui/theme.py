"""
Theme configuration for DSSAT Viewer's Tkinter UI
"""
import tkinter as tk
from tkinter import ttk
import platform

class DSSATTheme:
    """Theme manager for DSSAT Viewer application.
    
    This class manages the visual styling of the application,
    providing a modern and consistent appearance across platforms.
    
    Attributes:
        colors (dict): Dictionary of color values used in the theme
        fonts (dict): Dictionary of font configurations for different UI elements
    """
    
    def __init__(self):
        """Initialize theme with default color scheme."""
        self.colors = {
            # Primary colors
            'primary': '#1976D2',        # Blue
            'primary_light': '#BBDEFB',  # Light blue
            'primary_dark': '#0D47A1',   # Dark blue
            
            # Secondary colors
            'secondary': '#388E3C',      # Green
            'secondary_light': '#C8E6C9', # Light green
            'secondary_dark': '#1B5E20', # Dark green
            
            # UI colors
            'background': '#F5F5F5',     # Light gray
            'surface': '#FFFFFF',        # White
            'error': '#D32F2F',          # Red
            'warning': '#FFA000',        # Amber
            'info': '#0288D1',           # Light blue
            'success': '#388E3C',        # Green
            
            # Text colors
            'text_primary': '#212121',   # Dark gray (almost black)
            'text_secondary': '#757575', # Medium gray
            'text_disabled': '#BDBDBD',  # Light gray
            'text_on_primary': '#FFFFFF',  # White
            'text_on_secondary': '#FFFFFF', # White
            
            # Border colors
            'border': '#E0E0E0',         # Very light gray
            'divider': '#EEEEEE',        # Even lighter gray
        }
        
        # Determine system-specific font settings
        system = platform.system()
        if system == 'Windows':
            base_font = 'Segoe UI'
            mono_font = 'Consolas'
        elif system == 'Darwin':  # macOS
            base_font = 'Helvetica Neue'
            mono_font = 'Menlo'
        else:  # Linux and others
            base_font = 'DejaVu Sans'
            mono_font = 'DejaVu Sans Mono'
        
        self.fonts = {
            'default': (base_font, 10),
            'heading': (base_font, 14, 'bold'),
            'subheading': (base_font, 12, 'bold'),
            'button': (base_font, 10),
            'monospace': (mono_font, 10),
            'small': (base_font, 9),
            'tiny': (base_font, 8),
        }
    
    def apply(self, root):
        """Apply theme to the application.
        
        Args:
            root (tk.Tk): The root window of the application
        """
        # Configure root window
        root.configure(bg=self.colors['background'])
        
        # Create style
        style = ttk.Style(root)
        
        # Use a modern theme as base
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        
        # Configure ttk styles
        style.configure('TFrame', background=self.colors['background'])
        style.configure('Surface.TFrame', background=self.colors['surface'])
        style.configure('Card.TFrame', background=self.colors['surface'], 
                      relief='solid', borderwidth=1, bordercolor=self.colors['border'])
        
        style.configure('TLabel', background=self.colors['background'], 
                      foreground=self.colors['text_primary'],
                      font=self.fonts['default'])
        
        style.configure('Heading.TLabel', 
                      font=self.fonts['heading'],
                      foreground=self.colors['primary_dark'])
        
        style.configure('Subheading.TLabel', 
                      font=self.fonts['subheading'])
        
        style.configure('TButton', 
                      font=self.fonts['button'],
                      background=self.colors['primary'],
                      foreground=self.colors['text_on_primary'])
        
        style.map('TButton',
                background=[('active', self.colors['primary_dark'])],
                foreground=[('active', self.colors['text_on_primary'])])
        
        style.configure('Accent.TButton',
                      background=self.colors['secondary'],
                      foreground=self.colors['text_on_secondary'])
        
        style.map('Accent.TButton',
                background=[('active', self.colors['secondary_dark'])],
                foreground=[('active', self.colors['text_on_secondary'])])
        
        style.configure('TEntry', 
                      fieldbackground=self.colors['surface'],
                      font=self.fonts['default'])
        
        style.configure('TCombobox', 
                      fieldbackground=self.colors['surface'],
                      font=self.fonts['default'])
        
        style.configure('TNotebook', 
                      background=self.colors['background'])
        
        style.configure('TNotebook.Tab', 
                      background=self.colors['background'],
                      foreground=self.colors['text_primary'],
                      font=self.fonts['default'],
                      padding=[10, 4])
        
        style.map('TNotebook.Tab',
                background=[('selected', self.colors['primary'])],
                foreground=[('selected', self.colors['text_on_primary'])])
        
        style.configure('Treeview', 
                      background=self.colors['surface'],
                      fieldbackground=self.colors['surface'],
                      foreground=self.colors['text_primary'],
                      font=self.fonts['default'],
                      rowheight=25)
        
        style.configure('Treeview.Heading', 
                      background=self.colors['primary_light'],
                      foreground=self.colors['text_primary'],
                      font=self.fonts['subheading'])
        
        style.map('Treeview',
                background=[('selected', self.colors['primary_light'])],
                foreground=[('selected', self.colors['primary_dark'])])
        
        # Configure listbox, text and other tk widgets
        root.option_add('*TkListbox*background', self.colors['surface'])
        root.option_add('*TkListbox*foreground', self.colors['text_primary'])
        root.option_add('*TkListbox*font', self.fonts['default'])
        root.option_add('*TkListbox*selectBackground', self.colors['primary'])
        root.option_add('*TkListbox*selectForeground', self.colors['text_on_primary'])
        
        root.option_add('*TkText*background', self.colors['surface'])
        root.option_add('*TkText*foreground', self.colors['text_primary'])
        root.option_add('*TkText*font', self.fonts['default'])
        
        root.option_add('*TkCanvas*background', self.colors['surface'])
        
        # Configure scrollbars
        style.configure('TScrollbar', 
                      background=self.colors['background'],
                      troughcolor=self.colors['surface'],
                      bordercolor=self.colors['border'],
                      arrowcolor=self.colors['primary'])
    
    def create_custom_widget_styles(self, style):
        """Create custom widget styles.
        
        Args:
            style (ttk.Style): The style object to configure
        """
        # Create a section header style (a label with a line underneath)
        style.configure('Section.TLabel',
                      font=self.fonts['subheading'],
                      foreground=self.colors['primary_dark'],
                      padding=(0, 10, 0, 5))
        
        # Toolbar-style frame
        style.configure('Toolbar.TFrame',
                      background=self.colors['primary_light'],
                      relief='flat')
        
        # Card style for content boxes
        style.configure('Card.TFrame',
                      background=self.colors['surface'],
                      relief='raised',
                      borderwidth=1)
        
        # Info panel style
        style.configure('InfoPanel.TFrame',
                      background=self.colors['info'],
                      relief='flat',
                      borderwidth=0)
        
        style.configure('InfoPanel.TLabel',
                      background=self.colors['info'],
                      foreground=self.colors['text_on_primary'],
                      font=self.fonts['default'])
        
        # Warning panel style
        style.configure('WarningPanel.TFrame',
                      background=self.colors['warning'],
                      relief='flat',
                      borderwidth=0)
        
        style.configure('WarningPanel.TLabel',
                      background=self.colors['warning'],
                      foreground=self.colors['text_on_primary'],
                      font=self.fonts['default'])
        
        # Error panel style
        style.configure('ErrorPanel.TFrame',
                      background=self.colors['error'],
                      relief='flat',
                      borderwidth=0)
        
        style.configure('ErrorPanel.TLabel',
                      background=self.colors['error'],
                      foreground=self.colors['text_on_primary'],
                      font=self.fonts['default'])
        
        # Success panel style
        style.configure('SuccessPanel.TFrame',
                      background=self.colors['success'],
                      relief='flat',
                      borderwidth=0)
        
        style.configure('SuccessPanel.TLabel',
                      background=self.colors['success'],
                      foreground=self.colors['text_on_primary'],
                      font=self.fonts['default'])
    
    def get_color(self, name):
        """Get a color value by name.
        
        Args:
            name (str): The name of the color
            
        Returns:
            str: The color value
        """
        return self.colors.get(name, self.colors['text_primary'])
    
    def get_font(self, name):
        """Get a font configuration by name.
        
        Args:
            name (str): The name of the font configuration
            
        Returns:
            tuple: The font configuration
        """
        return self.fonts.get(name, self.fonts['default'])