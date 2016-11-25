.PHONY: test

deploy: build
	aws lambda update-function-code \
	--function-name FindGoesAppt \
	--zip-file fileb://deploy.zip

build: deploy.zip

deploy.zip: lambda_function.py mechanize
	zip -r deploy lambda_function.py mechanize/

test:
	python test.py