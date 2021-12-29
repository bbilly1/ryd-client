# RYD Client
Python client library for the **Return YouTube Dislike API**:

- [https://returnyoutubedislike.com/](https://returnyoutubedislike.com/)
- [https://github.com/Anarios/return-youtube-dislike/](https://github.com/Anarios/return-youtube-dislike/)


## Functionality
- Get votes from a list of YouTube video IDs.
- Register your user ID by solving the challenge.
- Cast your vote for a list of YouTube video IDs. 

## Install
Download and install library from [https://pypi.org/project/ryd-client/](https://pypi.org/project/ryd-client/):

```shell
pip install ryd-client
```

## Usage
Some command example

### Get 
Pass a list of YouTube video IDs and get a list of votes or pass a string of a single YouTube video ID to get a single votes dictionary:

```python
import ryd_client

# Passing a list returns a list of dictionaries 
# with ratings for every video ID returns a list

result = ryd_client.get(["kxOuG8jMIgI", "CaaJyRvvaq8"])

[{'id': 'kxOuG8jMIgI',
  'likes': 27863,
  'dislikes': 509751,
  'rating': 1.2113002641063706,
  'viewCount': 3211800,
  'deleted': False,
  'status': 200},
 {'id': 'CaaJyRvvaq8',
  'likes': 505944,
  'dislikes': 13401,
  'rating': 4.900014260551845,
  'viewCount': 3610078,
  'deleted': False,
  'status': 200}]


# passing a single ID returns a dictionary 
# with ratings from a single video

result = ryd_client.get("kxOuG8jMIgI")

{'id': 'kxOuG8jMIgI',
 'likes': 27863,
 'dislikes': 509751,
 'rating': 1.2113002641063706,
 'viewCount': 3211800,
 'deleted': False,
 'status': 200}
```

### Register
To cast a vote, you need to be registered in the API with your user id. Generate a random user id, one per user, store it in your application and reuse for all future votes from this user.

```python
import ryd_client

user_id = ryd_client.generate_user_id()

# Returns a random 36 char string of ascii_letters and digits
'5v3X3mxQOm3fkez8aWsGsEgjpFe0pJNPWIJi'

```

Register your user_id in the api:

```python
import ryd_client

success = ryd_client.register(user_id)

# Returns True on success, False on fail
True

```

### Post
Once your `user_id` is registered, you are allowed to vote. Vote on a list or on a single video ID. Pass a list or a single tuple where the first value of the tuple is the video ID and second value is the vote either as `string` or `int`:
- like: 1
- dislike: -1
- neutral: 0 (aka *undo* your previous vote)

Strings automatically get converted to the matching number, both are valid:

```python
import ryd_client

# voting on a list of videos
# returns a list of results
votes = [
    ("kxOuG8jMIgI", "dislike"),
    ("CaaJyRvvaq8", 1),
    ("CEp5SLT-DJg", 0),
]

response = ryd_client.post(votes, user_id=user_id)

[{'id': 'kxOuG8jMIgI', 'status': True, 'vote': -1},
 {'id': 'CaaJyRvvaq8', 'status': True, 'vote': 1},
 {'id': 'CEp5SLT-DJg', 'status': True, 'vote': 0}]

# voting on a single video
# returns a single result

vote = ("kxOuG8jMIgI", -1)
response = ryd_client.post(vote, user_id=user_id)

{'id': 'kxOuG8jMIgI', 'status': True, 'vote': -1}

```


## Acknowledgement
If you find this API useful, please consider donating to the [project](https://returnyoutubedislike.com/donate).
