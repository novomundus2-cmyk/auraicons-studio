.PHONY: test up down status producer spark math db pipeline ai netgui archify verify-all logs help

help:
	@echo "=================================================================="
	@echo " DATA PLATFORM, HASKELL/PYTHON MATH, DATABASE & ARCHIFY LAB"
	@echo "=================================================================="
	@echo "make verify-all - Run Math + Build DB + Run Pipeline + AI Audit"
	@echo "make archify    - Open the interactive Archify Pipeline Visualizer"
	@echo "make netgui     - Web server on this Mac only (port 8765). LAN=1 shares it read-only on your Wi-Fi"
	@echo "make test       - Run the regression test suite (temp databases, safe)"
	@echo "make db         - Build & populate the Master Database & Categories"
	@echo "make pipeline   - Execute the 6-Stage Clean Code Streaming Pipeline"
	@echo "make math       - Run SymPy, SciPy, NumPy & Polars mathematical proofs"
	@echo "make ai         - Run Multi-AI Audit (Antigravity SDK + BigQuery AI/ML)"
	@echo "make up         - Start Kafka (KRaft), NiFi, Spark, MinIO containers"
	@echo "make down       - Stop all platform containers"
	@echo "=================================================================="

verify-all: math db pipeline ai

archify:
	open 05_archify_visualizer/index.html

netgui:
	/opt/homebrew/bin/uv run --directory 06_ai_note_agent python ../05_archify_visualizer/netgui_server.py $(if $(LAN),--lan)

test:
	/opt/homebrew/bin/uv run --directory 06_ai_note_agent --with pytest python -m pytest ../tests -q

db:
	/opt/homebrew/bin/uv run --directory 06_ai_note_agent python ../04_database_lakehouse/build_database.py

pipeline:
	/opt/homebrew/bin/uv run --directory 06_ai_note_agent python ../02_streaming_platform/pipeline_orchestrator.py

math:
	/opt/homebrew/bin/uv run --directory 06_ai_note_agent python ../03_math_haskell_python/scientific_analytics.py

ai:
	/opt/homebrew/bin/uv run --directory 06_ai_note_agent python agent.py --audit

notes:
	/opt/homebrew/bin/uv run --directory 06_ai_note_agent python agent.py

up:
	docker compose up -d
	@echo "Services launching..."
	@echo "- Kafka Broker: localhost:9092"
	@echo "- NiFi Web UI:  https://localhost:8443/nifi (admin / adminPassword123!)"
	@echo "- Spark UI:     http://localhost:8080"
	@echo "- MinIO S3:     http://localhost:9001 (minioadmin / minioadmin)"

down:
	docker compose down

status:
	docker compose ps

logs:
	docker compose logs -f

producer:
	python3 -m pip install -q -r 02_streaming_platform/producers/requirements.txt
	python3 02_streaming_platform/producers/transaction_producer.py

spark:
	docker exec -it data-platform-spark-master /opt/bitnami/spark/bin/spark-submit \
		--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
		--master spark://spark-master:7077 \
		/opt/bitnami/spark/jobs/streaming_processor.py
