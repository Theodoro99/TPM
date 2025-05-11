from datetime import datetime

def format_date(date_obj):
    """Format a datetime object to a readable string format.
    
    Args:
        date_obj: A datetime object to format
        
    Returns:
        A formatted string in the format 'DD-MM-YYYY HH:MM'
    """
    if not date_obj:
        return ""
    
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj)
        except ValueError:
            return date_obj
    
    return date_obj.strftime("%d-%m-%Y %H:%M")
