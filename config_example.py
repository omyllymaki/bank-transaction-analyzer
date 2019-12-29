# Data to be rejected as dict of lists where keys are columns and values are rows
# E.g. DROP_DATA = {'a': ['x', 'y']} rejects all rows that have values 'x' or 'y' in column 'a'
DROP_DATA = {
    'Saaja/Maksaja': ['x','y'],
    'Tapahtuma': ['z']
}

# Default dir that will opened when data is loaded
# Current script folder will be used if None
DEFAULT_DATA_DIR = None