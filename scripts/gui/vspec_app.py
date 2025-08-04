import tkinter as tk
from tkinter import ttk, filedialog, messagebox, OptionMenu
import sys
import os
import csv
import ast  # Import the ast module
import vspec2x
from vspec.vssexporters import vss2csv
import yaml

# Class defined to update VSS Spec files
class VSPECApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VSPEC File Manager")

        self.file_list = []
        self.current_file = None
        self.csv_data = []
        # self.unit_results = []  # List to store search unit_results
        # self.yaml_content = None  # This will hold the content of the loaded YAML file

        # Browse button to fetch VSPEC files
        self.browse_button = tk.Button(root, text="Browse Folder", command=self.browse_folder)
        self.browse_button.pack(pady=10)

        # Label to display the browsed folder path
        self.path_label = tk.Label(root, text="", wraplength=400, anchor="w", justify="left")
        self.path_label.pack(pady=10)

        # Dropdown menu for VSPEC files
        self.file_var = tk.StringVar()
        self.file_dropdown = ttk.Combobox(root, textvariable=self.file_var)
        self.file_dropdown.bind("<<ComboboxSelected>>", self.load_file)

        # Table/treeview for Signal details
        self.tree = ttk.Treeview(root, columns=(
        "Vspec File", "Branch name", "type", "Signal", "datatype", "unit", "min", "max", "default", "allowed",
        "description", "instances", "comment"), show="headings")
        self.tree.heading("Vspec File", text="Vspec File")
        self.tree.heading("Branch name", text="Branch name")
        self.tree.heading("type", text="Type")
        self.tree.heading("Signal", text="Branch/Signal")
        self.tree.heading("datatype", text="Datatype")
        self.tree.heading("unit", text="Unit")
        self.tree.heading("min", text="Min")
        self.tree.heading("max", text="Max")
        self.tree.heading("default", text="Default")
        self.tree.heading("allowed", text="Allowed")
        self.tree.heading("description", text="Description")
        self.tree.heading("instances", text="Instances")
        self.tree.heading("comment", text="Comment")
        self.tree.pack(pady=10)
        self.tree.bind("<Double-1>", self.on_double_click)

        # Buttons to add, delete, and save rows
        self.add_button = tk.Button(root, text="Add Row", command=self.add_row)
        self.add_button.pack(side=tk.LEFT, padx=10)

        self.delete_button = tk.Button(root, text="Delete Row", command=self.delete_row)
        self.delete_button.pack(side=tk.LEFT, padx=10)

        # Frame for Save button and User name entry
        self.save_frame = tk.Frame(root)
        self.save_frame.pack(side=tk.LEFT, padx=10)

        self.save_button = tk.Button(self.save_frame, text="Save to File", command=self.save_to_file)
        self.save_button.pack(side=tk.LEFT, padx=10)

        # User name label and entry
        self.user_label = tk.Label(self.save_frame, text="User name:")
        self.user_label.pack(side=tk.LEFT, padx=(20, 5))

        self.user_entry = tk.Entry(self.save_frame)
        self.user_entry.pack(side=tk.LEFT, padx=5)

        # Define the style for highlighted row
        self.tree.tag_configure('highlighted', background='#FFDDC1')

        # Bind the delete_file_on_exit method to window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # self.load_yaml()  # Load the YAML file when the self starts
        # Initialize the YAML Search self
        # self.yaml_search_app = YamlSearchApp(self.root)
        # self.yaml_search_app.load_yaml()  # Load YAML content
        # self.file_list = [...]  # Initialize with your file list

    # Code to Browse Vspec files from VSS folder/Repo
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
                              f.endswith('.vspec')]
            self.file_var.set('')  # Clear the dropdown selection
            self.file_dropdown['values'] = [os.path.basename(f) for f in self.file_list]

            # Display the selected folder path in the label
            self.path_label.config(text=f"Folder: {folder_path}")
        if folder_path:
            self.file_list = self.get_vspec_files(folder_path)
            if self.file_list:
                self.file_dropdown['values'] = [os.path.basename(f) for f in self.file_list]
                self.file_dropdown.current(0)
                self.load_file(None)
            else:
                messagebox.showerror("Error", "No VSPEC files found in the selected folder and subfolders.")

        vspec_file_path = folder_path + "/VehicleSignalSpecification.vspec"
        yaml_File_path = folder_path + "/units.yaml"
        self.Internal_file = folder_path + "/Donot_Delete_Internal_file.csv"

        # Extract data from the YAML file for dropdown (column index 5)
        self.dropdown_data = []
        if os.path.exists(yaml_File_path):
            with open(yaml_File_path, 'r') as file:
                yaml_content = yaml.safe_load(file)
                for key, value in yaml_content.items():
                    if isinstance(value, dict) and ('description' in value or 'definition' in value):
                        self.dropdown_data.append(key)

        # Add '-' option at the bottom of the dropdown list
        self.dropdown_data.append('-')
        
        # If YAML data is found, proceed with additional setup or else show error
        if not self.dropdown_data:
            messagebox.showerror("Error", "No descriptions or definitions found in the YAML file.")

        sys.argv = [os.path.basename(__file__), "-I", "../spec", "-u", yaml_File_path, vspec_file_path,
                    self.Internal_file]
        vspec2x.main(sys.argv[1:])

        self.load_csv_data(self.Internal_file)
        
    # Code to find the files with extension ".vspec"
    def get_vspec_files(self, folder_path):
        vspec_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.vspec'):
                    vspec_files.append(os.path.join(root, file))
        return vspec_files

    # Code to Load a selected file given in the application to update the Signal/Branch information and display the file information as dropdown
    def load_file(self, event):
        if self.file_dropdown.get():
            selected_file = self.file_dropdown.get()
            self.current_file = next((f for f in self.file_list if os.path.basename(f) == selected_file), None)

    # Code to fetch the branch information for the selected file from Vspec file
    def get_branches_for_file(self, file_name):
        folder_path = self.Internal_file.replace("/Donot_Delete_Internal_file.csv", "")
        for root, dirs, files in os.walk(folder_path):
            if file_name in files:
                file_path = os.path.join(root, file_name)
        # branch_contents = find_branch_content(file_path)
        
        with open(file_path, 'r') as file:
            lines = file.readlines()

            # To store the content above the found "type: branch"
            branch_contents = []

            # Scan through the lines
            for i, line in enumerate(lines):
                stripped_line = line.strip()

                if "type: branch" in stripped_line:
                    content_before = []

                    # Search for content above until we hit a blank line or #
                    for j in range(i - 1, -1, -1):
                        prev_line = lines[j].strip().replace(":", "")  # Remove colons
                        if prev_line == "" or prev_line.startswith("#"):
                            break
                        content_before.insert(0, prev_line)  # Insert at the start to maintain correct order

                    # Store the found content before the branch
                    if content_before:
                        branch_contents.append("\n".join(content_before))      

        return sorted(set(branch_contents))
      
    # def get_branches_for_file(self, file_name):
    #     # Remove ".vspec" from file name
    #     modified_file_name = file_name.replace("vspec", "")

    #     branches = [row['Signal'] for row in self.csv_data if
    #                 row['file_name'] == file_name and row['Type'].lower() == 'branch']
    #     updated_branches = []

    #     for branch in branches:
    #         if modified_file_name in branch:
    #             # Remove the part from the beginning up to the modified file name
    #             updated_branch = branch.split(modified_file_name, 1)[1]
    #             updated_branches.append(updated_branch)
    #         else:
    #             updated_branches.append(branch)

    #     return sorted(set(updated_branches))

    # Code to Add New Row in the application to Add new Signal/Branch into VSPEC files
    def add_row(self):
        # Insert an empty row with highlighted tag
        new_item = self.tree.insert('', 'end', values=("", "", "", "", "", "", "", "", "", "", "", "", "", "", ""), tags=('highlighted',))
        self.on_double_click(None, new_item)  # Trigger cell editing for the new row

    # Code to Delete the Row added in the application 
    def delete_row(self):
        selected_items = self.tree.selection()
        if selected_items:
            for item in selected_items:
                self.tree.delete(item)

    # Code to Save the data into VSPEC files
    def save_to_file(self):
        rows = self.tree.get_children()
        if not rows:
            messagebox.showerror("Error", "No data to save")
            return

        user_name = self.user_entry.get()
        if not user_name:
            messagebox.showerror("Error", "User name is required")
            return

        file_data = {}
        error_messages = []
        incorrect_files = []

        for row_index, row in enumerate(rows, start=1):
            values = self.tree.item(row)['values']

            # Validate Signal name
            if len(values) <= 3 or not values[3]:
                self.tree.tag_configure('empty', background='#FFFF00')
                self.tree.item(row, tags=('empty',))
                error_messages.append(f"Row {row_index}: Branch/Signal name is empty.")

            # Validate Datatype
            if len(values) <= 4 or not values[4]:
                self.tree.tag_configure('empty', background='#FFFF00')
                self.tree.item(row, tags=('empty',))
                error_messages.append(f"Row {row_index}: Data type is empty.")

            # Validate instances for 'branch' type
            if len(values) > 13 and values[2] == 'branch':
                try:
                    if values[13] and values[13] != '-':
                        ast.literal_eval(values[13])  # Try to parse the value as a list
                except (ValueError, SyntaxError):
                    self.tree.tag_configure('invalid_format', background='#FFDDC1')
                    self.tree.item(row, tags=('invalid_format',))
                    error_messages.append(f"Row {row_index}: Instances should be in the format ['X', 'Y'] or empty.")

            # Validate allowed for 'string/string[]' datatype
            if len(values) > 13 and values[2] != 'branch' and (values[4] == 'string' or values[4] == 'string[]'):
                try:
                    if values[9] and values[9] != '-':
                        ast.literal_eval(values[9])  # Try to parse the value as a list
                except (ValueError, SyntaxError):
                    self.tree.tag_configure('invalid_format', background='#FFDDC1')
                    self.tree.item(row, tags=('invalid_format',))
                    error_messages.append(
                        f"""Row {row_index}: Allowed should be in the format "["X", "Y"]" or ['X','Y'] or empty for 'string/string[]' datatype.""")

        # If there are any errors, show them in one error message with row numbers
        if error_messages:
            messagebox.showerror("Error", "\n".join(error_messages))
            return

        # Proceed with saving if no errors
        for row in rows:
            values = self.tree.item(row)['values']
            if len(values) < 4:
                continue

            file_name = values[0]
            branch_name = values[1]
            signal_name = str(values[3])

            if branch_name == "Not-Applicable":
                search_name = signal_name
            else:
                search_name = branch_name + "." + signal_name
            folder_path = self.Internal_file.replace("/Donot_Delete_Internal_file.csv", "")
            # updated_text = self.Internal_file.split("Donot_Delete_Internal_file.csv", 1)[1]
            if signal_name and self.is_duplicate_signal( search_name, file_name):#, folder_path, self.Internal_file):  #search_name, file_name):
                messagebox.showerror("Error",
                                     f"Branch/Signal name '{signal_name}' is already present in file '{os.path.basename(file_name)}'.")
                return

            file_path = next((f for f in self.file_list if os.path.basename(f) == file_name), None)
            # print(len(values))

            if file_path:
                if file_name not in file_data:
                    file_data[file_name] = []
                if len(values) > 13 and values[2] == 'branch' and values[13] and values[13] != '-':
                    file_data[file_name].append(
                        [branch_name, signal_name, values[2], values[13], values[12], values[14]])
                elif len(values) > 13 and values[2] == 'branch' and (not values[13] or values[13] == '-') and not \
                values[14]:
                    file_data[file_name].append([branch_name, signal_name, values[2], values[12]]) 
                elif len(values) > 12 and values[2] != 'branch' and (not values[9] or values[9] == '-'):
                    file_data[file_name].append(
                        [branch_name, signal_name, values[2], values[4], values[5], values[6], values[7], values[8],
                         values[10], values[11], values[12]]) #Condition to validate if data given in "Allowed" column is empty or '-' 
                else:
                    file_data[file_name].append(
                        [branch_name, signal_name, values[2], values[4], values[5], values[6], values[7], values[8],
                         values[9], values[10], values[11], values[12]])
            else:
                incorrect_files.append(file_name)

        for file_name, data in file_data.items():
            file_path = next((f for f in self.file_list if os.path.basename(f) == file_name), None)
            if file_path:
                existing_data = self.load_existing_data(file_path)
                new_data = [values for values in data if values[1] not in existing_data]
                with open(file_path, 'a') as file:
                    for values in new_data:
                        if values[0] == "Not-Applicable":
                            search_name = values[1]
                        else:
                            search_name = values[0] + "." + values[1]

                        if len(values) == 6 and values[2] == 'branch' and values[3] and values[3] != '-':
                            file.write(
                                f"\n{search_name}:\n  type: {values[2]}\n  instances: {values[3]}\n  description: {values[4]}\n  comment: {values[5]}\n  #Above Branch is added by {user_name}\n")
                        elif len(values) == 4 and values[2] == 'branch':
                            file.write(
                                f"\n{search_name}:\n  type: {values[2]}\n  description: {values[3]}\n  #Above Branch is added by {user_name}\n")
                        elif len(values) == 11 and values[2] != 'branch':
                            file.write(
                                f"\n{search_name}:\n  datatype: {values[3]}\n  unit: {values[4]}\n  min: {values[5]}\n  max: {values[6]}\n  type: {values[2]}\n  default: {values[7]}\n  description: {values[8]}\n  #Above Signal is added by {user_name}\n")
                        else:
                            file.write(
                                f"\n{search_name}:\n  datatype: {values[3]}\n  unit: {values[4]}\n  min: {values[5]}\n  max: {values[6]}\n  type: {values[2]}\n  default: {values[7]}\n  allowed: {values[8]}\n  description: {values[11]}\n  #Above Signal is added by {user_name}\n")

        if incorrect_files:
            messagebox.showerror("Error", f" files were not found: {', '.join(incorrect_files)}")
        else:
            messagebox.showinfo("Success", "Data saved successfully")

    # Code to Load the Intermediate file created while using the application
    def load_existing_data(self, file_path):
        existing_data = []
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("\n") or line.startswith(" "):
                    continue
                existing_data.append(line.strip())
        return existing_data

    # def is_duplicate_signal( self, combined_signal, file_name, folder_path, Internal_file_path):
                                
    #             # Open the CSV file and read its contents
    #             with open(Internal_file_path , 'r') as file:
    #                 reader = csv.reader(file)
    #                 header = next(reader)  # Read the header row if present
                    
    #                 # Iterate through each row in the file
    #                 for row in reader:
    #                     # Assuming 'A' column is at index 0 and 'N' column is at index 13 (0-indexed)
    #                     if row[13] == file_name:  # Check if the N column matches the file_name
    #                         if row[0] == combined_signal:  # Check if the A column matches the combined_signal
    #                             return Internal_file_path   # Return the file path if found
    #             return None  # Return None if no match is found
    
    
    # Code to find if Signal provided in the application is present in selected  VSpec file
    def is_duplicate_signal(self, search_name, file_name):
        file_path = next((f for f in self.file_list if os.path.basename(f) == file_name), None)
        if not file_path:
            return None

        with open(file_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            if search_name in line:
                return file_path
        return None

    # def is_duplicate_signal( self, combined_signal, file_name, folder_path, Internal_file_path):
    #     # Iterate over all the files in the app's file list
    #     for Internal_file_path in folder_path:
    #         # Check if the file name matches the provided file_name
    #         if os.path.basename(Internal_file_path ) == "Donot_Delete_Internal_file.csv":
    #             # Open the CSV file and read its contents
    #             with open(Internal_file_path , 'r') as file:
    #                 reader = csv.reader(file)
    #                 header = next(reader)  # Read the header row if present
                    
    #                 # Iterate through each row in the file
    #                 for row in reader:
    #                     # Assuming 'A' column is at index 0 and 'N' column is at index 13 (0-indexed)
    #                     if row[13] == file_name:  # Check if the N column matches the file_name
    #                         if row[0] == combined_signal:  # Check if the A column matches the combined_signal
    #                             return Internal_file_path   # Return the file path if found
    #     return None  # Return None if no match is found

    # Code to Load the Intermediate file created while using the application
    def load_csv_data(self, Internal_file):
        csv_file = Internal_file
        with open(csv_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.csv_data.append(row)   

    # Code to delete the Intermediate file while closing the application
    def on_closing(self):  
            self.delete_file_on_exit()
            self.root.destroy() 
          
    # Code to delete the Intermediate file while using the application     
    def delete_file_on_exit(self):
                if os.path.isfile(self.Internal_file):
                    print(f"File found: {self.Internal_file}")
                    self.file_found = True

                if self.file_found:
                     try:
                         os.remove(self.Internal_file)
                         print(f"Deleted File: {self.Internal_file}")
                     except Exception as e:
                         print(f"Error deleting file: {e}") 
    
    # Code to Edit the Row while Double Clicking on particular cell

    def on_double_click(self, event, item=None):
        if event:
            item = self.tree.identify_row(event.y)
            column = self.tree.identify_column(event.x)
            bbox = self.tree.bbox(item, column)  # Get the bounding box of the cell
            if not bbox:
                return
            x, y, width, height = bbox
        else:
            column = '#1'  # default to the first column if event is None
            bbox = self.tree.bbox(item, column)  # Get the bounding box of the cell
            if not bbox:
                return
            x, y, width, height = bbox

        if not item:
            return

        row_values = self.tree.item(item, "values")
        row_values = list(row_values)  # Convert tuple to list
        column_index = int(column[1:]) - 1

        if column_index < 0 or column_index >= len(row_values):
            return

        # Ensure that 'File' and 'type' columns are filled before allowing editing of other columns
        if column_index > 2 and (not row_values[0] or not row_values[1] or not row_values[2]):
            messagebox.showerror("Error",
                                 "Please fill in the 'File', 'Branch' and 'type' columns before editing other columns.")
            return

        cell_value = row_values[column_index]

        def save_value(new_value):
            row_values[column_index] = new_value
            if column_index == 0:
                row_values[1] = ""  # Clear the Branch name column
            self.tree.item(item, values=row_values)
            option_menu.destroy()

        if column_index == 0:  # Vspec File column
                file_var = tk.StringVar(value=cell_value)
                file_list = [os.path.basename(f) for f in self.file_list]
                option_menu = tk.OptionMenu(self.tree, file_var, *file_list, command=save_value)
                option_menu.place(x=x, y=y, width=width, height=height)
                option_menu.focus_set()
            

        elif column_index == 1:  # Branch name column
                selected_file = self.tree.item(item, 'values')[0]
                # selected_file = os.path.join(folder_path, file_name)
                branch_names = self.get_branches_for_file(selected_file)
                branch_names.append("Not-Applicable")  # Append "Not-Applicable" option
                branch_var = tk.StringVar(value=cell_value)
                option_menu = tk.OptionMenu(self.tree, branch_var, *branch_names, command=save_value)
                option_menu.place(x=x, y=y, width=width, height=height)
                option_menu.focus_set()               

        if column_index == 25:  # Assuming column index 5 is the one where you want the dropdown
            if self.dropdown_data:
                dropdown_var = tk.StringVar(value=cell_value)
                option_menu = tk.OptionMenu(self.tree, dropdown_var, *self.dropdown_data, command=save_value)
                option_menu.place(x=x, y=y, width=width, height=height)
                option_menu.focus_set()
 
        elif column_index == 2:  # type column
                type_var = tk.StringVar(value=cell_value)
                types = ["branch", "attribute", "sensor", "actuator"]
                option_menu = tk.OptionMenu(self.tree, type_var, *types, command=save_value)
                option_menu.place(x=x, y=y, width=width, height=height)
                option_menu.focus_set()

                def save_type_value(new_value):
                    row_values[column_index] = new_value
                    self.tree.item(item, values=row_values)
                    option_menu.destroy()

                    # Set other columns based on type selection
                    if new_value == "branch":
                        for idx in range(4, 12):
                            row_values[idx] = '-'  # Set columns 4 to 12 to '-'
                        for idx in [3, 5, 12, 13, 14]:
                            row_values[idx] = ''  # Ensure '-' is set for these columns if not already set

                    elif new_value == "attribute":
                        for idx in [13, 14]:
                            row_values[idx] = '-'  # Clear "attribute", "sensor", "actuator"
                        for idx in range(4, 12):
                            row_values[idx] = ''  # Set columns 4 to 12 to '-'
                    elif new_value == "sensor":
                        for idx in [13, 14]:
                            row_values[idx] = '-'  # Clear "attribute", "sensor", "actuator"
                        for idx in range(4, 12):
                            row_values[idx] = ''  # Set columns 4 to 12 to '-'
                    elif new_value == "actuator":
                        for idx in [13, 14]:
                            row_values[idx] = '-'  # Clear "attribute", "sensor", "actuator"
                        for idx in range(4, 12):
                            row_values[idx] = ''  # Set columns 4 to 12 to '-'
                    else:
                        for idx in range(4, 14):
                            if row_values[idx] == '-':
                                row_values[idx] = ''  # Clear '-' for columns 4 to 14

                    self.tree.item(item, values=row_values)

                type_var.trace('w', lambda *args: save_type_value(type_var.get()))
            
        else:
                if row_values[2] == "branch":
                    if column_index in [3, 5, 12, 13,
                                        14]:  # Allow editing for 'Signal', 'description', 'instances', 'comment' columns
                        cell_entry = tk.Entry(self.tree, width=width)
                        cell_entry.place(x=x, y=y, width=width, height=height)
                        cell_entry.insert(0, cell_value)
                        cell_entry.focus()

                        def save_entry_value(event):
                            new_value = cell_entry.get()
                            row_values[column_index] = new_value
                            self.tree.item(item, values=row_values)
                            cell_entry.destroy()

                        cell_entry.bind("<Return>", save_entry_value)
                        cell_entry.bind("<FocusOut>", save_entry_value)
                    else:
                        messagebox.showinfo("Info", "This column is not editable for 'branch' type.")
                elif row_values[2] != "branch" and (row_values[4] == "string" or row_values[4] == "string[]"):
                    if column_index == 9:  # 'Allowed' column
                        cell_entry = tk.Entry(self.tree, width=width)
                        cell_entry.place(x=x, y=y, width=width, height=height)
                        cell_entry.insert(0, cell_value)
                        cell_entry.focus()

                        def save_entry_value(event):
                            new_value = cell_entry.get()
                            if new_value == '-' and row_values[4] != "string" and row_values[4] != "string[]":
                                messagebox.showerror("Error",
                                                    "The 'Allowed' column cannot be set to '-' for data types other than 'string' or 'string[]'.")
                                cell_entry.focus()  # Keep focus on the entry
                                return
                            row_values[column_index] = new_value
                            self.tree.item(item, values=row_values)
                            cell_entry.destroy()

                        cell_entry.bind("<Return>", save_entry_value)
                        cell_entry.bind("<FocusOut>", save_entry_value)
                    else:
                        cell_entry = tk.Entry(self.tree, width=width)
                        cell_entry.place(x=x, y=y, width=width, height=height)
                        cell_entry.insert(0, cell_value)
                        cell_entry.focus()

                        def save_entry_value(event):
                            new_value = cell_entry.get()
                            row_values[column_index] = new_value
                            self.tree.item(item, values=row_values)
                            cell_entry.destroy()

                        cell_entry.bind("<Return>", save_entry_value)
                        cell_entry.bind("<FocusOut>", save_entry_value)
                else:
                    if column_index == 4:  # Datatype column
                        cell_entry = tk.Entry(self.tree, width=width)
                        cell_entry.place(x=x, y=y, width=width, height=height)
                        cell_entry.insert(0, cell_value)
                        cell_entry.focus()

                        def save_datatype_value(event):
                            new_value = cell_entry.get()
                            row_values[column_index] = new_value
                            if new_value not in ["string", "string[]"]:
                                row_values[9] = '-'  # Set 'Allowed' column to '-'
                            else:
                                row_values[9] = ''  # Clear '-' in 'Allowed' column
                            self.tree.item(item, values=row_values)
                            cell_entry.destroy()

                        cell_entry.bind("<Return>", save_datatype_value)
                        cell_entry.bind("<FocusOut>", save_datatype_value)

                    else:
                        if column_index == 9:  # 'Allowed' column for other conditions
                            row_values[column_index] = '-'
                            self.tree.item(item, values=row_values)
                        else:
                            cell_entry = tk.Entry(self.tree, width=width)
                            cell_entry.place(x=x, y=y, width=width, height=height)
                            cell_entry.insert(0, cell_value)
                            cell_entry.focus()

                            def save_entry_value(event):
                                new_value = cell_entry.get()
                                row_values[column_index] = new_value
                                self.tree.item(item, values=row_values)
                                cell_entry.destroy()

                            cell_entry.bind("<Return>", save_entry_value)
                            cell_entry.bind("<FocusOut>", save_entry_value)    