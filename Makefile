.PHONY: help build run test test-unit test-integration clean

help:
	@echo "Доступные команды:"
	@echo "  build         - Собрать Docker образ"
	@echo "  run           - Запустить приложение в Docker"
	@echo "  test          - Запустить все тесты"
	@echo "  test-unit     - Запустить unit тесты"
	@echo "  test-integration - Запустить интеграционные тесты"
	@echo "  clean         - Очистить контейнеры и образы"

build:
	docker build -t creative-generator .

run:
	docker run -p 8000:8000 \
		-e DATABASE_URL=postgresql://user:password@db:5432/creative_db \
		-e DATA_FILE=/app/data.txt \
		creative-generator

test: build
	docker run --rm \
		-e DATABASE_URL=postgresql://test:test@localhost/test_db \
		-e DATA_FILE=/app/data.txt \
		creative-generator \
		sh -c "pytest tests/ -v"

test-unit: build
	docker run --rm \
		-e DATABASE_URL=postgresql://test:test@localhost/test_db \
		-e DATA_FILE=/app/data.txt \
		creative-generator \
		sh -c "pytest tests/test_app.py tests/test_utils.py tests/test_models.py tests/test_crud.py -v"

test-integration: build
	docker run --rm \
		-e DATABASE_URL=postgresql://test:test@localhost/test_db \
		-e DATA_FILE=/app/data.txt \
		creative-generator \
		sh -c "pytest tests/test_app_integration.py -v -m integration"

clean:
	docker system prune -f