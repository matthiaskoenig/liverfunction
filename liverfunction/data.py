"""
Helpers for loading and working with data.
"""
import pandas as pd
from IPython.display import display

def load_data(fid, sep="\t", show=True, data_dir=".", extension="csv"):
    """ Loads data from given figure/table id.
    Displays the first rows of the dataframe by default.
    """
    if fid.endswith(".csv") or fid.endswith(".tsv"):
        pass
    else:
        fid = '{}.{}'.format(fid, extension)
    df = pd.read_csv(os.path.join(data_dir, fid), sep=sep, comment="#")
    if show is True:
        display(df.head())
        print(fid)
    return df


