from setuptools import setup, find_packages

setup(
    name="data-analytics-app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.0.0",
        "pandas>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "start-app=app.main:main"
        ],
    },
)
