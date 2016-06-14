import ConfigParser
import util

class MPIConfig():
    """
    Configuration for starting a MPI fetch in a multi-node scenario
    """
    MPIRUN        = None
    HOSTS         = None
    HOSTFLAG      = None
    IF_INCLUDE    = None
    ENV           = None
    EXEC          = None
    TEMP_DIR      = None
    ID_MAPPING    = None
    NUM_PROCESSES = None

def initMPIConfig(parser):
    if not parser.has_section("mpi"):
        return
    MPIConfig.MPIRUN        = parser.get('mpi', 'MPIRUN')
    MPIConfig.HOSTS         = parser.get('mpi', 'HOSTS')
    MPIConfig.HOSTFLAG      = parser.get('mpi', 'HOSTFLAG')
    MPIConfig.EXEC          = parser.get('mpi', 'EXECUTABLE')
    MPIConfig.TEMP_DIR      = parser.get('mpi', 'TEMP_DIR')
    MPIConfig.ID_MAPPING    = parser.get('mpi', 'LOADER_JSON')
    MPIConfig.NUM_PROCESSES = parser.get('mpi', 'NUM_PROCESSES')

    if parser.has_option('mpi', 'BTL_TCP_IF_INCLUDE'):
        MPIConfig.IF_INCLUDE = parser.get('mpi', 'BTL_TCP_IF_INCLUDE')
    if parser.has_option('mpi', 'INCLUDE_ENV'):
        MPIConfig.ENV      = parser.get('mpi', 'INCLUDE_ENV')

def initConfig(configFile):
    """
    Initialize the configuration variables from the configFile
    """
    parser = ConfigParser.RawConfigParser()
    parser.read(configFile)

    debug = parser.get('mode', 'DEBUG')
    if debug == 'ON':
        util.DEBUG = True
    else:
        util.DEBUG = False

    initMPIConfig(parser)
