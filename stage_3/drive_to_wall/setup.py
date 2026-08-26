from setuptools import find_packages, setup

package_name = 'drive_to_wall'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Elrick Winston Dsouza',
    maintainer_email='elrickwinston.dsouza@hs-weingarten.de',
    description='Drive turtlebot towards a wall using scan data',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'drive_to_wall_node = drive_to_wall.drive_to_wall_node:main'
        ],
    },
)
