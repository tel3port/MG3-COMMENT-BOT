# -*- coding: utf-8 -*-

from google_search_results import GoogleSearchResults
import json

# create the serpwow object, passing in our API key
serpwow = GoogleSearchResults("DC14D724")

params = {
  "q": "Donald Trump",
  "search_type": "news",
  "no_cache": "true"
}
# retrieve the search results as JSON
result = serpwow.get_json(params)

# pretty-print the result
print(json.dumps(result, indent=2, sort_keys=True))