#!/usr/bin/env python3
import requests
import argparse
from collections import namedtuple
from os import environ
from datetime import datetime, tzinfo
import time
import json
from math import ceil

# force israel time
environ["TZ"] = "Asia/Jerusalem"
time.tzset()

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


def get_balance(s):
    return float(s.get("https://www.mysodexo.co.il/new_ajax_service.aspx?getBdgt=1").text)


# subcommands

def print_balance(args):
    s = login(glob_auth_data)
    print(get_balance(s))

def print_plan(args):
    reset_day = args.reset_day
    daily_max = args.daily_max

    iter_date = datetime.now()

    # find the number of days
    day_count = 0
    first_day = True
    while (first_day) or (iter_date.day < reset_day):
        first_day = False
        # monday is 0, sunday is 6, friday,saturday are 4,5
        if iter_date.weekday() not in [4, 5]:
            day_count += 1

        iter_date = datetime(iter_date.year, iter_date.month, iter_date.day + 1)

    if day_count == 0:
        print("no days... why are you doing this on a weekend???")
        return

    balance = get_balance(login(glob_auth_data))
    needed_days = (ceil(balance) + (daily_max - 1)) // daily_max

    print("balance:", balance)
    print("days remaining (including today):", day_count)
    print("needed days:", needed_days)
    print("you should start in:", day_count - needed_days, "days")


# parser

my_parser = argparse.ArgumentParser(description="A cli for cibus", prog="clibus")
subparsers = my_parser.add_subparsers(title="subcommands", description="required subcommands", required=True)

parser_balance = subparsers.add_parser("balance", help="get account balance")
parser_balance.set_defaults(func=print_balance)
parser_plan = subparsers.add_parser("plan", help="when should you starting extracting to wolt?")
parser_plan.add_argument("--reset-day", type=int, default=25)
parser_plan.add_argument("--daily-max", type=int, default=200)
parser_plan.set_defaults(func=print_plan)

args = my_parser.parse_args()
args.func(args)
