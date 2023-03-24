install:
	poetry install

test: install
	poetry run pytest -v -s tests

download:
	poetry run cryptodataset ccxt \
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
