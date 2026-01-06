import requests
import time


class AniListClient:
    BASE_URL = "https://graphql.anilist.co"

    def __init__(self, token=None, log_func=print):
        self.log = log_func
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if token:
            self.headers['Authorization'] = f'Bearer {token}'

    def post(self, query, variables=None):
        try:
            response = requests.post(
                self.BASE_URL,
                json={'query': query, 'variables': variables},
                headers=self.headers
            )

            if response.status_code == 429:
                self.log("⚠️ Rate Limit! Waiting 60s...")
                time.sleep(60)
                return self.post(query, variables)  # Retry

            if response.status_code != 200:
                self.log(f"API Error {response.status_code}: {response.text}")
                return None

            return response.json()
        except Exception as e:
            self.log(f"Request failed: {e}")
            return None

    def validate_token(self):
        query = 'query { Viewer { id name } }'
        data = self.post(query)
        if data and 'data' in data:
            return data['data']['Viewer']
        return None

    def get_user_list(self, user_name_or_id):
        if isinstance(user_name_or_id, int):
            var_type = "$userId: Int"
            arg = "userId: $userId"
            variables = {'userId': user_name_or_id}
        else:
            var_type = "$userName: String"
            arg = "userName: $userName"
            variables = {'userName': user_name_or_id}

        query = f'''
        query ({var_type}) {{
            MediaListCollection({arg}, type: ANIME) {{
                lists {{
                    entries {{
                        mediaId
                        progress
                        media {{
                            id
                            title {{ romaji english }}
                        }}
                    }}
                }}
            }}
        }}
        '''

        data = self.post(query, variables)
        existing = {}

        if data and 'data' in data:
            for lst in data['data']['MediaListCollection']['lists']:
                for entry in lst['entries']:
                    existing[entry['mediaId']] = entry['progress']
        return existing

    def search_anime(self, search_string):
        query = '''
        query ($search: String) {
          Media (search: $search, type: ANIME, sort: SEARCH_MATCH) {
            id
            title { romaji english }
          }
        }
        '''
        data = self.post(query, {'search': search_string})
        if data and 'data' in data:
            return data['data']['Media']
        return None

    def update_list(self, media_id, progress):
        query = '''
        mutation ($mediaId: Int, $progress: Int) {
          SaveMediaListEntry (mediaId: $mediaId, progress: $progress, status: CURRENT) { id }
        }
        '''
        data = self.post(query, {'mediaId': media_id, 'progress': progress})
        return data is not None