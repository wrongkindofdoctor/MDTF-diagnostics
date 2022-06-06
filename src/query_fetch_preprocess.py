import abc
import collections
import glob
import intake_esm
import os
import pandas as pd
from src import util


FileGlobTuple = collections.namedtuple(
    'FileGlobTuple', 'name glob attrs'
)
FileGlobTuple.__doc__ = """
    Class representing one file glob pattern. *attrs* is a dict containing the
    data catalog values that will be associated with all files found using *glob*.
    *name* is used for logging only.
"""


class AbstractQueryMixin(abc.ABC):
    @abc.abstractmethod
    def query_dataset(self, var):
        """Sets *data* attribute on var or raises an exception."""
        pass

    def setup_query(self):
        """Called once, before the iterative :meth:`~DataSourceBase.request_data` process starts.
        Use to, eg, initialize database or remote filesystem connections.
        """
        pass

    def pre_query_hook(self, vars):
        """Called before querying the presence of a new batch of variables."""
        pass

    def set_experiment(self):
        """Called after querying the presence of a new batch of variables, to
        filter or otherwise ensure that the returned DataKeys for *all*
        variables comes from the same experimental run of the model, by setting
        the *status* attribute of those DataKeys to ACTIVE."""
        pass

    def post_query_hook(self, vars):
        """Called after select_experiment(), after each query of a new batch of
        variables."""
        pass

    def tear_down_query(self):
        """Called once, after the iterative :meth:`~DataSourceBase.request_data` process ends.
        Use to, eg, close database or remote filesystem connections.
        """
        pass


class AbstractFetchMixin(abc.ABC):
    @abc.abstractmethod
    def fetch_dataset(self, var, data_key):
        """Fetches data corresponding to *data_key*. Populates its *local_data*
        attribute with a list of identifiers for successfully fetched data
        (paths to locally downloaded copies of data).
        """
        pass

    def setup_fetch(self):
        """Called once, before the iterative :meth:`~DataSourceBase.request_data` process starts.
        Use to, eg, initialize database or remote filesystem connections.
        """
        pass

    def pre_fetch_hook(self, vars):
        """Called before fetching each batch of query results."""
        pass

    def post_fetch_hook(self, vars):
        """Called after fetching each batch of query results."""
        pass

    def tear_down_fetch(self):
        """Called once, after the iterative :meth:`~DataSourceBase.request_data` process ends.
        Use to, eg, close database or remote filesystem connections.
        """
        pass


class AbstractDataSource(AbstractQueryMixin, AbstractFetchMixin,
                         metaclass=util.MDTFABCMeta):
    @abc.abstractmethod
    def __init__(self, case_dict, parent):
        # sets signature of __init__ method
        pass

    def pre_query_and_fetch_hook(self):
        """Called once, before the iterative :meth:`~DataSourceBase.request_data` process starts.
        Use to, eg, initialize database or remote filesystem connections.
        """
        # call methods if we're using mixins; if not, child classes will override
        if hasattr(self, 'setup_query'):
            self.setup_query()
        if hasattr(self, 'setup_fetch'):
            self.setup_fetch()

    def post_query_and_fetch_hook(self):
        """Called once, after the iterative :meth:`~DataSourceBase.request_data` process ends.
        Use to, eg, close database or remote filesystem connections.
        """
        # call methods if we're using mixins; if not, child classes will override
        if hasattr(self, 'tear_down_query'):
            self.tear_down_query()
        if hasattr(self, 'tear_down_fetch'):

            self.tear_down_fetch()


