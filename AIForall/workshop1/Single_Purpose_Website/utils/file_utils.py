from datetime import datetime
import os

def generate_filename(file_format: str) -> str:
    """
    Generate filename with date format.
    
    Args:
        file_format: 'pdf' or 'docx'
    
    Returns:
        Filename in format: contract_YYYY-MM-DD.pdf or contract_YYYY-MM-DD.docx
    """
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    if file_format.lower() == 'pdf':
        return f"contract_{date_str}.pdf"
    elif file_format.lower() == 'docx':
        return f"contract_{date_str}.docx"
    else:
        return f"contract_{date_str}.{file_format}"

def cleanup_old_files(directory: str, max_age_hours: int = 24):
    """
    Clean up old files from directory.
    
    Args:
        directory: Path to directory
        max_age_hours: Maximum age of files in hours
    """
    if not os.path.exists(directory):
        return
    
    from datetime import timedelta
    now = datetime.now()
    max_age = timedelta(hours=max_age_hours)
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        if os.path.isfile(filepath):
            file_age = now - datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if file_age > max_age:
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error removing file {filepath}: {e}")
