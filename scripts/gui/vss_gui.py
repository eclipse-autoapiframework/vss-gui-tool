import ast
import sys
import os

# Get the current working directory
current_dir = os.path.dirname(__file__)

# Construct the relative path
relative_path = os.path.join(current_dir, '../vss/vss-tools')

# Add the relative path to sys.path
sys.path.append(relative_path)

import vspec2x
from vspec.vssexporters import vss2json
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext 
import csv
from screeninfo import get_monitors
import logging
from vspec_app import VSPECApp
from typing import Dict, Any
from vspec.model.vsstree import VSSNode
import json

# Class defined for Redirecting standard data and standard error messages to log window
class RedirectText(object):
    def __init__(app, widget):
        app.widget = widget

    def write(app, string):
        app.widget.insert(tk.END, string)
        app.widget.see(tk.END)

    def flush(app):
        pass
        
# Class defined for Hovering of data in current application
class ToolTip(tk.Toplevel):
    def __init__(app, widget, text="", line_length=50):
        super().__init__(widget)
        app.widget = widget
        app.text = text
        app.line_length = line_length
        app.overrideredirect(True)
        app.geometry("+0+0")
        app.label = tk.Label(app, text=app.wrap_text(app.text), background="white", relief="solid", borderwidth=1,
                              justify='left')
        app.label.grid()

    # Wrapping text in hover
    def wrap_text(app, text):
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            if len(' '.join(current_line + [word])) <= app.line_length:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)

    def show(app, x, y):
        app.geometry(f"+{x}+{y}")
        app.deiconify()

    def hide(app):
        app.withdraw()

