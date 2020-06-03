import numpy as np
import os
import h5py

def combine_data_files(files, filename):
    """ Create an HDF5 file object and add links to all given files

    Parameters
    ----------
    files : str
        path to files
    filename : str
        name of the combined file
    """

    # Sort in ascending order:
    fnum = [int(fname.split(".")[-2]) for fname in files]
    sorting = np.argsort(fnum)
    files = files[sorting]

    # Create the file object with links to all the files:
    with h5py.File(filename,'a') as f:

        # Iterate through data files and add missing links:
        for i,filename in enumerate(files):
            # Make an external link:
            if not 'link{}'.format(i) in f:
                f['link{}'.format(i)] = \
                        h5py.ExternalLink(filename,'/')

def get_data_path(data_category, simID, snapID):
    """ Constructs the path to data directory. 
    
    Paramaters
    ----------
    data_category : str
        recognized values are: 'part' and 'group'

    Returns
    -------
    path : str
        path to data directory
    """

    home = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(home,"snapshots",simID)

    prefix = ""
    if data_category == "part":
        prefix = "snapshot_"
    else:
        prefix += "groups_"

    # Find the snapshot directory and add to path:
    for dirname in os.listdir(path):
        if prefix + str(snapID) in dirname:
            path = os.path.join(path,dirname) 

    return path
