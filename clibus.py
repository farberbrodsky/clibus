#!/usr/bin/env python3
import requests
import argparse
from collections import namedtuple
from os import environ
import json

AuthData = namedtuple("AuthData", "username company password")

with open(environ["HOME"] + "/.cibus.json") as f:
    json_auth_data = json.load(f)
    assert(type(json_auth_data["username"]) is str)
    assert(type(json_auth_data["company"]) is str)
    assert(type(json_auth_data["password"]) is str)

glob_auth_data = AuthData(json_auth_data["username"], json_auth_data["company"], json_auth_data["password"])

def login(auth_data):
    s = requests.Session()
    data = {
        "txtUsr": auth_data.username + "|" + auth_data.company,
        "hidUsr": auth_data.username,
        "txtCmp": auth_data.company,
        "txtPas": auth_data.password,
        "txtPhone": "",
        "g-recaptcha-response": "",
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATEGENERATOR": "E02A6B22",
        "ctl12": "",
        "ctl19": ""
    }

    login_result = s.post("https://www.mysodexo.co.il/", data=data)
    second_result = s.get("https://www.mysodexo.co.il/new_login.aspx?ref=&protocol=")
    # validity checking
    assert(s.cookies)
    assert("%2f" in s.cookies["birthday"])
    return s

# subcommands

def print_balance(args):
    s = login(glob_auth_data)
    print(s.get("https://www.mysodexo.co.il/new_ajax_service.aspx?getBdgt=1").text)


# parser

my_parser = argparse.ArgumentParser(description="A cli for cibus", prog="clibus")
subparsers = my_parser.add_subparsers(title="subcommands", description="required subcommands", required=True)

parser_balance = subparsers.add_parser("balance", help="get account balance")
parser_balance.set_defaults(func=print_balance)

args = my_parser.parse_args()
args.func(args)
