.PHONY: up
up:
	@docker compose up -d

.PHONY: bank
up:
	@docker compose up -d bank

.PHONY: client
up:
	@docker compose up -d client1

.PHONY: clients
up:
	@docker compose up -d client1 client2

