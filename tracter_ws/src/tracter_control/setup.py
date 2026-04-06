from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'tracter_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'paths'), glob('paths/*.csv')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nontanan',
    maintainer_email='nontanan@gensurv.com',
    description='MPC and GWO control for tractor-trailer system',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mpc_node = tracter_control.mpc_node:main',
            'gwo_tuner_node = tracter_control.gwo_tuner_node:main',
            'path_publisher_node = tracter_control.path_publisher:main',
            'vehicle_node = tracter_control.vehicle_node:main',
        ],
    },
)
