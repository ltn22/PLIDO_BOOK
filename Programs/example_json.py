import json
import pprint

struct_python = {
"Image": {
      "Width": 800,
      "Height": 600,
      "Title": "View from 15th Floor",
      "Thumbnail": {   
           "Url": "http://www.example.com/image/481989943",
           "Height": 125,
           "Width": 100
       },
       "Animated" : False,
       "Copyright" : None,
       "IDs": [0x11, 0x943, 234, 38793],
       "Title": "Empty picture"
    }
}

print (struct_python)
pprint.pprint(struct_python)

struct_json = json.dumps(struct_python)

print(struct_json)

struct_python2 = json.loads(struct_json)

pprint.pprint (struct_python2)