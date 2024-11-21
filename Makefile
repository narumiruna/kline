test:
	uv run pytest -v -s tests

lint:
	uv run ruff check --fix .

download:
	uv run kline ccxt \
		-e binance \
		-s BTCUSDT \
		-s ETHUSDT \
		-s BNBUSDT \
		-s XRPUSDT \
		-s BCHUSDT \
		-s LTCUSDT \
		-s SANDUSDT \
		-s LINKUSDT \
		-s DOGEUSDT \
		-s COMPUSDT \
		-s DOTUSDT \
		-s MATICUSDT \
		-s ADAUSDT \
		-s SOLUSDT \
		-s SHIBUSDT \
		-s APEUSDT \
		-s ETCUSDT \
		-t 1h \
		-t 1d \
		-o data/2023-03-24
