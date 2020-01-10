'''
sweeps package analysis tools for generated data
Uses `pandas` library for DataFrames

Created: November 2019
'''

import pandas as pd
import numpy as np
import os
import json
import warnings


def remove_non_rfs(sim_loc, directory_list):
    """Remove files not corresponding to rfs directories from a directory list.

    Keyword arguments:
    sim_loc -- location of where sweeps was run and ./rfs/ folder is located
    directory_list -- the list variable of all pathis in the rfs directory
    """
    for rf in directory_list:
        if not os.path.isdir(os.path.join(sim_loc, 'rfs', rf)):
            # rf is not a directory -> remove it:
            directory_list.remove(rf)

            # Print a message if this file isn't hidden:
            if rf[0] != '.':    # Check if file is a hidden system file
                print('!! File', rf, 'in rfs directory is not a run folder. '
                      'It has been removed from directory_list.')


def get_DataFrame(
        sim_loc: str, ID_hashes=None,
        col_headers=None) -> pd.core.frame.DataFrame:
    """Extract and return a pandas DataFrame from a directory of run folders.

    Keyword arguments:
    sim_loc -- location of where sweeps was run and ./rfs/ folder is located
    ID_hashes -- a list of particular run IDs wanted to construct a data frame
    col_headers -- a list of custom column headers for the DataFrame
    """
    IDs = os.listdir(os.path.join(sim_loc, 'rfs'))

    # Remove non-directories from IDs:
    remove_non_rfs(sim_loc, IDs)

    # If requested, use custom list of IDs:
    if ID_hashes is not None:
        assert ID_hashes.issubset(IDs), ("Invalid ID_hashes list; Some "
                                         "requested run IDs in ID_hashes are "
                                         "not in the list of found IDS.")
        for rf in IDs:
            if rf not in ID_hashes:
                IDs.remove(rf)

    num_IDs = len(IDs)
    params = [dict() for x in range(num_IDs)]
    for i in range(num_IDs):
        with open(os.path.join(sim_loc, 'rfs', IDs[i], 'params.json')) as par:
            params[i] = json.load(par)   # Get JSON dict from parameter file

    df = pd.DataFrame(params, index=IDs) if col_headers is None \
        else pd.DataFrame(params, index=IDs, columns=col_headers)
    return df


def get_data(ID: str, sim_loc: str):
    """Return data extracted from a saved file in a particular run folder.

    Keyword arguments:
    ID -- hash / folder name of desired run
    sim_loc -- location of where sweeps was run and ./rfs/ folder is located
    """
    directory_list = os.listdir(os.path.join(sim_loc, 'rfs', ID))
    directory_list = [e for e in directory_list if e not in (
        'log.txt', 'params.json', 'status.txt')]
    for filename in directory_list:
        if filename[0] == '.':
            # Hidden file - exclude from search
            directory_list.remove(filename)
            break
        filepath = os.path.join(sim_loc, 'rfs', ID, filename)
        if filename[-5:] == '.hdf5':
            # HDF5 file
            import h5py
            with h5py.File(filepath, 'r') as f:
                print("Keys: %s" % f.keys())    # List all groups
                return f
        elif filename[-4:] == '.mat':
            # Matlab matrix file
            import scipy.io
            return scipy.io.loadmat(filepath)
        elif filename[-5:] == '.json' and filename != 'params.json':
            with open(filepath) as data_file:
                return json.load(data_file)
        elif filename[-5:] == '.bson':
            # Binary JSON file
            import bson     # bson neds to be installed: pip install bson
            with open(filepath) as bson_file:
                return bson.loads(bson_file.read())
        elif filename[-4:] == '.npz':
            # Numpy npz file
            return np.load(filepath)
        elif filename[-5:] == '.pklz':
            # pickle file
            import pickle
            import gzip
            with gzip.open(filepath) as f:
                return pickle.load(f)
        elif filename[-4:] == '.jld' or filename[-5:] == '.jld2':
            # Julia JLD or JLD2 file, which uses HDF5 encoding
            # Return an appropriate numpy matrix if
            import h5py
            with h5py.File(filepath, 'r') as f:
                keys = f.keys()
                return(
                    f if len(keys) > 1
                    else np.transpose(np.array(f.get(list(keys)[0])))
                    # Note: Julia stores data in column major order, as opposed
                    # to row major used by numpy, so to read matrices this way
                    # they are transposed.
                )
    if directory_list:  # (if directory_list is not empty)
        warnings.warn("No recognized data type recognized; returning a file:")
        with open(os.path.join(sim_loc, 'rfs', ID, directory_list[0])) as file:
            return file
    else:
        raise IOError('No data files found for given run folder.')
