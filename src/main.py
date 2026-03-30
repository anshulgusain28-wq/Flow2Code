import tkinter as tk
import sys
import os
import ctypes

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.editor import FlowchartEditor

def main():
    # HIGH DPI FIX FOR WINDOWS
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1) # 1 = Process System DPI Aware
    except Exception:
        pass # Not on Windows 8.1+

    root = tk.Tk()
    root.title("Flow2Code - Flowchart to Python Compiler")
    root.geometry("1600x1000") # Larger default size for high res
    
    # Optional: scaling for consistency across screens
    # root.tk.call('tk', 'scaling', 2.0) 

    app = FlowchartEditor(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()
