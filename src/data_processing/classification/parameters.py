CATEGORIES = [
    "Food & Drink",
    "Shopping",
    "Beauty & Health",
    "Transport",
    "Restaurant",
    "Other",
]

REGEXP_PATTERNS = {
    "Food & Drink": "sale|prisma|citymarket|k market|s market|k supermarket|kylävalinta|lidl|siwa|alko",
    "Shopping": "power|dressmann|clas ohlson|new yorker|hennes mauritz|kirjakauppa|sokos|tokmanni|verkkokauppa|gigantti|cdon|stadium",
    "Beauty & Health": "apteekki|parturi|specsavers|optikko|instrumentarium|hammas",
    "Transport": "vr|taksi|abc|teboil|neste",
    "Restaurant": "buffa|cafe|kebab|pizza|ravintola|mauno|grilli|food|unica|fazer|restaurant|sodexo|food|kahvi|subway",
}

TRAIN_PROPORTION = 0.75
SHUFFLE = False
DROP_DATA = "../../../configurations/drop_data.json"
OUTPUT_PATH = "../../../configurations/classifier.p"
DATA_PATH = "/data"