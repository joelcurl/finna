def is_current_date(key, past_dates, today):
    if key not in past_dates:
        past_dates[key] = today
        return True
    else:
        if past_dates[key] < today:
            past_dates[key] = today
            return True
    return False


