from pathlib import Path

from setuptools import find_packages, setup

README = (Path(__file__).parent / "README.md").read_text()

setup(
    name="pyskindose",
    version="22.2.2",
    description=(
        "Tools and script for calculating peak skin dose and create dose maps for fluoroscopic exams from RDSR" " data"
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://dev.azure.com/Sjukhusfysiker/PySkinDose",
    author="Max Hellström",
    author_email="max.hellstrom@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas",
        "numpy",
        "pydicom>=2.0",
        "numpy-stl",
        "plotly>=4.13.3",
        "scipy",
        "tqdm",
        "psutil",
        "pillow >= 8.1.1",
        "kaleido",
    ],
    include_package_data=True,
    zip_safe=False,
)
