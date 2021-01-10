# Data to be rejected as dict of lists where keys are columns and values are rows
# E.g. DROP_DATA = {'a': ['x', 'y']} rejects all rows that have values 'x' or 'y' in column 'a'
DROP_DATA = {
    'target': ['x', 'y'],
    'event': ['z']
}

# Default dir that will opened when data is loaded
# Current script folder will be used if None
DEFAULT_DATA_DIR = None

# Map of indicators that we want to follow
# Key is indicator name
# Value is regexp pattern used to filter all the events with matching criteria
INDICATORS = {
    "VR": "vr",
    "Store": "sale|prisma|citymarket|k market|s market|k supermarket|kylävalinta|lidl",
    "All": ".*"
}
