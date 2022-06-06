"""
Base classes implementing logic for querying, fetching and preprocessing
model data requested by the PODs for multirun mode
(i.e., a single POD is associated with multiple data sources)
"""

from src import util, data_manager, diagnostic, core, preprocessor
import collections
import logging

_log = logging.getLogger(__name__)


# METHOD RESOLUTION ORDER (MRO): What order will classes inherit in MultirunDataSourceBase
# (and other classes with multiple base classes)?
# Python3 uses C3 linearization algorithm (https://en.wikipedia.org/wiki/C3_linearization):
# L[C] = C + merge of linearization of parents of C and list of parents of C
# in the order they are inherited from left to right.
# super() returns proxy objects: objects with the ability to dispatch to methods of other objects via delegation.
# Technically, super is a class overriding the __getattribute__ method.
# Instances of super are proxy objects providing access to the methods in the MRO.
# General format is:
# super(cls, instance-or-subclass).method(*args, **kw)
# You can get the MRO of a class by running print(class.mro())



# --------------------------------------------------------------------------

# MRO: [<class '__main__.MultirunDataframeQueryDataSourceBase'>
# <class '__main__.MultirunDataSourceBase'>
# <class 'src.data_manager.DataframeQueryDataSourceBase'>
# <class 'src.data_manager.DataSourceBase'>
# <class 'src.core.MDTFObjectBase'>
# <class 'src.util.logs.CaseLoggerMixin'>
# <class 'src.util.logs._CaseAndPODHandlerMixin'>
# <class 'src.util.logs.MDTFObjectLoggerMixinBase'>
# <class 'src.data_manager.AbstractDataSource'>
# <class 'src.data_manager.AbstractQueryMixin'>
# <class 'src.data_manager.AbstractFetchMixin'>
# <class 'abc.ABC'>
# <class 'object'>]


# defining attributes using dc.field default_factory means that all instances have a default type
# This also ensures that the same attribute object is not reused each time it is called
# Therefore, you can modify individual values in one dc.field instance without propagating the
# changes to other object instances
#class MultirunVarlist(diagnostic.Varlist):
    # contents: dc.InitVar = util.MANDATORY # fields inherited from data_model.DMDataSet
    # vars: list = dc.field(init=False, default_factory=list)
    # coord_bounds: list = dc.field(init=False, default_factory=list)
    # aux_coords: list = dc.field(init=False, default_factory=list)
 #   pass

#class MultirunDiagnostic(diagnostic.Diagnostic):
    # _id = util.MDTF_ID()           # fields inherited from core.MDTFObjectBase
    # name: str
    # _parent: object
    # log = util.MDTFObjectLogger
    # status: ObjectStatus
    # long_name: str = ""  # fields inherited from diagnostic.diagnostic
    # description: str = ""
    # convention: str = "CF"
    # realm: str = ""
    # driver: str = ""
    # program: str = ""
    # runtime_requirements: dict = dc.field(default_factory=dict)
    # pod_env_vars: util.ConsistentDict = dc.field(default_factory=util.ConsistentDict)
    # log_file: io.IOBase = dc.field(default=None, init=False)
    # nc_largefile: bool = False
    # varlist: Varlist = None
    # preprocessor: typing.Any = dc.field(default=None, compare=False)
    # POD_CODE_DIR = ""
    # POD_OBS_DATA = ""
    # POD_WK_DIR = ""
    # POD_OUT_DIR = ""
    # _deactivation_log_level = logging.ERROR
    #  _interpreters = {'.py': 'python', '.ncl': 'ncl', '.R': 'Rscript'}
    #varlist = MultirunVarlist = None


   # @property
    #def _log_name(self):
        # POD loggers sit in a subtree of the DataSource logger distinct from
        # the DataKey loggers; the two subtrees are distinguished by class name
    #    _log_name = f"{self.name}_{self._id}".replace('.', '_')
    #    return f"{self._parent._log_name}.{self.__class__.__name__}.{_log_name}"



#if __name__ == "__main__":
#    print(MultirunVarlistEntry.mro())