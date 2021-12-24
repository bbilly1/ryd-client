# RYD Client
Python client library for the **Return YouTube Dislike API**:

- [https://returnyoutubedislike.com/](https://returnyoutubedislike.com/)
- [https://github.com/Anarios/return-youtube-dislike/](https://github.com/Anarios/return-youtube-dislike/)


## Functionality
- Get votes from a list of YouTube video IDs.
- Register your user ID by solving the challenge.
- Cast your vote for a list of YouTube video IDs. 


## Usage
Some command example

### Get Votes
Pass a list of YouTube video IDs and get a list of votes.

```python
import ryd_client

ratings = ryd_client.get_votes(["kxOuG8jMIgI", "CaaJyRvvaq8"])

# Returns a list of dictionaries with ratings for every video ID
[{'id': 'kxOuG8jMIgI',
  'likes': 27569,
  'dislikes': 503144,
  'rating': 1.2117898772151874,
  'viewCount': 3177346,
  'deleted': False,
  'status': 200},
 {'id': 'CaaJyRvvaq8',
  'likes': 502489,
  'dislikes': 13270,
  'rating': 4.900305046067389,
  'viewCount': 3575816,
  'deleted': False,
  'status': 200}]
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

### Post Votes
Once your `user_id` is registered, you are allowed to vote. Vote on a list of video IDs. Pass a list of tuples where the first value is the video ID and second value is the vote either as `string` or `int`:
- like: 1
- dislike: -1
- neutral: 0 (aka *undo* your previous vote)

Strings automatically get converted to the matching number, both are valid:

```python
import ryd_client

votes = [
    ("kxOuG8jMIgI", "dislike"),
    ("CaaJyRvvaq8", 1),
    ("CEp5SLT-DJg", 0),
]

response = ryd_client.post_votes(votes, user_id=user_id)

# Returns a list of dictionaries for every vote cast
[{'id': 'kxOuG8jMIgI', 'status': True, 'vote': -1},
 {'id': 'CaaJyRvvaq8', 'status': True, 'vote': 1},
 {'id': 'CEp5SLT-DJg', 'status': True, 'vote': 0}]

```


## Acknowledgement
If you find this API usefull, please consider donating to the [project](https://returnyoutubedislike.com/donate).
