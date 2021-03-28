from setuptools import setup

setup(name="sqlalchemy_xcom_plugin",
	version="1.0",
	description="MySQL Group replication connect helper",
	author="Hiroaki Kawai",
	author_email="hiroaki.kawai@gmail.com",
	url="https://github.com/hkwi/sqlalchemy_xcom_plugin",
	py_modules = ["sqlalchemy_xcom_plugin"],
	entry_points={
		"sqlalchemy.plugins": [
			"xcom = sqlalchemy_xcom_plugin:XcomPlugin"
		]
	}
)
