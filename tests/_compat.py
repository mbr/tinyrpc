# from http://stackoverflow.com/questions/28215214/how-to-add-custom-renames-in-six

import six
mod = six.MovedModule('mock', 'mock', 'unittest.mock')
six.add_move(mod)
six._importer._add_module(mod, "moves." + mod.name)

# issue open at https://bitbucket.org/gutworth/six/issue/116/enable-importing-from-within-custom
