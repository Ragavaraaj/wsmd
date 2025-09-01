import tkinter as tk
import threading
import time
from datetime import datetime

import os
import sqlite3
from pathlib import Path

large_font = ("Arial", 96, "bold")
medium_font = ("Arial", 64)
small_font = ("Arial", 32)

common_bg = "black"
common_fg = "white"


class DeviceDashboard:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.devices = []
        self.last_data_hash = None  # For tracking changes
        
        # Start the refresh thread
        self.running = True
        self.thread = threading.Thread(target=self.refresh_thread)
        self.thread.daemon = True
        self.thread.start()
    
    def setup_ui(self):
        # Configure the window
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="black")
        
        # Create header frame
        header_frame = tk.Frame(self.root, bg="black")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text="WSMD",
            font=small_font,
            fg=common_fg,
            bg=common_bg
        )
        title_label.pack(side=tk.LEFT)
        
        # Current time
        self.time_label = tk.Label(
            header_frame,
            text="",
            font=small_font,
            fg=common_fg,
            bg=common_bg
        )
        self.time_label.pack(side=tk.RIGHT)
        self.update_time()
        
        # Create table frame
        self.table_frame = tk.Frame(self.root, bg="black")
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=40)
        
        # Create an empty cell at position (0,0)
        empty_cell = tk.Label(
            self.table_frame,
            text="",
            font=medium_font,
            fg=common_fg,
            bg=common_bg,
            borderwidth=1,
            relief="flat",
            padx=5,
            pady=5
        )
        empty_cell.grid(row=0, column=0, sticky="nsew")
        
        # Create "COUNT" label at position (1,0)
        count_label = tk.Label(
            self.table_frame,
            text="HIT",
            font=medium_font,
            fg=common_fg,
            bg=common_bg,
            borderwidth=0,
            relief="flat",
            padx=5,
            pady=5
        )
        count_label.grid(row=1, column=0, sticky="nsew")
        
        # Create "MAX" label at position (2,0)
        max_label = tk.Label(
            self.table_frame,
            text="SET",
            font=medium_font,
            fg=common_fg,
            bg=common_bg,
            borderwidth=0,
            relief="flat",
            padx=5,
            pady=5
        )
        max_label.grid(row=2, column=0, sticky="nsew")
        
        no_hit_label = tk.Label(
            self.table_frame,
            text="NO HIT",
            font=medium_font,
            fg=common_fg,
            bg=common_bg,
            borderwidth=0,
            relief="flat",
            padx=5,
            pady=5
        )
        no_hit_label.grid(row=3, column=0, sticky="nsew")
        
        
        # Configure grid
        self.table_frame.grid_columnconfigure(0, weight=1)  # First column
        
        # We'll use the table_frame directly for the device data
        # No need for a separate devices_frame
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=common_bg, height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame,
            text="Dashboard initialized. Waiting for data...",
            font=small_font,
            fg=common_fg,
            bg=common_bg,
            anchor="w",
            padx=10
        )
        self.status_label.pack(fill=tk.X)
        
        # Add exit button (press Escape to exit)
        self.root.bind("<Escape>", self.exit_application)
    
    def update_time(self):
        """Update the current time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def update_device_table(self):
        """Update the device table with current data"""
        # Clear existing device data (keep the first column with labels)
        for widget in self.table_frame.winfo_children():
            grid_info = widget.grid_info()
            if grid_info and int(grid_info["column"]) > 0:
                widget.destroy()
        
        if not self.devices:
            # Show "No devices" message
            no_devices_label = tk.Label(
                self.table_frame,
                text="No devices found",
                font=large_font,
                fg=common_fg,
                bg=common_bg,
                padx=10,
                pady=20
            )
            no_devices_label.grid(row=0, column=1, rowspan=3, sticky="nsew")
            return
        
        # Configure columns for devices
        for i in range(len(self.devices)):
            self.table_frame.grid_columnconfigure(i+1, weight=1)
        
        
        # Create columns for each device
        for i, device in enumerate(self.devices):
            col_index = i + 1  # Start from column 1 (column 0 has labels)
            
            # Device Name/MAC as header (row 0)
            device_name = device.get("name") or device["mac_address"]
            device_label = tk.Label(
                self.table_frame,
                text=device_name,
                font=large_font,
                fg=common_fg,
                bg=common_bg,
                borderwidth=0,
                relief="flat",
                padx=5,
                pady=5
            )
            device_label.grid(row=0, column=col_index, sticky="nsew")
            
            # Hit counter (row 1)
            hit_label = tk.Label(
                self.table_frame,
                text=str(device["hit_counter"]),
                font=large_font,
                fg=common_fg,
                bg=common_bg,
                padx=10,
                pady=10
            )
            hit_label.grid(row=1, column=col_index, sticky="nsew")
            
            # Max hits (row 2)
            max_hit_label = tk.Label(
                self.table_frame,
                text=str(device["max_hits"]),
                font=large_font,
                fg=common_fg,
                bg=common_bg,
                padx=10,
                pady=10
            )
            max_hit_label.grid(row=2, column=col_index, sticky="nsew")
            
            # Highlight row if over limit
            no_hit_label = tk.Label(
                self.table_frame,
                text="",
                font=large_font,
                fg=common_fg,
                bg=common_bg,
                padx=10,
                pady=10
            )
            no_hit_label.grid(row=3, column=col_index, sticky="nsew")
    
    def fetch_devices(self):
        """Fetch device data directly from the SQLite database"""
        try:
            # Determine the path to the database file
            # Assuming the database is in the root of the project
            db_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).joinpath("wsmd.db")
            
            # Connect to the SQLite database
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()
            
            # Execute the SQL query - include all needed columns and sort by order
            cursor.execute('SELECT "mac_address", "hit_counter", "max_hits", "name" FROM devices ORDER BY "order"')

            # Convert to list of dictionaries
            new_devices = []
            for row in cursor.fetchall():
                new_devices.append({
                    "mac_address": row["mac_address"],
                    "hit_counter": row["hit_counter"],
                    "max_hits": row["max_hits"],
                    "name": row["name"],
                })
            
            # Close the connection
            conn.close()
            
            # Generate a hash of the new data
            new_data_hash = hash(str(new_devices))
            
            # Only update the UI and status if data has changed
            if new_data_hash != self.last_data_hash:
                self.devices = new_devices
                self.last_data_hash = new_data_hash
                self.status_label.config(
                    text=f"{len(self.devices)} devices found"
                )
                # Force an immediate UI update when data changes
                self.root.after(0, self.update_device_table)
                return True  # Data changed
            return False  # No change in data
            
        except Exception as e:
            self.status_label.config(
                text=f"Error connecting to database: {str(e)}"
            )
            return False  # Error occurred
    
    def refresh_thread(self):
        """Background thread to refresh data periodically"""
        while self.running:
            try:
                # Fetch new data - will only update UI if data changed
                self.fetch_devices()
                
                # Wait for next refresh - shorter interval for more responsive updates
                time.sleep(0.5)  # Check twice per second for near real-time updates
            except Exception as e:
                # Handle any unexpected errors to prevent thread from crashing
                print(f"Error in refresh thread: {str(e)}")
                time.sleep(1)  # Wait a bit longer if there was an error
    
    def exit_application(self, event=None):
        """Exit the application"""
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DeviceDashboard(root)
    root.mainloop()
