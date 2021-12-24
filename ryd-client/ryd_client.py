"""post votes for YouTube video"""

import random
import string
import base64
import hashlib

import requests

API_URL = "https://returnyoutubedislikeapi.com"
HEADERS = {"User-Agent": "https://github.com/bbilly1/ryd-client v0.0.1"}

class Login:
    """handle user registation"""

    def __init__(self, user_id=False):
        self.user_id = user_id

    def generate_user_id(self):
        """get random 36 int user id"""
        choice = string.ascii_letters + string.digits
        new_user_id = str()
        for _ in range(36):
            letter = random.SystemRandom().choice(choice)
            new_user_id = new_user_id + letter

        self.user_id = new_user_id

        return new_user_id

    def get_puzzle(self):
        """get puzzle"""
        user_id = self.user_id or self.generate_user_id()
        url = f"{API_URL}/puzzle/registration?userId={user_id}"
        puzzle = requests.get(url, headers=HEADERS).json()
        puzzle["user_id"] = user_id

        return puzzle

    def post_puzzle(self, solution):
        """post solved puzzle to confirm registration"""
        url = f"{API_URL}/puzzle/registration?userId={self.user_id}"
        response = requests.post(url, headers=HEADERS, json=solution)
        if response.ok:
            print(f"successfully registered with user id {self.user_id}")
            return response.text == "true"

        return False


class Puzzle:
    """solve your puzzle"""

    def __init__(self, puzzle):
        self.puzzle = puzzle

    @staticmethod
    def count_leading_zeros(to_check):
        """return leading binary zeroes"""
        zeros = 0
        for i in to_check:
            if i == 0:
                zeros = zeros + 8
            else:
                zeros = zeros + f"{i:08b}".index("1")
                break

        return zeros

    def solve(self):
        """get puzzle solution"""
        challenge = list(base64.b64decode(self.puzzle['challenge']))
        max_count = 2 ** self.puzzle["difficulty"] * 5
        # fill buffer
        buffer = bytearray(20)
        for i in range(4, 20):
            buffer[i] = challenge[i - 4]
        # keep hashing until leading zeros are matched
        for i in range(max_count):
            new_buffer = (i).to_bytes(4, byteorder="little") + buffer[4:20]
            to_check = list(hashlib.sha512(new_buffer).digest())
            zeros = self.count_leading_zeros(to_check)
            if zeros >= self.puzzle["difficulty"]:
                solution = base64.b64encode(new_buffer[0:4]).decode()
                return {"solution": solution}

        return False


class Vote:
    """cast your vote"""

    def __init__(self, user_id, vote):
        self.user_id = user_id
        self.video_id = vote[0]
        self.vote = self.validate_vote(vote[1])

    def post(self):
        """post vote to API"""
        puzzle = self._initial_vote()
        solution = Puzzle(puzzle).solve()
        response = self._confirm_vote(solution)
        if not response:
            print(f"failed to cast vote for: {self.user_id}, {self.video_id}")
            raise ValueError

        message = {
            "id": self.video_id,
            "status": response,
            "vote": self.vote
        }

        return message

    @staticmethod
    def validate_vote(vote):
        """convert vote"""
        vote_map = {
            "like": 1,
            "dislike": -1,
            "neutral": 0
        }
        if isinstance(vote, str):
            try:
                return vote_map[vote]
            except KeyError:
                print(f"invalid vote: {vote}")
                raise
        elif isinstance(vote, int):
            if vote in vote_map.values():
                return vote
            raise ValueError(f"invalid vote cast: {vote}")

        return False

    def _initial_vote(self):
        """send initial vote to recieve puzzle"""
        data = {
            "userId": self.user_id,
            "videoId": self.video_id,
            "value": self.vote,
        }
        url = f"{API_URL}/interact/vote"
        response = requests.post(url, headers=HEADERS, json=data)
        if not response.ok:
            print("failed")
            raise ValueError
        puzzle = response.json()

        return puzzle

    def _confirm_vote(self, solution):
        """send second confirmation with solved puzzle"""
        data = {
            "userId": self.user_id,
            "videoId": self.video_id,
            "solution": solution["solution"]
        }
        url = f"{API_URL}/interact/confirmVote"
        response = requests.post(url, headers=HEADERS, json=data)
        if response.ok:
            return response.text == "true"

        return False


def generate_user_id():
    """short hand to generate user id"""
    user_id = Login().generate_user_id()
    return user_id


def register(user_id):
    """register your user id"""
    login_handler = Login(user_id)
    puzzle = login_handler.get_puzzle()
    solution = Puzzle(puzzle).solve()
    response = login_handler.post_puzzle(solution)
    if not response:
        print(f"failed to register with user id {user_id}")
        return False

    return True


def get_votes(youtube_ids):
    """get votes from list of youtube_ids"""

    all_votes = []

    for youtube_id in youtube_ids:
        url = f"{API_URL}/votes?videoId={youtube_id}"
        votes = requests.get(url, headers=HEADERS)

        if votes.ok:
            parsed = votes.json()
            parsed["status"] = votes.status_code
            del parsed["dateCreated"]
        elif votes.status_code in [400, 404]:
            parsed = {
                "id": youtube_id,
                "status": votes.status_code,
            }
        elif votes.status_code == 429:
            print("ratelimiting reached, cancle")
            break

        all_votes.append(parsed)

    return all_votes


def post_votes(votes, user_id):
    """post votes"""
    all_votes = []
    for vote_pair in votes:
        vote_handler = Vote(user_id, vote_pair)
        message = vote_handler.post()
        all_votes.append(message)

    return all_votes
