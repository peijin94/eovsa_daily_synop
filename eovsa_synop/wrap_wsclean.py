import subprocess
from typing import List, Optional, Union

class WSClean:
    def __init__(self, vis: str):
        """
        Initialize WSClean wrapper
        
        Parameters:
        -----------
        vis : str
            Input measurement set path
        """
        self.vis = vis
        self.params = {
            'size': [1024, 1024],        # default size
            'scale': "2.5asec",          # default pixel scale
            'weight_briggs': 0.0,        # default Briggs robust
            'niter': 0,                  # default no cleaning
            'mgain': 1.0,                # default mgain
            'data_column': "DATA",       # default data column
            'name': "wsclean",           # default output name
            'multiscale': False,         # default no multiscale
            'local_rms': False,          # default no local rms
            'no_update_model': False,    # default update model
            'no_negative': False         # default allow negative
        }

    def setup(self, **kwargs):
        """
        Set WSClean parameters
        
        Parameters:
        -----------
        size : int or list, optional
            Image size in pixels [width, height] or single value for square
        scale : str, optional
            Pixel scale (e.g., "2.5asec")
        weight_briggs : float, optional
            Briggs robust parameter
        niter : int, optional
            Number of clean iterations
        mgain : float, optional
            Major cycle gain
        data_column : str, optional
            Data column to image
        name : str, optional
            Output name prefix
        multiscale : bool, optional
            Enable multiscale clean
        auto_mask : float, optional
            Auto-masking threshold
        auto_threshold : float, optional
            Auto threshold value
        local_rms : bool, optional
            Enable local RMS
        no_update_model : bool, optional
            Disable model data updates
        intervals_out : int, optional
            Number of time intervals
        spws : list or str, optional
            Spectral windows to image
        pol : str, optional
            Polarization to image
        no_negative : bool, optional
            Prevent negative components
        """
        # Handle size parameter specially
        if 'size' in kwargs:
            size = kwargs['size']
            if isinstance(size, (int, float)):
                self.params['size'] = [int(size), int(size)]
            else:
                self.params['size'] = [int(size[0]), int(size[1])]
            
        # Update all other parameters
        for key, value in kwargs.items():
            if key != 'size':
                self.params[key] = value
        
        return self

    def build_command(self) -> str:
        """Build wsclean command"""
        cmd = ['wsclean']
        
        # Add basic parameters
        cmd.extend(['-size', str(self.params['size'][0]), str(self.params['size'][1])])
        cmd.extend(['-scale', self.params['scale']])
        cmd.extend(['-weight', 'briggs', str(self.params['weight_briggs'])])
        
        if self.params['niter'] > 0:
            cmd.extend(['-niter', str(self.params['niter'])])
            
        if self.params['multiscale']:
            cmd.append('-multiscale')
            
        if self.params['mgain'] != 1.0:
            cmd.extend(['-mgain', str(self.params['mgain'])])
            
        if 'pol' in self.params:
            cmd.extend(['-pol', self.params['pol']])
            
        if 'auto_mask' in self.params:
            cmd.extend(['-auto-mask', str(self.params['auto_mask'])])
            
        if 'auto_threshold' in self.params:
            cmd.extend(['-auto-threshold', str(self.params['auto_threshold'])])
            
        if self.params['local_rms']:
            cmd.append('-local-rms')
            
        if self.params['no_update_model']:
            cmd.append('-no-update-model-required')
            
        if self.params['no_negative']:
            cmd.append('-no-negative')
            
        if 'intervals_out' in self.params:
            cmd.extend(['-intervals-out', str(self.params['intervals_out'])])

        if self.params['quiet']:
            cmd.append('-quiet')

        if 'spws' in self.params:
            spws = self.params['spws']
            if isinstance(spws, list):
                spws = ','.join(map(str, spws))
            cmd.extend(['-spws', spws])

        cmd.extend(['-name', self.params['name']])
        cmd.append(self.vis)
        
        return ' '.join(cmd)
    
    def run(self, dryrun: bool = False) -> int:
        """
        Run wsclean command
        
        Parameters:
        -----------
        dryrun : bool, optional
            If True, only print the command without executing
            
        Returns:
        --------
        int
            Return code from wsclean execution
        """
        cmd = self.build_command()
        
        if dryrun:
            print(f"Would run: {cmd}")
            return 0
            
        print(f"Running: {cmd}")
        process = subprocess.run(cmd, shell=True)
        return process.returncode

# Example usage:
if __name__ == "__main__":
    wsclean = WSClean("UDB20241215.ms")
    
    # Configure all parameters in one call
    wsclean.setup(
        size=1024,
        scale="2.5asec",
        weight_briggs=0.0,
        niter=1000,
        multiscale=True,
        mgain=0.8,
        data_column="DATA",
        pol="xx",
        auto_mask=7,
        auto_threshold=2,
        local_rms=True,
        no_update_model=True,
        no_negative=True,
        spws=[4,5,6,7,8,9],
        intervals_out=4,
        name="eovsa"
    )
    
    # Run WSClean (with dryrun=True to just print the command)
    wsclean.run(dryrun=True)