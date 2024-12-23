from casatasks import flagdata
from casatools import table, msmetadata
import numpy as np

def flag_keep_antennas(vis, keep_antennas=range(13)):
    """
    Flag all antennas except the specified ones in the measurement set.
    
    Parameters:
    -----------
    vis : str
        Input measurement set filename
    keep_antennas : list or range
        List of antenna numbers to keep (default: 0-12)
    """
    # Initialize tools
    msmd = msmetadata()
    
    try:
        # Open the measurement set
        msmd.open(vis)
        
        # Get all antenna IDs
        all_antennas = msmd.antennaids()
        
        # Convert keep_antennas to list if it's a range
        keep_list = list(keep_antennas)
        
        # Find antennas to flag (all except those we want to keep)
        flag_list = [ant for ant in all_antennas if ant not in keep_list]
        
        if not flag_list:
            print("No antennas to flag!")
            return
            
        # Convert antenna list to string format required by flagdata
        flag_string = ','.join(map(str, flag_list))
        
        print(f"Flagging antennas: {flag_string}")
        print(f"Keeping antennas: {','.join(map(str, keep_list))}")
        
        # Run flagdata
        flagdata(vis=vis,
                mode='manual',
                antenna=flag_string,
                flagbackup=True,
                action='apply')
                
        print("Flagging complete!")
        
    except Exception as e:
        print(f"Error during flagging: {str(e)}")
        
    finally:
        # Clean up
        msmd.done()

if __name__ == "__main__":
    # Input measurement set
    ms_file = "UDB20241215.ms"  # Replace with your MS filename
    
    # Run flagging to keep antennas 0-12
    flag_keep_antennas(ms_file)
    
    # If you want to specify a different range, you can do:
    # flag_keep_antennas(ms_file, keep_antennas=range(0,13))  # 0-12
    # or specific antennas:
    # flag_keep_antennas(ms_file, keep_antennas=[0,1,2,3,4,5,6,7,8,9,10,11,12])