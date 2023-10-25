import csv
import pandas as pd
import chardet
from superagi.lib.logger import logger

def correct_csv_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']

    if encoding != 'utf-8':
        data = []
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=',', quotechar='"')
            for row in reader:
                try:
                    data.append(row)
                except Exception as e:
                    logger.error(f"An error occurred while processing the file: {e}")
                    continue

        df = pd.DataFrame(data)
        df.to_csv(file_path, encoding='utf-8', index=False)
        logger.info("File is converted to utf-8 encoding.")
    else:
        logger.info("File is already in utf-8 encoding.")