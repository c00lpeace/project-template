from setuptools import setup, find_packages

setup(
    name="shared_core",
    version="1.0.0",
    description="공통 문서 모델 패키지 - Backend와 Prefect 프로젝트에서 공통으로 사용",
    author="Document Processing Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "python-dateutil>=2.8.0",
    ],
)
