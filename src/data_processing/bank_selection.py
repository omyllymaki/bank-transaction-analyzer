from src.data_processing.loaders.nordea_loader import NordeaLoader
from src.data_processing.transformers.nordea_transformer import NordeaTransformer


class UnsupportedBankOption(Exception):
    pass


class Bank:
    def __init__(self, loader, transformer):
        self.loader = loader
        self.transformer = transformer


def get_bank(bank: str):
    if bank == "Nordea":
        return Bank(loader=NordeaLoader(), transformer=NordeaTransformer())
    else:
        raise UnsupportedBankOption("Unsupported bank option selected")