# class for GUI creation
class TextSearchApp:
    def __init__(app, root, log_window):
        app.root = root
        root.title("VSS_GUI")
        # Geometry of the GUI(width,height)
        app.root.geometry(f"{window_width}x{window_height}") 
        # Hovering variable initialized to None
        app.tooltip = None
        app.folder_path = tk.StringVar()
        app.file_list = []
        app.current_file = None
 
        # Frame for grid layout (first and second rows)
        app.grid_frame = tk.Frame(root)
        app.grid_frame.grid(row=0, column=0, sticky="nsew")

        # Browse Folder Label and Entry
        app.label = tk.Label(app.grid_frame , text="Folder")
        app.label.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')

        app.folder_entry = tk.Entry(app.grid_frame , textvariable=folder_path_, width=100)
        app.folder_entry.grid(row=0, column=1, padx=10, pady=5)

        # Create a button to browse for a folder
        app.browse_button = tk.Button(app.grid_frame , text="Browse Folder", command=app.browse_folder)
        app.browse_button.grid(row=0, column=2, padx=10, pady=5)

        # Create a label and entry for the search term
        app.search_label = tk.Label(app.grid_frame , text="Search Text")
        app.search_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')

        app.search_entry = tk.Entry(app.grid_frame , width=100)
        app.search_entry.grid(row=1, column=1, padx=10, pady=5)

        # Create a button and label for the search term
        app.search_button = tk.Button(app.grid_frame , text="Search", command=app.search_text)
        app.search_button.grid(row=1, column=2, padx=10, pady=5)
         
        app.search_label = tk.Label(app.grid_frame , text="Search Data")
        app.search_label.grid(row=2, column=0, padx=10, pady=10, sticky='N')

        # Button to clear search results
        app.clear_button = tk.Button(app.grid_frame , text="Clear Search", command=app.clear_results)
        app.clear_button.grid(row=2, column=2, padx=10, pady=10)

        # Frame for treeview layout (third row)
        app.tree_frame = tk.Frame(root)
        app.tree_frame.grid(row=3, column=0, sticky="nsew")
        app.tree_frame.grid_columnconfigure(0, weight=1)
        app.tree_frame.grid_rowconfigure(0, weight=1)


        # Treeview widget to display search results
        app.tree_results = ttk.Treeview(app.tree_frame, columns=("Signal", "Type", "DataType","Unit", "Min", "Max","Default", "Allowed","Description"), show="headings")
        app.tree_results.heading("Signal", text="Signal")
        app.tree_results.heading("Type", text="Type")
        app.tree_results.heading("DataType", text="DataType")
        app.tree_results.heading("Unit", text="Unit")
        app.tree_results.heading("Min", text="Min")
        app.tree_results.heading("Max", text="Max")
        app.tree_results.heading("Default", text="Default")
        app.tree_results.heading("Allowed", text="Allowed")
        app.tree_results.heading("Description", text="Description")

        app.tree_results.grid(row=3, column=0, columnspan=9, padx=10, pady=10, sticky="nsew")

        # Bind the <Double-1> event to the column headers
        app.tree_results.bind("<Double-1>", app.adjust_column_width)

        # Hovering on display search results
        app.tree_results.bind("<Motion>", app.on_search_hover)
        app.tree_results.bind("<Leave>", app.hide_tooltip)

        # Add a scrollbar for the table/treeview
        app.scrollbar_results = ttk.Scrollbar(app.tree_frame , orient=tk.VERTICAL, command=app.tree_results.yview)       
        app.scrollbar_results.grid(row=3, column=3, sticky="ns")
        app.tree_results.configure(yscroll=app.scrollbar_results.set)

        # Bind the configure event to the resize function
        app.tree_frame.bind("<Configure>", app.resize_columns)

        # Frame for grid layout (5th row)
        app.grid_frame2 = tk.Frame(root)
        app.grid_frame2.grid(row=5, column=0, sticky="nsew")

        # Create a label for the Selected Data
        app.search_label = tk.Label(app.grid_frame2 , text="Selected Data")
        app.search_label.grid(row=5, column=0, padx=10, pady=10, sticky='e')

        # Button to move selected item to selected list
        app.move_button = tk.Button(app.grid_frame2 , text="Move to Selected", command=app.move_to_selected)
        app.move_button.grid(row=5, column=2, padx=100, pady=10, sticky='nw')

        # Button to remove selected item from selected list
        app.remove_button = tk.Button(app.grid_frame2 , text="Remove from Selected", command=app.remove_from_selected)
        app.remove_button.grid(row=5, column=3, padx=100, pady=10)

        # Button to Selected search results
        app.Select_clear_button = tk.Button(app.grid_frame2 , text="Clear Select list", command=app.clear_Selected_list)
        app.Select_clear_button.grid(row=5, column=4, padx=100, pady=10, sticky='e')
 
        # Frame for table/treeview layout (6th row)
        app.tree_frame2 = tk.Frame(root)
        app.tree_frame2.grid(row=6, column=0, sticky="nsew")
        app.tree_frame2.grid_columnconfigure(0, weight=1)
        app.tree_frame2.grid_rowconfigure(0, weight=1)

        # table/treeview widget to display selected items
        app.tree_selected = ttk.Treeview(app.tree_frame2 , columns=("Signal", "Type", "DataType","Unit", "Min", "Max","Default", "Allowed","Vspec","Description"), show="headings")
        app.tree_selected.heading("Signal", text="Signal")
        app.tree_selected.heading("Type", text="Type")
        app.tree_selected.heading("DataType", text="DataType")
        app.tree_selected.heading("Unit", text="Unit")
        app.tree_selected.heading("Min", text="Min")
        app.tree_selected.heading("Max", text="Max")
        app.tree_selected.heading("Default", text="Default")
        app.tree_selected.heading("Allowed", text="Allowed")
        app.tree_selected.heading("Description", text="Description")

        app.tree_selected.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Bind the <Double-1> event (Double click event) to the column headers
        app.tree_selected.bind("<Double-1>", app.adjust_column_width)
        
        # Hovering on display Selected Data
        app.tree_selected.bind("<Motion>", app.on_selected_hover)
        app.tree_selected.bind("<Leave>", app.hide_tooltip)

        # Add a scrollbar for the table/treeview
        app.scrollbar_selected = ttk.Scrollbar(app.tree_frame2, orient=tk.VERTICAL, command=app.tree_selected.yview)
        app.scrollbar_selected.grid(row=6, column=3, sticky="ns")
        app.tree_selected.configure(yscroll=app.scrollbar_selected.set) 

        # Bind the configure event to the resize function
        app.tree_frame2.bind("<Configure>", app.resize_columns)
        
        # Frame for grid layout (7th row)
        app.grid_frame3 = tk.Frame(root)
        app.grid_frame3.grid(row=7, column=0, sticky="nsew")

        # Button to update New Signal and Branch details into VSPEC file 
        app.open_button = tk.Button(app.grid_frame3, text="VSPEC_Update", command=open_vspec_app)
        app.open_button.grid(row=7, column=1,padx=300, pady=10, sticky="nsew")

        # Button to generate CSV file from selected items
        # app.generate_button = tk.Button(app.grid_frame3 , text="Generate CSV File", command=app.generate_csv)
        # app.generate_button.grid(row=7, column=2, padx=500, pady=10, sticky='nsew')

        # Button to generate JSON file from selected items
        app.generate_button = tk.Button(app.grid_frame3 , text="Generate JSON File", command=app.generate_json)
        app.generate_button.grid(row=7, column=2, padx=500, pady=10, sticky='nsew')

        # Frame for grid layout (8th row)
        app.grid_frame3 = tk.Frame(root)
        app.grid_frame3.grid(row=8, column=0, sticky="nsew")

        # Bind the delete_file_on_exit method to window close event to delete intermediate file
        app.root.protocol("WM_DELETE_WINDOW", app.on_closing)

        # Create a Text widget in the log window to display messages
        app.log_text = scrolledtext.ScrolledText(log_window, width=70, height=15, bg ='Black', fg = 'White')
        app.log_text.pack(padx=10, pady=10)

        # Redirect stdandard out and stdandard err
        sys.stdout = RedirectText(app.log_text)
        sys.stderr = RedirectText(app.log_text)
        

    def adjust_column_width(app, event):
        # Identify the region where the double-click occurred
        region = app.tree_selected.identify("region", event.x, event.y)
        if region == "heading":
            # Get the column that was double-clicked
            column = app.tree_selected.identify_column(event.x)
            # Calculate the maximum width of the column content
            max_width = max(
                app.tree_selected.bbox(item, column)['width'] for item in app.tree_selected.get_children(''))
            # Set the column width
            app.tree_selected.column(column, width=max_width)

    # Code to re-size the columns width according to the size of Application
    def resize_columns(app, event):
        # Calculate the width of each column based on the treeview's width
        total_width = app.tree_results.winfo_width()
        num_columns = len(app.tree_results["columns"])
        new_width = int(total_width / num_columns)

        for col in app.tree_results["columns"]:
            app.tree_results.column(col, width=new_width)

    # Code to Browse VSS Spec path 
    def browse_folder(app):
        app.folder_path = filedialog.askdirectory()          
        folder_path_.set(app.folder_path)

        app.vspec_file_path = app.folder_path + "/VehicleSignalSpecification.vspec"
        app.yaml_File_path = app.folder_path + "/units.yaml"
        app.Internal_file = app.folder_path + "/Donot_Delete_Internal_file.csv"

        sys.argv = [os.path.basename(__file__), "-I", "../spec", "-u", app.yaml_File_path, app.vspec_file_path, app.Internal_file]
        vspec2x.main(sys.argv[1:])
        
        app.data_File_path = app.folder_path  + "/Donot_Delete_Internal_file.csv"
        app.csv_path = app.data_File_path
        
        # Load CSV file after setting up the Treeview
        app.load_csv_file()

    # Code to Delete the Intermediate file created while closing the application    
    def on_closing(app):
            app.delete_file_on_exit()
            app.root.destroy() 
          
    # Code to Delete the Intermediate file created while using the application      
    def delete_file_on_exit(app):
                if os.path.isfile(app.data_File_path):
                    print(f"File found: {app.data_File_path}")
                    app.file_found = True

                if app.file_found:
                     try:
                         os.remove(app.data_File_path)
                         print(f"Deleted File: {app.data_File_path}")
                     except Exception as e:
                         print(f"Error deleting file: {e}") 
    
    # Code for Data extraction from Intermediate file 
    def load_csv_file(app):
                try:
                      with open(app.csv_path, newline='', encoding='utf-8') as csvfile:
                           app.data = list(csv.reader(csvfile))
                           app.columns = ["Signal", "Type", "DataType","Unit", "Min", "Max","Default", "Allowed","Description"]
                           app.tree_results["columns"] = app.columns
                           app.tree_selected["columns"] = app.columns
                           for col in app.columns:
                                app.tree_results.heading(col, text=col)                                
                                app.tree_selected.heading(col, text=col)                                

                    #  messagebox.showinfo("Success", "CSV file loaded successfully")
                except FileNotFoundError:
                     messagebox.showerror("Error", f" Internal file not found at {app.csv_path}") #f"CSV file not found at {app.csv_path}")
                except Exception as e:
                     messagebox.showerror("Error", f"Failed to load Internal file: {str(e)}")
      

    #Code to Search text in vspec files 
    def search_text(app):
        search_text = app.search_entry.get().strip()
        if not hasattr(app, 'data'):
            messagebox.showwarning("Error", "Issue with vspec file path above, Provide the 'Spec' folder path")#"CSV file not loaded")
            return
        if not search_text:
            messagebox.showwarning("Error", "Please enter text to search")
            return

        # Clear previous search results
        for row in app.tree_results.get_children():
            app.tree_results.delete(row)

        # Search for the text in the 'A' column of the data
        for row in app.data[1:]:  # Skip header row
            if search_text.lower() in row[0].lower() and row[1].lower() != "branch":
               #treeview = app.tree_results.insert("", "end", values=(row[0], row[1], row[2], row[4], row[5], row[6],row[12], row[9], row[10],row[11], row[13], row[7]))           
                treeview = app.tree_results.insert("", "end", values=(row[0], row[1], row[2], row[4], row[5], row[6], row[10], row[9], row[7]))           

    # Move Selected data from Search list to Selected list
    def move_to_selected(app):
        selected_items = app.tree_results.selection()
        existing_selected_values = [app.tree_selected.item(item, "values") for item in
                                    app.tree_selected.get_children()]
        duplicates = []

        for item in selected_items:
            values = app.tree_results.item(item, "values")
            if values not in existing_selected_values:
                treeview= app.tree_selected.insert("", "end", values=values)
                app.tree_results.delete(item)
            else:
                duplicates.append(values[0])  # Collecting only the 'A' column value

        if duplicates:
            duplicate_signals = "\n".join(duplicates)
            messagebox.showwarning("Duplicate Entries", f"The following signals are present in the selected list:\n{duplicate_signals}")

    # Remove Selected data from Selected list
    def remove_from_selected(app):
        selected_items = app.tree_selected.selection()
        existing_selected_values = [app.tree_results.item(item, "values") for item in
                                        app.tree_results.get_children()]        
        for item in selected_items:
            values = app.tree_selected.item(item, "values")
            if values not in existing_selected_values:
                app.tree_results.insert("", "end", values=values)
                app.tree_selected.delete(item)

            else:
                app.tree_selected.delete(item)                

    # Clear All Search  Results
    def clear_results(app) :
        for row in app.tree_results.get_children():
            app.tree_results.delete(row)

    # Clear All Selected Data
    def clear_Selected_list(app):
        for row in app.tree_selected.get_children():
            app.tree_selected.delete(row)        

    # Hover on Search Results
    def on_search_hover(app, event):
        app.handle_hover(event, app.tree_results)

    # Hover on Selected Data
    def on_selected_hover(app, event):
        app.handle_hover(event, app.tree_selected)

    # Hover on cell Data
    def handle_hover(app, event, treeview):
        item = treeview.identify("item", event.x, event.y)
        column = treeview.identify_column(event.x)
        if item and column:
            cell_value = treeview.item(item, "values")[int(column[1:]) - 1]
            if app.tooltip:
                app.tooltip.destroy()
            app.tooltip = ToolTip(treeview, cell_value)
            x, y, _, _ = treeview.bbox(item, column)
            x += treeview.winfo_rootx()
            y += treeview.winfo_rooty()
            app.tooltip.show(x, y + 20)

    # Code to support Hovering
    def hide_tooltip(app, event):
        if app.tooltip:
            app.tooltip.destroy()
            app.tooltip = None

    #Generate CSV Output file with Selected data elements
    def generate_csv(app):
        selected_items = app.tree_selected.get_children()
        if not selected_items:
            messagebox.showerror("Error", "Selected list is empty")
            return

        selected_data = [app.tree_selected.item(item, "values") for item in selected_items]
        csv_file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        if csv_file_path:
            try:
                with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Signal", "Type", "DataType","Unit", "Min", "Max","Default", "Allowed","Vspec","Description"])  # Write header
                    writer.writerows(selected_data)
                messagebox.showinfo("Success", f"CSV file has been saved at {csv_file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save CSV file: {str(e)}")
        
        app.folder_path = app.csv_path.replace("/Donot_Delete_Internal_file.csv", "")

    # Build the tree based on selected data elements 
    def build_vss_tree(selected_data):
        tree = {}
        for row in selected_data:
            path = row[0].split('.')
            current = tree
            for part in path[:-1]:
                current = current.setdefault(part, {"type": "branch", "children": {}})["children"]
            signal_name = path[-1]
            signal_data = {
                "type": row[1],
                "datatype": row[2],
                "unit": row[3],
                "min": float(row[4]) if row[4] != '' else "", # Conversion of string to double only if entry is available 
                "max": float(row[5]) if row[5] != '' else "", # Conversion of string to double only if entry is available
                "default": row[6] if (row[6] == "UNKNOWN") else (float(row[6]) if (row[6] != '') else ""), #lists are not supported in this version
                "allowed": ast.literal_eval(row[7]) if row[7] != '' else "", # Conversion of string to python list
                "description": row[8],
            }
            # Remove keys with empty list values
            signal_data = {k: v for k, v in signal_data.items() if v != ""}
            current[signal_name] = signal_data
        return tree

    #Generate JSON Output file with Selected data elements
    def generate_json(app):
        selected_items = app.tree_selected.get_children()
        if not selected_items:
            messagebox.showerror("Error", "Selected list is empty")
            return

        selected_data = [app.tree_selected.item(item, "values") for item in selected_items]
        vss_tree = TextSearchApp.build_vss_tree(selected_data)
        json_file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])

        if json_file_path:
            try:
                with open(json_file_path, mode='w', encoding='utf-8') as file: 
                    json.dump(vss_tree, file, indent=4)
                    messagebox.showinfo("Success", f"JSON file has been saved at {json_file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save JSON file: {str(e)}")
        
        app.folder_path = app.csv_path.replace("/Donot_Delete_Internal_file.csv", "")    


# Code to display the the Log window    
def open_log_window():
        log_window = tk.Toplevel(root)
        log_window.title("Log Output")
        return log_window 

# Code to Call the VSPEC File Manager Application
def open_vspec_app():
    vspec_root = tk.Toplevel()
    app = VSPECApp(vspec_root)
    vspec_root.mainloop()    

if __name__ == "__main__":
    root = tk.Tk()

    # Get screen width and height
    screen_width = root.winfo_screenwidth() 
    screen_height = root.winfo_screenheight()

    # # Set the window size of the screen size
    window_width = int(screen_width *0.9)
    window_height = int(screen_height *0.9)

    folder_path_ = tk.StringVar()
    log_window = open_log_window()
    Instance_App = TextSearchApp(root, log_window)

    root.mainloop()
