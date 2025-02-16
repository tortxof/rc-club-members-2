import requests
from bs4 import BeautifulSoup


def verify_ama_membership(last_name: str, ama_number: int):
    response = requests.post(
        "https://www.modelaircraft.org/membership/verify",
        params={"ajax_form": "1"},
        data={
            "form_id": "membership_verify_form",
            "last_name": last_name,
            "ama_number": ama_number,
        },
    )

    soup = BeautifulSoup(response.json()[0]["data"], "html.parser")

    status = [
        stripped_line
        for stripped_line in (line.strip() for line in soup.text.split("\n"))
        if stripped_line
    ][1]

    return status
