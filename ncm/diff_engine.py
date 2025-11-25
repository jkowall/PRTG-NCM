import difflib

def compare_configs(old_config, new_config):
    """
    Compares two configuration strings and returns an HTML diff.
    """
    if old_config is None:
        old_config = ""
    if new_config is None:
        new_config = ""
        
    old_lines = old_config.splitlines()
    new_lines = new_config.splitlines()
    
    diff = difflib.HtmlDiff(wrapcolumn=80).make_file(
        old_lines, new_lines, 
        fromdesc="Previous Config", 
        todesc="New Config",
        context=True, 
        numlines=3
    )
    return diff
