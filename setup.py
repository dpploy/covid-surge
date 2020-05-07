import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="covid-surge",
    version="0.0.0",
    author="Valmor F. de Almeida",
    author_email="valmor_dealmeida@uml.edu",
    description="Covid-Surge is a utility for computing and comparing surge periods\
            of communities afflicted by the COVID-19 virus pandemic.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github/dpploy/covid-surge",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Topic :: Scientific/Engineering :: Mathematics',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Topic :: Education',
        'Topic :: Utilities'
    ],
    python_requires='>=3.6',
)
