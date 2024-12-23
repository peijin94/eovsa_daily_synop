import os
from casatools import table, msmetadata

def split_ms_by_scan(msfile):
    """
    Split a measurement set file into multiple files, one per scan.
    
    Parameters:
    -----------
    msfile : str
        Input measurement set filename
    """
    # Initialize tools
    tb = table()
    msmd = msmetadata()
    
    try:
        # Open the measurement set
        msmd.open(msfile)
        
        # Get list of scan numbers
        scan_numbers = msmd.scannumbers()
        print(f"Found {len(scan_numbers)} scans in {msfile}")
        
        # Create output directory if it doesn't exist
        base_name = os.path.splitext(msfile)[0]
        
        # Process each scan
        for scan in scan_numbers:
            # Define output filename
            outfile = f"{base_name}_scan{scan}.ms"
            
            # Skip if output file already exists
            if os.path.exists(outfile):
                print(f"Skipping scan {scan}, output file {outfile} already exists")
                continue
                
            print(f"Processing scan {scan}")
            
            # Create table query for the scan
            query = f"SCAN_NUMBER == {scan}"
            
            # Split the MS for this scan
            tb.open(msfile)
            subtb = tb.query(query)
            
            # Copy the subtable to new MS
            subtb.copy(outfile, deep=True)
            
            # Clean up
            subtb.close()
            tb.close()
            
            print(f"Created {outfile}")
            
    except Exception as e:
        print(f"Error processing measurement set: {str(e)}")
        
    finally:
        # Clean up
        msmd.close()
        tb.close()

ms_file = "UDB20241212.ms"

    # Run the splitting function
split_ms_by_scan(ms_file)