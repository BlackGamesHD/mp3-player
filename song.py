import eyed3

from music_player.constants import IMAGES_CACHE, UNKNOWN_ARTIST


class Song:
    def __init__(self, song_path):
        song_tags = eyed3.load(song_path)
        tags = song_tags.tag

        self.title = tags.title if tags.title else "Desconhecido"
        self.short_title = self.title if len(self.title) < 35 else self.title[:35] + '...'
        self.artist = tags.artist if tags.artist else "Desconhecido"
        self.album = tags.album if tags.album else "Desconhecido"
        self.duration = int(song_tags.info.time_secs)
        self.image = self.get_song_cover(tags.images)
        self.path = song_path

    def get_song_cover(self, images):
        return self.save_album_cover(images[0]) if images else UNKNOWN_ARTIST

    def save_album_cover(self, image):
        image_path = "{}/img{}.jpeg".format(IMAGES_CACHE, self.title.replace('*', ''))
        with open(image_path, "wb") as file:
            file.write(image.image_data)
        return image_path

    def __str__(self):
        return "{}{}".format(self.title, self.artist)
