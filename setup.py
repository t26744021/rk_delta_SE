from setuptools import setup, find_packages

with open ("docs\\English_README.md","r",encoding="utf-8") as f :  #pypi introduce
    description = f.read()

setup(
    name="rk_delta_SE",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
 
 
    ],
    long_description=description,
    long_description_content_type="text/markdown"
)


