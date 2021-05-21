import glob

from pygame import mixer
from PyQt5.QtGui import QCursor, QIcon, QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout, \
    QStyleFactory, QScrollArea, QSlider, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from functools import partial
from copy import deepcopy

from music_player.config import ConfigScreen
from music_player.local_functions.time_functions import duration_from_seconds
from music_player.song import Song
from music_player.constants import PLAY_ICON, PAUSE_ICON, NEXT_ICON, PREVIOUS_ICON, ADD_FOLDER_ICON, UNKNOWN_ARTIST


class MainWindow(QWidget):

    playing = False
    playing_index = 0
    current_playing = ''
    elapsed_time = 0
    songs = []
    playlist = []
    library_folders = []

    def __init__(self, title):
        super().__init__()

        # Config window
        self.config_window = ConfigScreen(self.library_folders)

        # song elapsed time timer
        self.slider_elapsed_time = QSlider(Qt.Horizontal)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.increment_elapsed_time)

        # Footer widgets
        self.artist_label = QLabel("")
        self.image_label = QLabel()
        self.song_label = QLabel("")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.label_current_song_elapsed = QLabel("00:00")
        self.label_current_song_duration = QLabel("00:00")
        self.play_button = QPushButton("")

        # Window config
        self.setWindowTitle(title)
        self.setLayout(QVBoxLayout())
        self.setStyleSheet("background-color: #181818")
        self.setMinimumSize(830, 600)

        # Creates body container and footer
        self.songs_container = self.create_songs_container()
        self.layout().addWidget(self.songs_container)
        self.footer()

        self.show()

    def create_songs_container(self):
        container = QWidget()
        grid = QGridLayout()
        container.setLayout(grid)
        grid.setContentsMargins(0, 0, 0, 0)

        try:
            grid.addWidget(self.song_list_header(), 0, 0)
            grid.addWidget(self.songs_list(), 1, 0)
        except Exception as e:
            print(e)

        return container

    @staticmethod
    def song_list_header():
        grid = QGridLayout()
        containter = QWidget()
        containter.setLayout(grid)
        grid.setContentsMargins(0, 10, 0, 10)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)

        label_header_play = QLabel("#")
        label_header_play.setStyleSheet("color: #B3B3B3; margin-bottom: 5%; margin-left: 20px;")
        label_header_play.setAlignment(Qt.AlignCenter)
        label_header_play.setMaximumWidth(40)

        label_header_song = QLabel("Música")
        label_header_song.setStyleSheet("color: #B3B3B3; margin-bottom: 5%;  margin-left: 20px;")

        label_header_artist = QLabel("Artista")
        label_header_artist.setStyleSheet("color: #B3B3B3; margin-bottom: 5%;  margin-left: 20px;")
        label_header_artist.setMinimumSize(200, 0)

        label_header_duration = QLabel("Duração")
        label_header_duration.setStyleSheet("color: #B3B3B3; margin-bottom: 5%")

        grid.addWidget(label_header_play, 0, 0)
        grid.addWidget(label_header_song, 0, 1)
        grid.addWidget(label_header_artist, 0, 2)
        grid.addWidget(label_header_duration, 0, 3)

        return containter

    def no_song_container(self):
        container = QWidget()
        grid = QVBoxLayout()
        container.setLayout(grid)

        grid.setAlignment(Qt.AlignCenter)

        label_no_song_found = QLabel("Não encontramos nenhuma música")
        label_no_song_found.setStyleSheet("color: #B3B3B3")

        button_add_folder = QPushButton("")
        button_add_folder.setFixedSize(50, 50)
        button_add_folder.setStyleSheet("color: #F2F2F2; border-image : url({})".format(ADD_FOLDER_ICON))
        button_add_folder.clicked.connect(self.open_config)

        grid.addWidget(label_no_song_found)
        grid.addWidget(button_add_folder)

        return container

    def song_row(self, song):
        container = QWidget()
        grid = QGridLayout()
        grid.setColumnStretch(1, 0)
        grid.setColumnStretch(2, 2)
        grid.setColumnStretch(5, 1)
        grid.setColumnStretch(4, 1)
        container.setLayout(grid)

        button_play = QPushButton(QIcon(PLAY_ICON), '')
        button_play.setCursor(QCursor(Qt.PointingHandCursor))
        button_play.clicked.connect(partial(self.play_song, song))
        button_play.setStyleSheet("border: 5px solid transparent; margin-right: 10px")

        label_song = QLabel(f"{song.short_title}")
        label_song.setStyleSheet("color: #F2F2F2; margin-right: 5px; ")
        label_song.setFont(QFont('Arial', 8))

        label_image = QLabel("")
        label_image.setStyleSheet("background: #181818; color: #F2F2F2;")

        pixmap = QPixmap(song.image).scaled(50, 50)
        label_image.setPixmap(pixmap)

        label_artist = QLabel(f"{song.artist}")
        label_artist.setMinimumSize(200, 0)
        label_artist.setStyleSheet("color:#B3B3B3; margin-left: 10px;")

        label_duration = QLabel("{}".format(duration_from_seconds(song.duration)))
        label_duration.setStyleSheet("color:#B3B3B3")

        grid.addWidget(button_play,    0, 0)
        grid.addWidget(label_image,     0, 1)
        grid.addWidget(label_song,     0, 2)
        grid.addWidget(label_artist,   0, 4)
        grid.addWidget(label_duration, 0, 5)

        return container

    def footer(self):
        container = QWidget()
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(5, 10, 5, 5)
        container.setLayout(footer_layout)

        # Song image
        pixmap = QPixmap(UNKNOWN_ARTIST).scaled(50, 50)
        self.image_label.setPixmap(pixmap)
        self.image_label.setMaximumWidth(50)

        # Song info container
        container_song_info = QGridLayout()
        self.song_label.setStyleSheet("color: #F2F2F2; margin-left:10px; margin-right:30px;")
        self.song_label.setAlignment(Qt.AlignLeft)
        self.song_label.setFont(QFont('Arial', 13))
        self.song_label.setFixedWidth(200)
        self.artist_label.setFont(QFont('Arial', 8))
        self.artist_label.setStyleSheet("color: #F2F2F2; margin-left:10px; margin-right:30px;")
        self.artist_label.setAlignment(Qt.AlignLeft)
        self.artist_label.setFixedWidth(200)

        container_song_info.addWidget(self.song_label)
        container_song_info.addWidget(self.artist_label)

        # Playback info container
        container_playback = QGridLayout()
        self.slider_elapsed_time.setValue(0)
        self.slider_elapsed_time.sliderReleased.connect(self.change_song_timestamp)
        self.slider_elapsed_time.setEnabled(False)

        self.label_current_song_elapsed.setStyleSheet("color: #F2F2F2")
        self.label_current_song_duration.setStyleSheet("color: #F2F2F2")

        self.play_button.setStyleSheet("border-image : url({});".format(PAUSE_ICON))
        self.play_button.clicked.connect(self.player_controller)
        self.play_button.setFixedSize(24, 24)

        previous_button = QPushButton('')
        previous_button.setStyleSheet("border-image : url({});".format(PREVIOUS_ICON))
        previous_button.setFixedSize(18, 18)
        previous_button.clicked.connect(self.previous_song)

        next_button = QPushButton('')
        next_button.setStyleSheet("border-image : url({});".format(NEXT_ICON))
        next_button.setFixedSize(18, 18)
        next_button.clicked.connect(self.next_song)

        buttons_container = QHBoxLayout()
        buttons_container.setAlignment(Qt.AlignCenter)
        buttons_container.addWidget(previous_button)
        buttons_container.addWidget(self.play_button)
        buttons_container.addWidget(next_button)

        container_playback.addLayout(buttons_container, 0, 1, 1, 2)
        container_playback.addWidget(self.label_current_song_elapsed, 1, 0)
        container_playback.addWidget(self.label_current_song_duration, 1, 2)
        container_playback.addWidget(self.slider_elapsed_time, 1, 1)
        container_playback.setContentsMargins(0, 0, 150, 0)

        # Volume container
        container_volume = QGridLayout()
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(30)
        self.volume_slider.setValue(30)
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.valueChanged.connect(self.change_volume)
        container_volume.addWidget(self.volume_slider)
        container_volume.setContentsMargins(0, 5, 0, 0)

        footer_layout.addWidget(self.image_label)
        footer_layout.addLayout(container_song_info)
        footer_layout.addLayout(container_playback)
        footer_layout.addLayout(container_volume)

        self.layout().addWidget(container)

    def songs_list(self):
        scroll = QScrollArea()
        container = QWidget()
        container.setLayout(QVBoxLayout())

        self.scan_songs()

        if self.songs:
            for song in self.songs:
                container.layout().addWidget(self.song_row(song))
        else:
            container.layout().addWidget(self.no_song_container())

        scroll.setWidget(container)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        return scroll

    def play_song(self, song):
        self.slider_elapsed_time.setEnabled(True)
        self.playing = True
        self.elapsed_time = 0
        self.label_current_song_elapsed.setText("00:00")
        self.slider_elapsed_time.setValue(0)
        self.slider_elapsed_time.setMaximum(song.duration)
        self.update_timer.start(1000)

        # Swap current song to the start of the playlist
        song_index = [song.title for song in self.playlist].index(song.title)
        self.playing_index = song_index

        pixmap = QPixmap(song.image).scaled(50, 50)
        self.image_label.setPixmap(pixmap)

        self.song_label.setText(song.title)
        self.artist_label.setText(song.artist)
        self.label_current_song_duration.setText(f"{duration_from_seconds(song.duration)}")
        mixer.music.load(song.path)

        mixer.music.play()

    def increment_elapsed_time(self):
        self.elapsed_time += 1
        self.slider_elapsed_time.setValue(self.elapsed_time)
        self.label_current_song_elapsed.setText(duration_from_seconds(self.elapsed_time))

    def player_controller(self):
        if self.playing:
            self.playing = False
            self.update_timer.stop()
            self.play_button.setStyleSheet("border-image : url({});".format(PAUSE_ICON))
            mixer.music.pause()
        else:
            self.playing = True
            self.update_timer.start(1000)
            self.play_button.setStyleSheet("border-image : url({});".format(PLAY_ICON))
            mixer.music.unpause()

    def change_volume(self):
        # Volume == slider/30 because there are 30 steps and mixer only accepts volume > 0 and volume < 1
        volume = self.volume_slider.value()/30
        mixer.music.set_volume(volume)

    def next_song(self):
        next_song_index = self.playing_index + 1

        if next_song_index >= len(self.playlist):
            next_song_index = 0

        self.play_song(self.playlist[next_song_index])

        self.playing_index = next_song_index

    def previous_song(self):
        previous_song_index = self.playing_index - 1

        if previous_song_index < 0:
            previous_song_index = 0

        self.play_song(self.playlist[previous_song_index])

        self.playing_index = previous_song_index

    def change_song_timestamp(self):
        # Volume == slider/30 because there are 30 steps and mixer only accepts volume > 0 and volume < 1
        timestamp = self.slider_elapsed_time.value()
        self.elapsed_time = timestamp
        mixer.music.play(start=timestamp)

    def scan_songs(self):
        self.songs.clear()
        for folder in self.library_folders:
            for song_path in glob.glob(f"{folder}/*.mp3"):
                song_class = Song(song_path)
                self.songs.append(song_class)

        self.songs.sort(key=lambda s: s.title)
        self.playlist = deepcopy(self.songs)

    def open_config(self):
        self.config_window = ConfigScreen(self.library_folders)
        self.config_window.show()
        self.config_window.submitted.connect(self.update_library)

    def update_library(self, library_folders):
        self.library_folders.clear()
        self.library_folders.extend(library_folders)

        # Deletes current folder container, recreates it, then add to layout
        # also updates the reference to the widget self.folder_container
        temp_container = self.create_songs_container()

        self.layout().replaceWidget(self.songs_container, temp_container)

        self.songs_container = temp_container


mixer.init()
app = QApplication([])
mw = MainWindow("Player")
app.setStyle(QStyleFactory.create("fusion"))

app.exec_()