class OnTheFlyFilesystemQueryMixin(metaclass=util.MDTFABCMeta):
    """Mixin that creates an intake_esm.esm_datastore catalog by using a regex
    (\_FileRegexClass) to query the existence of data files on a remote
    filesystem.

    For the purposes of this class, all data attributes are inferred only from
    filea nd directory naming conventions: the contents of the files are not
    examined (i.e., the data files are not read from) until they are fetched to
    a local filesystem.

    .. note::
       At time of writing, the `filename parsing
       <https://www.anaconda.com/blog/intake-parsing-data-from-filenames-and-paths>`__
       functionality included in `intake
       <https://intake.readthedocs.io/en/latest/index.html>`__ is too limited to
       correctly parse our use cases, which is why we use the
       :class:`~src.util.RegexPattern` class instead.
    """
    # root directory to begin crawling at:
    CATALOG_DIR = util.abstract_attribute()
    # regex to use to generate catalog entries from relative paths:
    _FileRegexClass = util.abstract_attribute()
    _asset_file_format = "netcdf"

    @property
    def df(self):
        assert (hasattr(self, 'catalog') and hasattr(self.catalog, 'df'))
        return self.catalog.df

    @property
    def remote_data_col(self):
        """Name of the column in the catalog containing the path to the remote
        data file.
        """
        return self._FileRegexClass._pattern.input_field

    def _dummy_esmcol_spec(self):
        """Dummy specification dict that enables us to use intake_esm's
        machinery. The catalog is temporary and not retained after the code
        finishes running.
        """
        data_cols = list(self._FileRegexClass._pattern.fields)
        data_cols.remove(self.remote_data_col)
        # no aggregations, since for now we want to manually insert logic for
        # file fetching (& error handling etc.) before we load an xarray Dataset.
        return {
            "esmcat_version": "0.1.0",
            "id": "MDTF_" + self.__class__.__name__,
            "description": "",
            "attributes": [
                {"column_name":c, "vocabulary": ""} for c in data_cols
            ],
            "assets": {
                "column_name": self.remote_data_col,
                "format": self._asset_file_format
            },
            "last_updated": "2020-12-06"
        }

    @abc.abstractmethod
    def generate_catalog(self):
        """Method (to be implemented by child classes) which returns the data
        catalog as a Pandas DataFrame. One of the columns of the DataFrame must
        have the name returned by :meth:`remote_data_col` and contain paths to
        the files.
        """
        pass

    def setup_query(self):
        """Generate an intake_esm catalog of files found in CATALOG_DIR.
        Attributes of files listed in the catalog (columns of the DataFrame) are
        taken from the match groups (fields) of the class's \_FileRegexClass.
        """
        self.log.info('Starting data file search at %s:', self.CATALOG_DIR)
        self.catalog = intake_esm.core.esm_datastore.from_df(
            self.generate_catalog(),
            esmcol_data=self._dummy_esmcol_spec(),
            progressbar=False, sep='|'
        )


class OnTheFlyDirectoryHierarchyQueryMixin(
    OnTheFlyFilesystemQueryMixin, metaclass=util.MDTFABCMeta
):
    """Mixin that creates an intake_esm.esm_datastore catalog on-the-fly by
    crawling a directory hierarchy and populating catalog entry attributes
    by running a regex (\_FileRegexClass) against the paths of files in the
    directory hierarchy.
    """
    # optional regex to speed up directory crawl to skip non-matching directories
    # without examining all files; default below is to not skip any directories
    _DirectoryRegex = util.RegexPattern(".*")

    def iter_files(self):
        """Generator that yields instances of \_FileRegexClass generated from
        relative paths of files in CATALOG_DIR. Only paths that match the regex
        in \_FileRegexClass are returned.
        """
        # in case CATALOG_DIR is subset of CASE_ROOT_DIR
        path_offset = len(os.path.join(self.attrs.CASE_ROOT_DIR, ""))
        for root, _, files in os.walk(self.CATALOG_DIR):
            try:
                self._DirectoryRegex.match(root[path_offset:])
            except util.RegexParseError:
                continue
            if not self._DirectoryRegex.is_matched:
                continue
            for f in files:
                if f.startswith('.'):
                    continue
                try:
                    path = os.path.join(root, f)
                    yield self._FileRegexClass.from_string(path, path_offset)
                except util.RegexSuppressedError:
                    # decided to silently ignore this file
                    continue
                except Exception:
                    self.log.info("  Couldn't parse path '%s'.", path[path_offset:])
                    continue

    def generate_catalog(self):
        """Crawl the directory hierarchy via :meth:`iter_files` and return the
        set of found files as rows in a Pandas DataFrame.
        """
        # DataFrame constructor must be passed list, not just an iterable
        df = pd.DataFrame(list(self.iter_files()), dtype='object')
        if len(df) == 0:
            self.log.critical('Directory crawl did not find any files.')
            raise AssertionError('Directory crawl did not find any files.')
        else:
            self.log.info("Directory crawl found %d files.", len(df))
        return df


