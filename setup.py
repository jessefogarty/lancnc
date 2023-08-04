from setuptools import setup, find_packages

setup(
    name='lancnc',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'asyncssh',
        'pydantic',
        'rich',
        'cryptography',
    ],
    entry_points={
        'console_scripts': [
            'lancnc = cli:main',
        ],
    },
    author='Your Name',
    author_email='youremail@example.com',
    description='LanCNC: Manage and execute commands on remote hosts using SSH',
    url='https://github.com/username/lancnc',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

