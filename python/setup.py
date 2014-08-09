from setuptools import setup, find_packages

from griffinmcelroy.version import get_version_string

ALL_PACKAGES=find_packages()

setup(
    name='griffinmcelroy',
    version=get_version_string(),
    description='your sweet baby brother griffin',
    author='jonathan',
    author_email='jonathan.dye@sungard.com',
    license='Rights Reserved',
    packages=ALL_PACKAGES,
    provides=ALL_PACKAGES,
    include_package_data=True,

    # plugins
    entry_points = {
        'griffinmcelroy.gatherers': [
            'vcenter = griffinmcelroy.gatherer.plugins.vcenter:VCenterGathererPlugin',
            'isr9024 = griffinmcelroy.gatherer.plugins.voltaire:ISR9024GathererPlugin',
            'procurve = griffinmcelroy.gatherer.plugins.procurve:ProcurveGathererPlugin',
        ],
    },

    # dependencies
    setup_requires=(
        'setuptools==5.4.2',
    ),
    install_requires=(
        'config==0.3.9',
        'pyvmomi==5.5.0',
        'pyzmq==14.3.1',
        'requests==2.3.0',
        'SQLAlchemy==0.9.7',
        'psycopg2==2.5.3',
        'paramiko==1.14.0',
    ),
    tests_require=(
        'nose==1.3.3',
        'coverage==3.7.1',
    ),
)