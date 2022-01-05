"""api client for returnyoutubedislike.com"""

import base64
import hashlib
import random
import string

import requests

API_URL = "https://returnyoutubedislikeapi.com"
HEADERS = {"User-Agent": "https://github.com/bbilly1/ryd-client v0.0.3"}


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
        challenge = list(base64.b64decode(self.puzzle["challenge"]))
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


class VotePost:
    """cast your vote"""

    def __init__(self, votes, user_id):
        self.votes = votes
        self.user_id = user_id

    def process(self):
        """process the input"""
        if isinstance(self.votes, list):
            to_return = self._process_list()
        elif isinstance(self.votes, tuple):
            youtube_id, vote = self.votes
            validated = self.validate_vote(vote)
            to_return = self.post((youtube_id, validated))
        else:
            raise ValueError

        return to_return

    def _process_list(self):
        """process a list of votes"""
        validated = [(i[0], self.validate_vote(i[1])) for i in self.votes]

        all_messages = []
        for vote in validated:
            message = self.post(vote)
            all_messages.append(message)

        return all_messages

    def post(self, vote):
        """post vote to API"""
        puzzle = self._initial_vote(vote)
        solution = Puzzle(puzzle).solve()
        response = self._confirm_vote(solution, vote[0])
        if not response:
            print(f"failed to cast vote for: {self.user_id}, {vote}")
            raise ValueError

        message = {
            "id": vote[0],
            "status": response,
            "vote": vote[1],
        }

        return message

    @staticmethod
    def validate_vote(vote):
        """convert vote"""
        vote_map = {
            "like": 1,
            "dislike": -1,
            "neutral": 0,
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

    def _initial_vote(self, vote):
        """send initial vote to receive puzzle"""
        data = {
            "userId": self.user_id,
            "videoId": vote[0],
            "value": vote[1],
        }
        url = f"{API_URL}/interact/vote"
        response = requests.post(url, headers=HEADERS, json=data)
        if not response.ok:
            print("failed")
            raise ValueError
        puzzle = response.json()

        return puzzle

    def _confirm_vote(self, solution, video_id):
        """send second confirmation with solved puzzle"""
        data = {
            "userId": self.user_id,
            "videoId": video_id,
            "solution": solution["solution"],
        }
        url = f"{API_URL}/interact/confirmVote"
        response = requests.post(url, headers=HEADERS, json=data)
        if response.ok:
            return response.text == "true"

        return False


class VoteGet:
    """get single vote or list of votes"""

    def __init__(self, youtube_ids):
        self.youtube_ids = youtube_ids

    def process(self):
        """process youtube_ids build list or string"""
        if isinstance(self.youtube_ids, list):
            to_return = self._process_list()
        elif isinstance(self.youtube_ids, str):
            to_return = self._get_vote(self.youtube_ids)
        else:
            raise ValueError

        return to_return

    def _process_list(self):
        """process list"""
        all_votes = []
        for youtube_id in self.youtube_ids:
            parsed = self._get_vote(youtube_id)
            all_votes.append(parsed)
        return all_votes

    @staticmethod
    def _get_vote(youtube_id):
        """get vote from a single video"""
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
            print("ratelimiting reached, cancel")

        return parsed


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


def get(youtube_ids):
    """get votes from list of youtube_ids"""

    result = VoteGet(youtube_ids).process()

    return result


def post(votes, user_id):
    """post votes"""

    result = VotePost(votes, user_id).process()

    return result
