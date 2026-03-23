.PHONY: fetch summary help

fetch: ## Google News RSS에서 뉴스 수집
	python3 scripts/fetch_news.py

fetch-3d: ## 최근 3일 뉴스만 수집
	python3 scripts/fetch_news.py --days 3

summary: ## 수집된 뉴스 요약 출력
	python3 scripts/generate_post.py

help: ## 도움말
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'
