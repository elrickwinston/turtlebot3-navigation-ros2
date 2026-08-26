from setuptools import find_packages, setup

package_name = 'turtlemover'

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
    description='Examples of using pubsub on turtlesim',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'move_turtle = turtlemover.move_turtle:main',
            'move_turtle_topic = turtlemover.move_turtle_topic:main',
        ],
    },
)
