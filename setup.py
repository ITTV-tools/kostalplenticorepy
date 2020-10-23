import setuptools

setuptools.setup(
    name="kostalplenticore",
    version="0.3",
    author="ittv-tools",
    description="API call to Kostal Plenticore",
    url="https://github.com/ITTV-tools/kostalplenticorepy",
    py_modules=["kostalplenticore"],
    package_dir={'': 'src'},
    install_requires=['pycryptodome'],
    classifieres=[
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9"
    ]

)
