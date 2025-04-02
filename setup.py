from setuptools import setup, find_packages

setup(
    name='pdf-converter',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'PyQt5==5.15.7',
        'PyPDF2==3.0.1'
    ],
    entry_points={
        'console_scripts': [
            'pdf-converter=gui:main',
        ],
    },
    author='Your Name',
    description='A PDF to DXF converter',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
