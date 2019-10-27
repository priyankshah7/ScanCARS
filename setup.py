from distutils.core import setup
from Cython.Build import cythonize

setup(
    # ext_modules=cythonize(["scancars/sdk/andor/pyandor.pyx"]),
    name='scancars',
    version='0.0.1',
    packages=[
        'scancars',
        'scancars.threads',
        'scancars.sdk',
        'scancars.sdk.andor',
        'scancars.utils',
        'scancars.gui',
        'scancars.gui.css',
        'scancars.gui.forms'
    ]
)
