import random
from os.path import join, dirname

import requests
from json_database import JsonStorageXDG

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class DeepCDigitalSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        self.supported_media = [MediaType.MOVIE]
        self.skill_icon = self.default_bg = join(dirname(__file__), "ui", "deepcdigital_icon.jpg")
        self.archive = JsonStorageXDG("DeepCDigitalMovies", subfolder="OCP")
        super().__init__(*args, **kwargs)

    def initialize(self):
        self._sync_db()
        self.load_ocp_keywords()

    def _sync_db(self):
        bootstrap = "https://github.com/JarbasSkills/skill-deepcdigital/raw/dev/bootstrap.json"
        data = requests.get(bootstrap).json()
        self.archive.merge(data)
        self.schedule_event(self._sync_db, random.randint(3600, 24 * 3600))
        self.media_type_exceptions = {}

    def load_ocp_keywords(self):
        title = []
        docus = []

        for url, data in self.archive.items():
            t = data["title"].split("|")[0].split("(")[0].strip().strip("¿?.!").rstrip("¿")
            if "documentary" in data["title"].lower():
                print(t)
                docus.append(t)
                # signal this entry as DOCUMENTARY media type
                # in case it gets selected later
                self.media_type_exceptions[data["url"]] = MediaType.DOCUMENTARY
            else:
                title.append(t)
                if ":" in t:
                    t1, t2 = t.split(":", 1)
                    title.append(t1.strip())
                    title.append(t2.strip())

        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_name", title)
        self.register_ocp_keyword(MediaType.DOCUMENTARY,
                                  "documentary_name", docus)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_streaming_provider",
                                  ["Deep C Digital",
                                   "DeepCDigital"])

    def get_playlist(self, score=50, num_entries=250):
        pl = self.featured_media()[:num_entries]
        return {
            "match_confidence": score,
            "media_type": MediaType.MOVIE,
            "playlist": pl,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": self.skill_icon,
            "bg_image": self.default_bg,
            "title": "DeepCDigital (Movie Playlist)",
            "author": "DeepCDigital"
        }

    @ocp_search()
    def search_db(self, phrase, media_type):
        base_score = 15 if media_type == MediaType.MOVIE else 0
        entities = self.ocp_voc_match(phrase)

        skill = "movie_streaming_provider" in entities  # skill matched

        base_score += 30 * len(entities)
        title = entities.get("movie_name")
        dtitle = entities.get("documentary_name")

        if media_type == MediaType.DOCUMENTARY:
            candidates = [video for video in self.archive.values()
                          if self.media_type_exceptions.get(video["url"], MediaType.MOVIE) ==
                          MediaType.DOCUMENTARY]

        else:
            candidates = [video for video in self.archive.values()
                          if video["url"] not in self.media_type_exceptions]

        if title:
            base_score += 30
            candidates = [video for video in candidates
                          if title.lower() in video["title"].lower()]
            for video in candidates:
                yield {
                    "title": video["title"],
                    "author": video["author"],
                    "match_confidence": min(100, base_score),
                    "media_type": MediaType.MOVIE,
                    "uri": "youtube//" + video["url"],
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["thumbnail"],
                    "bg_image": video["thumbnail"]
                }

        if dtitle:
            base_score += 20
            candidates = [video for video in candidates
                          if dtitle.lower() in video["title"].lower()]
            for video in candidates:
                yield {
                    "title": video["title"],
                    "author": video["author"],
                    "match_confidence": min(100, base_score),
                    "media_type": MediaType.DOCUMENTARY,
                    "uri": "youtube//" + video["url"],
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["thumbnail"],
                    "bg_image": video["thumbnail"]
                }

        if skill:
            yield self.get_playlist()

    @ocp_featured_media()
    def featured_media(self):
        return [{
            "title": video["title"],
            "image": video["thumbnail"],
            "match_confidence": 70,
            "media_type": MediaType.MOVIE,
            "uri": "youtube//" + video["url"],
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "bg_image": video["thumbnail"],
            "skill_id": self.skill_id
        } for video in self.archive.values()]


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = DeepCDigitalSkill(bus=FakeBus(), skill_id="t.fake")
    for r in s.search_db("play Homecoming Massacre", MediaType.MOVIE):
        print(r)
        # {'title': 'Homecoming Massacre | Full Horror Movie | Kenny White | Killer Clown', 'author': 'Deep C Digital', 'match_confidence': 75, 'media_type': <MediaType.MOVIE: 10>, 'uri': 'youtube//https://youtube.com/watch?v=mwOx2kgG26c', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/mwOx2kgG26c/sddefault.jpg?v=62f2bd45', 'bg_image': 'https://i.ytimg.com/vi/mwOx2kgG26c/sddefault.jpg?v=62f2bd45'}
    for r in s.search_db("play Is Genesis History", MediaType.DOCUMENTARY):
        print(r)
        # {'title': 'Is Genesis History? (2017) | Documentary | Del Tackett, Kevin L. Anderson, Steve A. Austin', 'author': 'Deep C Digital', 'match_confidence': 50, 'media_type': <MediaType.DOCUMENTARY: 15>, 'uri': 'youtube//https://youtube.com/watch?v=ulpQSgm70J4', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/ulpQSgm70J4/sddefault.jpg?v=63b71431', 'bg_image': 'https://i.ytimg.com/vi/ulpQSgm70J4/sddefault.jpg?v=63b71431'}
