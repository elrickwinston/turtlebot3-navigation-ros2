from setuptools import find_packages, setup

package_name = 'catch_a_turtle'

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
    description='Catch a turtle using pubsub and services',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turtle_runner = catch_a_turtle.turtle_runner:main',
            'catch_a_turtle = catch_a_turtle.catch_a_turtle:main',
        ],
    },
)
