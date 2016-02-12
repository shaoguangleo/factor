"""
Module that holds all operations for outlier sources

The outlier calibration steps are divided into operations on the basis of whether
or not they can be run in parallel or in series.

Classes
-------
OutlierPeel : Operation
    Runs the calibration for peeling an outlier source. May be run in parallel
OutlierSub : Operation
    Subtracts outlier sources from data. Must be run in series as writes are
    made to original datasets

"""
import os
import ast
from factor.lib.operation import Operation
from lofarpipe.support.data_map import DataMap


class OutlierPeel(Operation):
    """
    Operation to peel a direction
    """
    def __init__(self, parset, bands, direction):
        super(OutlierPeel, self).__init__(parset, bands, direction,
            name='OutlierPeel')

        # Define extra parameters needed for this operation (beyond those
        # defined in the master Operation class and as attributes of the
        # direction object)
        ms_files = [band.file for band in self.bands]
        skymodels = [band.skymodel_dirindep for band in self.bands]
        dir_indep_parmdbs = [band.dirindparmdb for band in self.bands]
        self.parms_dict.update({'ms_files': ms_files,
                                'skymodels': skymodels,
                                'dir_indep_parmdbs': dir_indep_parmdbs})


    def finalize(self):
        """
        Finalize this operation
        """
        # Add output datamaps to direction object for later reference
        self.direction.input_bands_mapfile = os.path.join(self.pipeline_mapfile_dir,
            'input_bands.mapfile')
        self.direction.subtracted_data_mapfile = os.path.join(self.pipeline_mapfile_dir,
            'add_all_facet_sources.mapfile')

        # Store results of verify_subtract check. This will work if the verification
        # was done using multiple bands although we use only one at the moment
        if os.path.exists(self.direction.verify_subtract_mapfile) and not self.parset['skip_selfcal_check']:
            ok_mapfile = DataMap.load(self.direction.verify_subtract_mapfile)
            ok_flags = [ast.literal_eval(item.file) for item in ok_mapfile]
            if all(ok_flags):
                self.direction.selfcal_ok = True
            else:
                self.direction.selfcal_ok = False
        elif self.parset['skip_selfcal_check']:
            self.direction.selfcal_ok = True
        else:
            self.direction.selfcal_ok = False

        # Delete temp data
        self.direction.cleanup_mapfiles = [
            os.path.join(self.pipeline_mapfile_dir, 'corrupt_outlier_model.mapfile'),
            os.path.join(self.pipeline_mapfile_dir, 'shift_and_average.mapfile'),
            os.path.join(self.pipeline_mapfile_dir, 'concat_data.mapfile'),
            os.path.join(self.pipeline_mapfile_dir, 'concat_blavg_data.mapfile'),
            os.path.join(self.pipeline_mapfile_dir, 'chunk_files.mapfile'),
            os.path.join(self.pipeline_mapfile_dir, 'predict_outlier_model.mapfile')]
        self.log.debug('Cleaning up files (direction: {})'.format(self.direction.name))
        self.direction.cleanup()


class OutlierSub(Operation):
    """
    Operation to subtract improved model
    """
    def __init__(self, parset, bands, direction):
        super(OutlierSub, self).__init__(parset, bands, direction,
            name='OutlierSub')

        # Delete temp data
        self.direction.cleanup_mapfiles = [self.direction.subtracted_data_mapfile]
        self.log.debug('Cleaning up files (direction: {})'.format(self.direction.name))
        self.direction.cleanup()
