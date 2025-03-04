import os
import sys

def get_resource_path(relative_path):
    """ Get the absolute path to a resource file. """
    if getattr(sys, 'frozen', False):
        # The application is frozen (running as an executable)
        base_path = os.path.dirname(sys.executable)
    else:
        # The application is not frozen (running in development)
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
