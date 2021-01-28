from data_processing.loaders.nordea_loader import NordeaLoader
from data_processing.transformers.nordea_transformer import NordeaTransformer

# Data to be rejected as dict of lists where keys are columns and values are rows
# E.g. DROP_DATA = {'a': ['x', 'y']} rejects all rows that have values 'x' or 'y' in column 'a'
DROP_DATA = {
    'target': ['x', 'y'],
    'event': ['z']
}

# Default dir that will opened when data is loaded
# Current script folder will be used if None
DEFAULT_DATA_DIR = "./test_data"

# Data loader and transformer
# Change these only if you are using custom data set and you need to implement you own data loader and transformer
DATA_LOADER = NordeaLoader()
DATA_TRANSFORMER = NordeaTransformer()
