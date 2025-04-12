from typing import cast
from bs4 import BeautifulSoup, Tag
from sites.apkmirror import FailedToFetch, FailedToFindElement, Version
import requests
from constants import HEADERS
import utils

HOST = "apkcombo.com"
CHECKIN_URL = "https://apkcombo.com/checkin"


def download_apk(version: Version):
    """
    Download apk given a version
    """

    response = requests.get(version.link, headers=HEADERS)
    if response.status_code != 200:
        raise FailedToFetch(f"{version.link}: {response.status_code}")

    bs4 = BeautifulSoup(response.text, "html.parser")

    download_link = bs4.find("a", attrs={"class": "variant"})
    if download_link is None:
        raise FailedToFindElement("Download link")

    link = download_link.get("href")

    # get the fingerprint

    checkinResponse = requests.get(CHECKIN_URL, headers=HEADERS)
    if response.status_code != 200:
        raise FailedToFetch(f"{version.link}: {response.status_code}")

    package_name = version.link.split("/")[4]

    direct_link = (
        f"https://{HOST}{link}&{checkinResponse.text}&package_name={package_name}"
    )

    print(direct_link)

    utils.download(direct_link, "big_file.apkm", headers=HEADERS)


def get_versions(url: str) -> list[Version]:
    """
    Get the versions of the app from the given apkcombo url
    """

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise FailedToFetch(f"{url}: {response.status_code}")

    bs4 = BeautifulSoup(response.text, "html.parser")
    versions = bs4.find("ul", attrs={"class": "list-versions content"})

    out: list[Version] = []
    if versions is not None:
        versions = cast(Tag, versions)
        for version in versions.findChildren("a", recursive=True):
            v = version.findChild(
                "span", attrs={"class": "vername"}, recursive=True
            ).text.split(" ")[-1]

            link = f"https://{HOST}{version.get('href')}"

            out.append(Version(v, link))

    print(out)

    return out
