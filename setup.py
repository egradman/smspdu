from setuptools import setup, find_packages

setup(
    name          = "smspdu",
    version       = "0.2",
    url           = "http://www.exothermia.net/monkeys_and_robots/2009/04/24/python-code-to-decode-sms-pdu/",
    author        = "Eric Gradman",
    author_email  = "eric@gradman.com",
    description   = "A module to decode SMS PDU format (and talk to an Ericcson T68 phone",
    license       = "MIT",
    packages      = find_packages(),
)
