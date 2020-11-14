
from enum import Enum

# vasily_currencybot
token = '1410387700:AAFcWJw8YHTvoh5oBLhJyE8O5lAHwclvvd4'

#'1204975875:AAEMu946PZhuCbAY-MZP34UPtzsbZTE2qKQ'
db_file = 'database.vdb'


class States(Enum):
    S_START = "0"
    S_FIND_QUOTE = "1"
    S_CONVERT = "2"
