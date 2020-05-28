FROM anmolgoyal/tezos-blockchain
RUN apt-get update -y
COPY app /app
WORKDIR /app
CMD ["python3", "app.py"] 
