# Makefile

start:
	@echo Starting basic server...
	@python3 basic.py & echo $$! > server1.pid
	@echo 'Starting flask(keep alive) server...'
	@python3 flask_keep_alive.py & echo $$! > server2.pid

stop:
	@echo Stopping basic server...
	@kill `cat server1.pid` && rm server1.pid
	@echo 'Stopping flask(keep alive) server...'
	@kill `cat server2.pid` && rm server2.pid

.PHONY: start stop
