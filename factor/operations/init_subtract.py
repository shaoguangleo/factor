"""
Operation: init_subtract
Implements the initial creation  initial sky model and empty MS by imaging at high resolution  and low resolution and subtracting these from the datasets
"""

from factor.lib.operation import operation
import factor.actions as a

class init_subtract(operation):

    def run(self):

        import logging
        log = logging.getLogger(self.name)

