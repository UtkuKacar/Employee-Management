# core/scripts/date_utils.py
import datetime
from django.conf import settings

def is_holiday(date):

    #Verilen tarihin tatil günü olup olmadığını kontrol eder.
    day_name = date.strftime("%A")  # Günün adını alır (ör. "Saturday")
    return day_name in settings.HOLIDAYS
