import os
from casatools import table

def merge_split_scans(base_ms_name):
    """
    Merge previously split measurement sets back into a single MS file.
    
    Parameters:
    -----------
    base_ms_name : str
        Base name of the original measurement set (without .ms extension)
        The function will look for files matching pattern: base_name_scanX.ms
    """
    # Initialize table tool
    tb = table()
    
    try:
        # Get list of all split MS files in the current directory
        all_files = os.listdir('.')
        split_files = [f for f in all_files if f.startswith(base_ms_name) and 
                      '_scan' in f and f.endswith('.ms')]
        
        if not split_files:
            print(f"No split scan files found for {base_ms_name}")
            return
            
        # Sort files to ensure consistent ordering
        split_files.sort()
        print(f"Found {len(split_files)} split scan files to merge")
        
        # Define output merged MS name
        merged_ms = f"{base_ms_name}_merged.ms"
        
        if os.path.exists(merged_ms):
            print(f"Output file {merged_ms} already exists. Please remove it first.")
            return
            
        # Use the first file as the base and append others to it
        print(f"Using {split_files[0]} as base file")
        os.system(f"cp -r {split_files[0]} {merged_ms}")
        
        # Open the merged MS
        tb.open(merged_ms, nomodify=False)
        
        # Append each remaining file
        for ms_file in split_files[1:]:
            print(f"Appending {ms_file}")
            
            # Open the MS file to append
            tb_append = table(ms_file)
            
            # Add rows from this MS to the merged MS
            tb.addrows(tb_append.nrows())
            
            # Copy data from the append MS to the merged MS
            for colname in tb.colnames():
                try:
                    col_data = tb_append.getcol(colname)
                    tb.putcol(colname, col_data, startrow=tb.nrows() - tb_append.nrows())
                except Exception as e:
                    print(f"Warning: Error copying column {colname}: {str(e)}")
            
            # Close the append MS
            tb_append.close()
            
        print(f"Successfully created merged MS: {merged_ms}")
        
    except Exception as e:
        print(f"Error merging measurement sets: {str(e)}")
        
    finally:
        # Clean up
        tb.close()

# Example usage:
base_name = "UDB20241212"  # Without .ms extension
merge_split_scans(base_name)