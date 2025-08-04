# Open points/Issues  
While updating .vspec files in *VSPEC File Manager*:
1. After updating new attribute/sensor/actuator signals to vspec files, if *VSS_GUI* window is used to search the new signal it couldn’t be found due to incompatible/supported information of the signal. Due to this tool can get closed abnormally when path is browsed without any error notification.
2. While browsing the path in any of the applications if the tool gets terminated, it could be due to newly updated signal information in one of the vspec files.
3. *VSS_GUI* window must be configured with dynamic re-sizing according to the dimensions of screen. 
4. In *VSPEC File Manager* format verification of *Allowed* column must be with respect to provided datatype. It is yet to be implemented.
5. *VSS_GUI* and *VSPEC File Manager* windows cannot be closed once opened without providing the spec folder path, as tool will search for the path to delete the internal file created. So, the windows can be closed only after providing some path.
6. Alternative: Close the log window and then try closing the tool windows hassle free closure.
7. The dropdown option for unit in the *VSPEC File Manager* is currently not fully functional, as it does not allow scrolling through the list.
