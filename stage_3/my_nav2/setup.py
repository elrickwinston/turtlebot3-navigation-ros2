from setuptools import find_packages, setup

package_name = 'my_nav2'

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
    description='Package to publish navigation goals to Nav2',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'goal_pub = my_nav2.goal_pub:main',
        ],
    },
)
