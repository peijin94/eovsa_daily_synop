
from casatools import msmetadata 
from astropy.time import Time
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
import sunpy.map as smap
from sunpy.coordinates import Helioprojective, propagate_with_solar_surface
from astropy.time import Time
import matplotlib.pyplot as plt
import  numpy as np

from scipy import ndimage
from tqdm import tqdm

def get_N_time_from_ms(msname):
    """
    Get the number of time steps from a measurement set.
    
    Parameters
    ----------
    msname : str
        Path to the measurement set file
        
    Returns
    -------
    int
        Number of time steps
    """
    msmd = msmetadata()
    msmd.open(msname)
    n_times = msmd.timesforfield(0)
    msmd.close()
    return n_times


def get_begin_end_time_from_ms(msname):
    """
    Get the beginning and end times from a measurement set.
    
    Parameters
    ----------
    msname : str
        Path to the measurement set file
        
    Returns
    -------
    tuple
        (begin_time, end_time) as datetime objects
    """
    msmd = msmetadata()
    msmd.open(msname)
    t_range_msmd = msmd.timerangeforobs(0)
    msmd.close()
    
    # Extract MJD values
    begin_mjd = t_range_msmd['begin']['m0']['value']
    end_mjd = t_range_msmd['end']['m0']['value']
    
    # Convert MJD to datetime using astropy Time
    begin_time = Time(begin_mjd, format='mjd').datetime
    end_time = Time(end_mjd, format='mjd').datetime
    
    return begin_time, end_time


def solar_diff_rot_heliofits(in_fits, newtime, out_fits, template_fits=None, showplt=False, overwrite_prev=True):
    """
    Reproject a FITS file to account for solar differential rotation to a new observation time.

    Parameters
    ----------
    in_fits : str
        Path to the input FITS file to be reprojected
    newtime : astropy.time.Time
        The new time to which the map is reprojected
    out_fits : str
        Path for the output FITS file
    template_fits : str, optional
        Path to template FITS file for output. If None, uses in_fits as template
    showplt : bool, optional
        Show plots of the original and reprojected maps, defaults to False

    Returns
    -------
    str
        Path to the output FITS file
    """
    
    # Convert FITS to SunPy Map
    in_map = smap.Map(in_fits)
    
    # Calculate reference time and output time
    reftime = in_map.date + in_map.exposure_time / 2
    out_time = in_map.date - (reftime - Time(newtime))
    
    # Set up output frame
    out_frame = Helioprojective(observer=in_map.observer_coordinate, 
                              obstime=out_time,
                              rsun=in_map.coordinate_frame.rsun)
    
    # Define output center and reference pixel
    out_center = SkyCoord(0 * u.arcsec, 0 * u.arcsec, frame=out_frame)
    out_ref_pixel = [in_map.reference_pixel.x.value, 
                    in_map.reference_pixel.y.value] * in_map.reference_pixel.x.unit
    
    # Create output header
    out_header = smap.make_fitswcs_header(in_map.data.shape,
                                        out_center,
                                        reference_pixel=out_ref_pixel,
                                        scale=u.Quantity(in_map.scale))
    out_wcs = WCS(out_header)
    
    # Perform reprojection
    with propagate_with_solar_surface():
        out_map, footprint = in_map.reproject_to(out_wcs, return_footprint=True)
    
    # Fill missing data from original map
    out_data = out_map.data
    out_data[footprint == 0] = in_map.data[footprint == 0]
    
    # Create new map with reprojected data
    out_map = smap.Map(out_data, out_map.meta)
    out_map.meta['p_angle'] = in_map.meta['p_angle']
    
    # Display plots if requested
    if showplt:
        fig = plt.figure(figsize=(12, 4))

        ax1 = fig.add_subplot(121, projection=in_map)
        in_map.plot(axes=ax1, title='Original map')
        plt.colorbar()

        ax2 = fig.add_subplot(122, projection=out_map)
        out_map.plot(axes=ax2,
                    title=f"Reprojected to an Earth observer {(Time(newtime) - reftime).to('day')} later")
        plt.colorbar()
        plt.show()
    
    # Save to FITS file using template if provided
    if template_fits is None:
        template_fits = in_fits
        
    # Load template header
    template_map = smap.Map(template_fits)
    template_header = template_map.meta.copy()
    
    # Update necessary header information
    template_header.update({
        'DATE-OBS': out_map.date.iso,
        'DATE': out_map.date.iso,
        'CRVAL1': out_map.reference_coordinate.Tx.value,
        'CRVAL2': out_map.reference_coordinate.Ty.value,
        'CRPIX1': out_map.reference_pixel.x.value,
        'CRPIX2': out_map.reference_pixel.y.value,
        'PC1_1': out_map.rotation_matrix[0,0],
        'PC1_2': out_map.rotation_matrix[0,1],
        'PC2_1': out_map.rotation_matrix[1,0],
        'PC2_2': out_map.rotation_matrix[1,1]
    })
    
    # Create new map with template header and save to FITS
    final_map = smap.Map(out_data, template_header)
    final_map.save(out_fits,  overwrite=overwrite_prev)
    
    return out_fits



