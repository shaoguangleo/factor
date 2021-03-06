import os
from lofarpipe.support.data_map import DataMap, DataProduct


def plugin_main(args, **kwargs):
    """
    Makes a multi-mapfile for list of files

    Parameters
    ----------
    files : str
        Nested list of files given as a string. The sub-lists _must_ be separated by the string "], ["
        '[[file1a, file1b, file1c], [file2a, file2b]]'
    hosts : str
        List of hosts/nodes. May be given as a list or as a string (e.g.,
        '[host1, host2]'
    mapfile_dir : str
        Directory for output mapfile
    filename: str
        Name of output mapfile

    Returns
    -------
    result : dict
        Output datamap filename

    """
    if type(kwargs['files']) is str:
        tmplist = kwargs['files'].strip('[]').split('], [')
        files = []
        for filestring in tmplist:
            fileslist = filestring.split(',')
            files.append([f.strip(' \'') for f in fileslist])
    else:
        print 'PipelineStep_addListMultiMapfile.py kwargs[\'files\'] is not a string!'
        raise ValueError('PipelineStep_addListMultiMapfile.py kwargs[\'files\'] is not a string!')
    if type(kwargs['hosts']) is str:
        hosts = kwargs['hosts'].strip('[]').split(',')
        hosts = [h.strip() for h in hosts]
    mapfile_dir = kwargs['mapfile_dir']
    filename = kwargs['filename']

    for i in range(len(files)-len(hosts)):
        hosts.append(hosts[i])

    map_out = MultiDataMap([])
    for h, f in zip(hosts, files):
        map_out.data.append(MultiDataProduct(h, f, False))

    fileid = os.path.join(mapfile_dir, filename)
    map_out.save(fileid)
    result = {'mapfile': fileid}

    return result


class MultiDataProduct(DataProduct):
    """
    Class representing multiple files in a DataProduct.
    """
    def __init__(self, host=None, file=None, skip=True):
        super(MultiDataProduct, self).__init__(host, file, skip)
        if not file:
            self.file = list()
        else:
            self._set_file(file)

    def __repr__(self):
        """Represent an instance as a Python dict"""
        return (
            "{{'host': '{0}', 'file': '{1}', 'skip': {2}}}".format(self.host,
                '[{}]'.format(','.join(self.file)), str(self.skip))
        )

    def __str__(self):
        """Print an instance as 'host:[filelist]'"""
        return ':'.join((self.host, str(self.file)))

    def _set_file(self, data):
        try:
            # Try parsing as a list
            if isinstance(data, list):
                self.file = data
            if isinstance(data, DataProduct):
                self._from_dataproduct(data)
            if isinstance(data, DataMap):
                self._from_datamap(data)

        except TypeError:
            raise DataProduct("No known method to set a filelist from %s" % str(file))

    def _from_dataproduct(self, prod):
        print 'setting filelist from DataProduct'
        self.host = prod.host
        self.file = prod.file
        self.skip = prod.skip

    def _from_datamap(self, inmap):
        print 'setting filelist from DataMap'
        filelist = {}
        for item in inmap:
            if not item.host in filelist:
                filelist[item.host] = []
            filelist[item.host].append(item.file)
        self.file = filelist['i am']

    def append(self, item):
        self.file.append(item)


class MultiDataMap(DataMap):
    """
    Class representing a specialization of data-map, a collection of data
    products located on the same node, skippable as a set and individually
    """
    def __init__(self, data=list(), iterator=iter):
        super(MultiDataMap, self).__init__(data, iterator)

    @classmethod
    def load(cls, filename):
        """Load a data map from file `filename`. Return a DataMap instance."""
        with open(filename) as f:
            datamap = eval(f.read())
            for i, d in enumerate(datamap):
                file_entry = d['file']
                if file_entry.startswith('[') and file_entry.endswith(']'):
                    file_list = [e.strip(' \'\"') for e in file_entry.strip('[]').split(',')]
                    datamap[i] = {'host': d['host'], 'file': file_list, 'skip': d['skip']}
            return cls(datamap)

    @DataMap.data.setter
    def data(self, data):
        if isinstance(data, DataMap):
            mdpdict = {}
            data.iterator = DataMap.SkipIterator
            for item in data:
                if not item.host in mdpdict:
                    mdpdict[item.host] = []
                mdpdict[item.host].append(item.file)
            mdplist = []
            for k, v in mdpdict.iteritems():
                mdplist.append(MultiDataProduct(k, v, False))
            self._set_data(mdplist, dtype=MultiDataProduct)
        elif isinstance(data, MultiDataProduct):
            self._set_data(data, dtype=MultiDataProduct)
        elif not data:
            pass
        else:
            self._set_data(data, dtype=MultiDataProduct)

    def split_list(self, number):
        mdplist = []
        for item in self.data:
            for i in xrange(0, len(item.file), number):
                chunk = item.file[i:i+number]
                mdplist.append(MultiDataProduct(item.host, chunk, item.skip))
        self._set_data(mdplist)

