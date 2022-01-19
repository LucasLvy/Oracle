ligo=docker run --rm -v "$$PWD":"$$PWD" -w "$$PWD" ligolang/ligo:0.33.0
protocol=--protocol hangzhou
json=--michelson-format json

all: compile test originate

help:
	@echo  'Usage:'
	@echo  '  all             - Remove generated Michelson files, recompile smart contracts and lauch all tests'
	@echo  '  clean           - Remove generated Michelson files'
	@echo  '  test            - Run python unit tests'
	@echo  '  originate       - Deploy smart contracts advisor & indice (typescript using Taquito)'
	@echo  ''

compile: main.mligo clean
	@echo "Compiling to Michelson"
	@$(ligo) compile contract main.mligo $(protocol) > test/Oracle.tz
	@echo "Compiling to Michelson json format"
	@$(ligo) compile contract main.mligo $(json) $(protocol) > Oracle.json
	@$(ligo) compile contract client/main.mligo $(json) $(protocol) > Client.json

clean:
	@echo "Removing Michelson files"
	@rm -rf *.tz
	@echo "Removing Michelson 'json format' files"
	@rm Client.json
	@rm Oracle.json


test: compile
	@echo "Running the tests"
	@docker build . -t oracle_tests:latest
	@docker run oracle_tests:latest

originate:
	@echo "Deploying contract"
	@tsc deploy.ts --esModuleInterop --resolveJsonModule
	@node deploy.js