# class Playlist:
#     def __init__(self, name : str, tracks : list[str]):
#         self.name = name
#         self.tracks = tracks

#     @classmethod
#     def list_to_json(cls, playlists: list['Playlist']):
#         json = '{'
#         playlist_json = []
#         for playlist in playlists:
#             tracks_json = ','.join([f'"{track}"' for track in playlist.tracks])
#             playlist_json.append(f'"{playlist.name}":[{tracks_json}]')
#         json += ','.join(playlist_json)
#         json += '}'
#         return json
    
#     @classmethod
#     def json_to_list(cls, json : str):
#         playlists = []
#         json = json[1:-1]
#         for playlist in json.split(','):
#             name, tracks = playlist.split(':', maxsplit=1)
#             tracks = tracks[1:-1].split(',')
#             tracks = [track.replace('"','') for track in tracks if track] 
#             playlists.append(Playlist(name.replace('"',''), tracks))
#         return playlists