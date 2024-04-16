from __utils__ import *
import pandas as pd
from server import app
import json

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

from quickbooks import QuickBooks

with open("data.json", "r") as f:
    data = json.load(f)

auth_client = AuthClient(
        **data
    )

auth_client.refresh()
data["refresh_token"] = auth_client.refresh_token

with open("data.json", "w") as f:
    json.dump(data, f)
    
client = QuickBooks(
        auth_client=auth_client,
        refresh_token=auth_client.refresh_token,
        company_id=auth_client.realm_id
    )

ProfitAndLossDetail = client.get_report("ProfitAndLossDetail", {
    "start_date": "2016-01-01",
    "end_date": "2025-01-01"
})

with open("data/ProfitAndLossDetail.json", "w") as f:
    json.dump(ProfitAndLossDetail, f)