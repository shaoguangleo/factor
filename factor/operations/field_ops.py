"""
Module that holds all field (non-facet-specific) operations

Classes
-------
InitSubtract : Operation
    Images each band at high and low resolution to make and subtract sky models
MakeMosaic : Operation
    Makes a mosaic from the facet images

"""
import os
from factor.lib.operation import Operation


class InitSubtract(Operation):
    """
    Operation to create empty datasets
    """
    def __init__(self, parset, bands, reset=False):
        super(InitSubtract, self).__init__(parset, bands, direction=None,
            reset=reset, name='InitSubtract')


    def run_steps(self):
        """
        Run the steps for this operation
        """
        from factor.actions.images import MakeImage
        from factor.actions.models import MakeSkymodelFromModelImage, MergeSkymodels
        from factor.actions.calibrations import Subtract, FFT
        from factor.actions.visibilities import Average
        from factor.lib.datamap_lib import read_mapfile
#         from factor.operations.hardcoded_param import init_subtract as p
        from factor.operations.hardcoded_param import init_subtract_test as p
        self.log.warn('Using test parameters')

        bands = self.bands

        # Check operation state
        if os.path.exists(self.statebasename+'.done'):
            merged_skymodels_mapfile = os.path.join(self.parset['dir_working'],
                'datamaps/InitSubtract/MergeSkymodels/merge_output.datamap')
            skymodels, _ = read_mapfile(merged_skymodels_mapfile)
            for band, skymodel in zip(bands, skymodels):
                band.skymodel_dirindep = skymodel
            return

        # Make initial data maps for the empty datasets and their dir-indep
        # instrument parmdbs
        subtracted_all_mapfile = self.write_mapfile([band.file for band in bands],
        	prefix='subtracted_all')
        dir_indep_parmdbs_mapfile = self.write_mapfile([band.dirindparmdb for band
        	in bands], prefix='dir_indep_parmdbs')

        self.log.info('High-res imaging...')
        action = MakeImage(self.parset, subtracted_all_mapfile, p['imagerh'],
            prefix='highres')
        highres_image_basenames_mapfile = action.run()

        if self.parset['use_ftw']:
            self.log.debug('FFTing high-res model image...')
            action = FFT(self.parset, subtracted_all_mapfile,
                highres_image_basenames_mapfile, p['modelh'], prefix='highres')
            action.run()
            highres_skymodels_mapfile = None

        self.log.info('Making high-res sky model...')
        action = MakeSkymodelFromModelImage(self.parset,
            highres_image_basenames_mapfile, p['modelh'], prefix='highres')
        highres_skymodels_mapfile = action.run()

        self.log.info('Subtracting high-res sky model...')
        action = Subtract(self.parset, subtracted_all_mapfile, p['calibh'],
            model_datamap=highres_skymodels_mapfile,
            parmdb_datamap=dir_indep_parmdbs_mapfile, prefix='highres')
        action.run()

        self.log.info('Averaging...')
        action = Average(self.parset, subtracted_all_mapfile, p['avgl'],
            prefix='highres')
        avg_files_mapfile = action.run()

        self.log.info('Low-res imaging...')
        action = MakeImage(self.parset, avg_files_mapfile, p['imagerl'],
            prefix='lowres')
        lowres_image_basenames_mapfile = action.run()

        if self.parset['use_ftw']:
            self.log.debug('FFTing low-res model image...')
            action = FFT(self.parset, subtracted_all_mapfile,
                lowres_image_basenames_mapfile, p['modell'], prefix='lowres')
            action.run()

        self.log.info('Making low-res sky model...')
        action = MakeSkymodelFromModelImage(self.parset, lowres_image_basenames_mapfile,
            p['modell'], prefix='lowres')
        lowres_skymodels_mapfile = action.run()

        self.log.info('Subtracting low-res sky model...')
        action = Subtract(self.parset, subtracted_all_mapfile, p['calibl'],
            model_datamap=lowres_skymodels_mapfile,
            parmdb_datamap=dir_indep_parmdbs_mapfile, prefix='lowres')
        action.run()

        self.log.info('Merging low- and high-res sky models...')
        action = MergeSkymodels(self.parset, lowres_skymodels_mapfile,
            highres_skymodels_mapfile, p['merge'], prefix='merge')
        merged_skymodels_mapfile = action.run()
        skymodels, _ = read_mapfile(merged_skymodels_mapfile)
        for band, skymodel in zip(bands, skymodels):
            band.skymodel_dirindep = skymodel


class MakeMosaic(Operation):
    """
    Operation to mosiac facet images
    """
    def __init__(self, parset, bands, direction=None, reset=False):
        super(MakeMosaic, self).__init__(parset, bands, direction=direction,
            reset=reset, name='MakeMosaic')


    def run_steps(self):
        """
        Run the steps for this operation
        """
        pass
