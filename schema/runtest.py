#!/usr/bin/python3 -u

import json
from jsonschema import validate, Draft7Validator, draft7_format_checker
from jsonschema.exceptions import ValidationError, SchemaError
import glob
import traceback

print("Loading schema")
schema = json.load(open('schema.json','r'))
try:
    Draft7Validator.check_schema(schema)
except SchemaError as e:
    print("\033[31mSchama is not valid\033[0m")
    traceback.print_exc()
    print(e)
    exit(-1)

print("Running tests")
for file in glob.glob("test_messages/*.json"):
    print(f"  Testing \033[33m{file}\033[0m... ",end="")
    test = json.load(open(file,'r'))
    try:
        validate(instance=test, schema=schema, format_checker=draft7_format_checker)
        print(" \033[32mPASS\033[0m")
    except ValidationError as e:
        print(" \033[31mFAIL\033[0m")
        print(e)