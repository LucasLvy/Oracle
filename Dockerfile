FROM smartnodefr/pythonligo:latest

COPY . .

RUN ligo compile contract main.mligo > test/Oracle.tz

WORKDIR /test

ENTRYPOINT [ "pytest"]
