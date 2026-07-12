up:
	docker-compose up --build

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	pytest --cov=. --cov-report=term-missing

install:
	python -m pip install -r requirements.txt -r requirements-dev.txt

lock-dev:
	pip-compile --generate-hashes --allow-unsafe requirements-dev.txt --output-file requirements-dev.lock

sync-dev:
	python -m pip install -r requirements.txt -r requirements-dev.txt

benchmark:
	python benchmarks/ride_sharing_benchmarks.py --output benchmark-results.json
