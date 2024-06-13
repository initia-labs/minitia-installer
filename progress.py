from rich.progress import Progress, TextColumn, SpinnerColumn, BarColumn, TimeRemainingColumn

def setup_progress(task_description: str, total: int, show_percentage: bool = True, show_time_remaining: bool = True):
    """
    Set up a progress tracker with customizable options.

    Args:
    task_description (str): Description of the task.
    total (int): Total steps to complete the task.
    show_percentage (bool): Whether to show the percentage completed.
    show_time_remaining (bool): Whether to show the estimated time remaining.

    Returns:
    tuple: A tuple containing the Progress object and the task ID.
    """
    columns = [
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}")
    ]
    
    if show_percentage:
        columns.append(BarColumn())
    
    if show_time_remaining:
        columns.append(TimeRemainingColumn())

    try:
        with Progress(*columns) as progress:
            task = progress.add_task(f"[cyan]{task_description}...", total=total)
            return progress, task
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None