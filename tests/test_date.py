import locale
from datetime import datetime
from locale import LC_ALL
from time import strptime

import locate
from dateutil.parser import parser



def convert_date_flexible(date_str, output_format="%d.%m.%Y %H:%M"):
    month = {"янв": "01", "фев": "02", "мар": "03", "апр": "04", "май": "05", "июн": "06", "июл": "07", "авг": "08", "сен": "09", "окт": "10", "ноя": "11", "дек": "12"}
    input_formats = [
        "%d/%m/%Y",  # Пример: "20/01/2025"
        "%d-%m-%Y",  # Пример: "20-01-2025"
        "%Y.%m.%d",  # Пример: "2025.01.20"
        "%B %d, %Y",  # Пример: "January 20, 2025"
        "%d %B %Y",  # Пример: "20 января 2025"
        "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 с временной зоной
        "%Y-%m-%dT%H:%M:%S",  # ISO 8601 без временной зоны
        "%d %B %Y, %H:%M",  # Пример: "20 января 2025, 17:26"
        "%Y-%m-%d %H:%M:%S",  # Пример: "2025-01-20 17:26:00"
        "%d.%m.%Y %H:%M",  # Пример: "20.01.2025 17:26"
        "%Y/%m/%d %H:%M",  # Пример: "2025/01/20 17:26"
    ]


    if "янв" in date_str:
        _date = date_str.split()
        month_numb = month[_date[1][:3]] if _date[1][:3] in month else None
        if month_numb:
            _date[2] = _date[2].replace(",", "")

            if len(_date) == 3:
                return f"{_date[0]}.{month_numb}.{_date[2]}"
            return f"{_date[0]}.{month_numb}.{_date[2]} {_date[3]}"

    if len(date_str) == 5:
        current_date = datetime.now().strftime(output_format)[:-6]
        return f'{current_date} {date_str}'

    for fmt in input_formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime(output_format)
        except ValueError:
            continue

    raise date_str


# Пример использования
dates = [
    "21:52",
    "20 января 2025, 17:26",
    "20 янв 2025, 17:26",
    "2025-01-20 17:26:00",
    "20.01.2025 17:26",
    "20/01/2025",
    "20-01-2025",
    "2025.01.20",
    "20 января 2025"
]

for date in dates:
    try:
        print(f"Исходная: {date} -> Преобразованная: {convert_date_flexible(date)}")
    except ValueError as e:
        print(e)
