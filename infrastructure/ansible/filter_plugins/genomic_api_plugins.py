from jinja2.runtime import Undefined
import ansible.runner.filter_plugins.core as core


def well_defined(var):
    if isinstance(var, Undefined) or var is None:
        return False
    else:
        return True


def is_defined_true(var):
    if(not well_defined(var)):
        return False
    return core.bool(var)


def get_defined_string(var):
    if(not well_defined(var)):
        return ''
    return str(var)


class FilterModule(object):
    ''' Ansible additional jinja2 filters for Genomics API'''

    def filters(self):
        return {
            "well_defined": well_defined,
            "is_defined_true": is_defined_true,
            "get_defined_string": get_defined_string
        }