class OnTheFlyGlobQueryMixin(
    OnTheFlyFilesystemQueryMixin, metaclass=util.MDTFABCMeta
):
    """Mixin that creates an intake_esm.esm_datastore catalog on-the-fly by
    searching for files with (python's implementation of) the shell
    :py:mod:`glob` syntax.

    We still invoke \_FileRegexClass to parse the paths, but the expected use
    case is that this will be the trivial regex (matching everything, with no
    labeled match groups), since the file selection logic is being handled by
    the globs. If you know your data is stored according to some relevant
    structure, you should use :class:`OnTheFlyDirectoryHierarchyQueryMixin`
    instead.
    """
    @abc.abstractmethod
    def iter_globs(self):
        """Iterator returning :class:`FileGlobTuple` instances. The generated
        catalog contains the union of the files found by each of the globs.
        """
        pass

    def iter_files(self, path_glob):
        """Generator that yields instances of \_FileRegexClass generated from
        relative paths of files in CATALOG_DIR. Only paths that match the regex
        in \_FileRegexClass are returned.
        """
        path_offset = len(os.path.join(self.attrs.CASE_ROOT_DIR, ""))
        if not os.path.isabs(path_glob):
            path_glob = os.path.join(self.CATALOG_DIR, path_glob)
        for path in glob.iglob(path_glob, recursive=True):
            yield self._FileRegexClass.from_string(path, path_offset)

    def generate_catalog(self):
        """Build the catalog from the files returned from the set of globs
        provided by :meth:`rel_path_globs`.
        """
        catalog_df = pd.DataFrame(dtype='object')
        for glob_tuple in self.iter_globs():
            # DataFrame constructor must be passed list, not just an iterable
            df = pd.DataFrame(
                list(self.iter_files(glob_tuple.glob)),
                dtype='object'
            )
            if len(df) == 0:
                self.log.critical("No files found for '%s' with pattern '%s'.",
                                  glob_tuple.name, glob_tuple.glob)
                raise AssertionError((f"No files found for '{glob_tuple.name}' "
                                      f"with pattern '{glob_tuple.glob}'."))
            else:
                self.log.info("%d files found for '%s'.", len(df), glob_tuple.name)

            # add catalog attributes specific to this set of files
            for k, v in glob_tuple.attrs.items():
                df[k] = v
            catalog_df = catalog_df.append(df)
        # need to fix repeated indices from .append()ing
        return catalog_df.reset_index(drop=True)


class LocalFetchMixin(AbstractFetchMixin):
    """Mixin implementing data fetch for files on a locally mounted filesystem.
    No data is transferred; we assume that xarray can open the paths directly.
    Paths are unaltered and set as variable's *local_data*.
    """
    def fetch_dataset(self, var, d_key):
        paths = d_key.remote_data()
        if isinstance(paths, pd.Series):
            paths = paths.to_list()
        if not util.is_iterable(paths):
            paths = (paths, )
        for path in paths:
            if not os.path.exists(path):
                raise util.DataFetchEvent((f"Fetch {d_key} ({var.full_name}): "
                                           f"File not found at {path}."), var)
            else:
                self.log.debug("Fetch %s: found %s.", d_key, path)
        d_key.local_data = paths
