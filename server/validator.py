import os
import json
from jsonschema import validate, RefResolver, draft7_format_checker, Draft7Validator
from jsonschema.exceptions import ValidationError, SchemaError

##
# Message validation system.
# Applies the json schema to incoming and outging messages.
class MessageValidator():

    def __init__(self, config, core):
        self.config = config
        self.core = core

        self.schemapath = os.path.abspath("../schema/schema.json")
        self.schema = json.load(open(self.schemapath, 'r'))
        self.schema_resolver = RefResolver("file:" + self.schemapath, self.schema)

        try:
            Draft7Validator.check_schema(self.schema)
        except SchemaError as e:
            print("\033[31mSchama is not valid\033[0m")
            print(e)

    def validate(self, message):
        try:
            validate(message, self.schema, resolver=self.schema_resolver, format_checker=draft7_format_checker)
            return True
        except ValidationError as e:
            print("\033[31mSchema Validation Failure:\033[0m")
            print("Message:\033[33m")
            print(json.dumps(message, indent=2))
            print("\033[0mError:")
            print(e)
            print("== End of Error ==")
            return False