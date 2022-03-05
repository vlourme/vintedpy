import json
import api

res = api.search(
    'https://www.vinted.fr/vetements?search_text=dunk%20low&search_id=4680213517&status[]=3&status[]=4&size_id[]=790')

print(json.dumps(res, indent=2))
