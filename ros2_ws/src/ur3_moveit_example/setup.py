from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'ur3_moveit_example'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (
            os.path.join('share', 'ur3_moveit_example', 'urdf'),
            glob('urdf/*')
        ),
        (
            os.path.join('share', 'ur3_moveit_example', 'launch'),
            glob('launch/*.launch.py')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='shadowdk3@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'ur3_move = ur3_moveit_example.ur3_move:main',
            'gripper_pub = ur3_moveit_example.gripper_pub:main',
            'gripper_moveit = ur3_moveit_example.gripper_moveit:main',
        ],
    },
)
