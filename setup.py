import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask-ngrokpy",
    version="1.0.0",
    author="Jak Bin",
    description="A simple way to demo Flask apps from your machine.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jakbin/flask-ngrokpy",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords='flask,flask-ngrok,flask-ngrokpy,port-forwarding',
    install_requires=['Flask>=0.14.0', 'requests'],
    py_modules=['flask_ngrok_st']
)
