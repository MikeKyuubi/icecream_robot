from setuptools import setup
import os
from glob import glob

package_name = 'icecream_statemachine'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
        (os.path.join('share', package_name, 'worlds'),
            glob('worlds/*.world')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@example.com',
    description='Ice Cream State Machine + Mock Hardware Nodes',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'state_machine   = icecream_statemachine.state_machine_node:main',
            'mock_cobot      = icecream_statemachine.mock_cobot_node:main',
            'mock_icecream   = icecream_statemachine.mock_icecream_node:main',
            'mock_dispenser  = icecream_statemachine.mock_dispenser_node:main',
            'cobot           = icecream_statemachine.cobot_node:main',
            'cobot_teleop    = icecream_statemachine.cobot_teleop:main',
        ],
    },
)
