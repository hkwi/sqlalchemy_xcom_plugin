sqlalchemy mysql group replication connect helper

Put `plugin=xcom` parameter in dialect string (ex: `mysql://user:password@host/dbname?plugin=xcom` ), then sqlalchemy event listeners in xcom plugin becomes activated. XCom is an implemention of MySQL group replication infrastructure.

Single-primary mode is supported for now. Note that the user connecting to mysql have SELECT privilege on tables in `performance_schema` datababase.
