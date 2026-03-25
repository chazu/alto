.PHONY: build thin wrap clean test image run-image

# Full embedded build — standalone binary with full mag tooling (~84MB)
build: wrap
	mag build --full -o alto

# Thin embedded build — minimal binary with just VM + tcell + image (~77MB)
# No REPL, no formatter, no doctest — just runs Alto
thin: wrap
	mag build -o alto-thin

# Save Alto image separately (683K) — for use with external mag VM
image: wrap
	mag src/... wrap/... --save-image alto.image

# Run from saved image using system mag (decoupled from binary)
run-image: image
	mag --image alto.image -m Alto::Main.start

# Run example apps (use: make example-hello, make example-counter, etc.)
example-hello: build
	./alto -m Alto::HelloApp.start

example-counter: build
	./alto -m Alto::CounterApp.start

example-todo: build
	./alto -m Alto::TodoApp.start

example-dashboard: build
	./alto -m Alto::DashboardApp.start

# Run acceptance tests (40 tests)
test: wrap
	@cp test/test_system_browser_acceptance.mag src/tools/BrowserTest.mag
	@mag build --full -o alto_test
	@./alto_test -m Alto::BrowserTest.run
	@rm -f src/tools/BrowserTest.mag alto_test

wrap:
	mag wrap

clean:
	rm -f alto alto-thin alto_test alto.image profile.folded cpu.pprof
