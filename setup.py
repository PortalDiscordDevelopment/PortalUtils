import subprocess

from setuptools import setup

# with open("README.md", "r", encoding="utf-8") as fh:
#    long_description = fh.read()

ver = "0.1.0"

try:  # shamelessly stolen from jishaku
    ccount, cerr = subprocess.Popen(
        ["git", "rev-list", "--count", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()
    if ccount:
        chash, cerr = subprocess.Popen(
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()
        if chash:
            ver += ccount.decode().strip() + "+" + chash.decode().strip()
except:
    pass

setup(
    name="PortalUtils",
    version=ver,
    author="Clari, Zanderp25, Sparrow001",
    author_email="clarinet.puppy@gmail.com",
    url="https://github.com/PortalDiscordDevelopment/PortalUtils",
    description="Utilities for Portal bots written in discord.py.",
    #    long_description=long_description,
    packages=["PortalUtils"],
)