def rotateimage(data, xc_centre, yc_centre, p_angle):
    """
    Rotate an image around a specified point (xc_centre, yc_centre) by a given angle.

    :param data: The image data.
    :type data: numpy.ndarray
    :param xc_centre: The x-coordinate of the rotation center.
    :type xc_centre: int
    :param yc_centre: The y-coordinate of the rotation center.
    :type yc_centre: int
    :param p_angle: The rotation angle in degrees.
    :type p_angle: float
    :return: The rotated image.
    :rtype: numpy.ndarray
    """

    padX = [data.shape[1] - xc_centre, xc_centre]
    padY = [data.shape[0] - yc_centre, yc_centre]
    imgP = np.pad(data, [padY, padX], 'constant')
    imgR = ndimage.rotate(imgP, p_angle, reshape=False, order=0, prefilter=False)
    return imgR[padY[0]:-padY[1], padX[0]:-padX[1]]



def sunpyfits_to_j2000fits(in_fits, out_fits, template_fits=None, overwrite_prev=True):
    """
    Rotate a solar FITS file from helioprojective to RA-DEC coordinates and save to a new FITS file.

    Parameters
    ----------
    in_fits : str
        Path to input FITS file in helioprojective coordinates
    out_fits : str
        Path for output FITS file in RA-DEC coordinates
    template_fits : str, optional
        Path to template FITS file for output format. If None, uses in_fits as template
    overwrite_prev : bool, optional
        If True, overwrites existing output file. Defaults to True

    Returns
    -------
    str
        Path to the output FITS file
    """
    import astropy.units as u
    from astropy.io import fits
    
    # Load input map
    in_map = smap.Map(in_fits)
    p_ang = in_map.meta['p_angle'] * u.deg
    
    # Get reference pixel coordinates
    ref_x = int(in_map.reference_pixel.x.value)
    ref_y = int(in_map.reference_pixel.y.value)
    
    # Perform rotation
    data_rot = rotateimage(in_map.data, ref_x, ref_y, -p_ang.to('deg').value)
    
    # Use template if provided, otherwise use input file
    if template_fits is None:
        template_fits = in_fits
        
    # Read template header
    with fits.open(template_fits) as hdul:
        template_header = hdul[0].header.copy()
    
    # Update necessary header information
    template_header.update({
        'DATE-OBS': in_map.date.iso,
        'DATE': in_map.date.iso,
        'CRVAL1': in_map.reference_coordinate.Tx.value,
        'CRVAL2': in_map.reference_coordinate.Ty.value,
        'CRPIX1': ref_x,
        'CRPIX2': ref_y,
        'PC1_1': in_map.rotation_matrix[0,0],
        'PC1_2': in_map.rotation_matrix[0,1],
        'PC2_1': in_map.rotation_matrix[1,0],
        'PC2_2': in_map.rotation_matrix[1,1],
        'P_ANGLE': p_ang.to('deg').value
    })
    
    # Create and write output FITS file
    hdu = fits.PrimaryHDU(data_rot, header=template_header)
    hdu.writeto(out_fits, overwrite=overwrite_prev)
    
    return out_fits