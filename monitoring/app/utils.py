from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from io import BytesIO


def get_excel_io(data):
    book = Workbook()
    book.active = 0
    sheet = book.active
    sheet.title = "тест"
    buffer = BytesIO()
    book.save(buffer)
    buffer.seek(0)
    return buffer


def calculate_points(result, min_r, max_r, koef_min, koef_top, reverse):
    if (not reverse and min_r > max_r) or (reverse and min_r < max_r):
      max_r, min_r = min_r, max_r
    if min_r == max_r:
      return 0
    price = 100 / (max_r - min_r)
    shift = 0
    if (not reverse and result > max_r) or (reverse and result < max_r):
        shift = result - max_r
        result = max_r

    rating = (result - min_r) / (max_r - min_r) * 10 * koef_min + shift * price * koef_top
    return max(round(rating, 2), 0)

