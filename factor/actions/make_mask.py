"""
Action: make_mask
Make a mask using PyBDSM from a given image
"""

from factor.lib.action import action

class make_mask(action):
    """
    Implment the make_mask action
    """

    def __init__(self, op_name, image, threshpix = None, threshisl = None, rms_box = (55,12), adaptive_rms_box = False, rms_box_bright = None, atrous_do = False, clean=True):
        super(make_mask, self).__init__(op_name, name = 'make_mask')
        self.ms = ms
        self.image = image

    def run(self):
        # TODO: implement the template
        template_imager = make_template(ms = self.ms, imagename = self.imagename, \
                                niter = self.niter, imsize = self.imsize, cell = self.cell, uvrange = self.uvrange, mask = self.mask)
        cmd = 'casapy --nologger --log2term -c %s' % template_imager


    def get_results(self):
        """
        Return mask name
        """
        return self.mask
