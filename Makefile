.PHONY: build wrap clean profile pprof

build: wrap
	mag build --full -o alto

wrap:
	mag wrap

clean:
	rm -f alto profile.folded cpu.pprof

profile: build
	./alto --profile --profile-rate 1000 -v

pprof: build
	./alto --pprof -v
