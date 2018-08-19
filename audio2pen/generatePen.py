#!/usr/bin/env python3
from cv2 import cv2
import numpy as np
import sys
from acoustic_feature import extract
from math import cos, sin, degrees, radians

WIDTH, HEIGHT = 33, 33
PITCH_MAX = 2000
SAMPLING_RATE = 44100

FILE_LISTS = [ "/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle18.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system32.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system26.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system27.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system33.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle19.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water13.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound18.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound24.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano1_g_chord.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum2_cymbal.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system25.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect14.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system31.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system19.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system18.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano2_2re.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect15.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system30.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system24.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum2_snare.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano2_6ra.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass13.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound19.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound21.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water14.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system20.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system34.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system35.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano1_1do.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system21.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water15.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound20.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound22.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass14.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano2_4fa.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_radio.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system37.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system23.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system22.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect13.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system36.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water16.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound23.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_syber05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_syber11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_drink01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_monster03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_car02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro23.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system45.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_ice01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_fire04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_fire10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_fire11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_fire05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum1_tom1.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system44.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro22.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano1_6ra.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_car03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical13.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_monster02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_thunder01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano1_2re.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle13.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_door01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_syber10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_syber04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_syber12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_syber06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_escape.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_door03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_drink02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint13.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_thunder03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_car01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_explosion08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system46.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro20.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano1_f_chord.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum1_tom3.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_ice02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_fire07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_fire06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_fire12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_ice03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum1_tom2.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro21.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system47.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_monster01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_thunder02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_door02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime13.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_syber07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_paper02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_syber03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_door06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint16.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_stairs.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano1_4fa.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical28.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical14.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_car04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro19.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system43.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro25.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_fire02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_ice07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_ice06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_fire03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro24.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro30.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system42.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro18.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_car05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical15.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical29.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint17.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_syber02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_paper01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_door05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime14.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint15.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_thunder05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint29.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical17.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_car07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drumroll.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro26.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system40.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_fire01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_ice04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_ice05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system41.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro27.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_car06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical16.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint28.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint14.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_thunder04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano2_1do.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_door04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_syber01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_pc02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_bird03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_footstep02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint19.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint31.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint25.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical27.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano2_5so.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro16.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_explosion02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_applause01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_explosion03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro17.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_whistle01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical26.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint24.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_ignition01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_heartbeat01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint30.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint18.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_bird02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_pc03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_pc01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_footstep01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_ignition03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint26.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint32.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical24.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical30.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical18.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro15.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro29.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_explosion01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro28.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro14.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical19.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical31.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical25.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint33.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint27.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_ignition02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_darkness04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_bird01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_bird05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint23.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum2_hat.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_wind03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_fall02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical21.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano1_3mi.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_explosion04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_explosion05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_phone01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical20.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_wind02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_horse01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_darkness01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint22.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_bird04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_jingle08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_noise01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_tiger01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_syber09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano1_c_chord.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint20.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_darkness03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical22.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_fall01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system49.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_explosion07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_phone03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro13.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_fire08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_fire09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano1_8do.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_retro06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_phone02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system48.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_explosion06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano2_7si.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_magical23.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_wind01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_darkness02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum1_bassdrum1.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_onepoint21.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_ignition04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_chime08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_syber08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle_gun02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_dog01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_human03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar14.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system13.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar15.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum2_bassdrum.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_human02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano1_am_chord.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_elevator01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound13.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle_gun03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle_gun01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_dog02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano1_5so.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum1_snare.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_elevator03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system38.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_effect08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system39.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle13.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_finger01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_insects01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_human01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_elevator02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound14.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle_gun04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_human05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar12.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar06.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle17.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system29.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system15.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum2_tom3.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum2_tom2.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system14.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system28.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle16.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_vehicle01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar07.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar13.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_element_water08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano1_7si.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_voice_human04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_switch01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle_gun05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound15.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass09.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound17.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_piano2_3mi.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar05.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar11.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum1_hat.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle14.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system16.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum2_tom1.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system03.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_system17.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle01.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_battle15.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_drum1_cymbal.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_vehicle02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar10.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_guitar04.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_switch02.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound16.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_instruments_bass08.ogg",
"/Users/yan/Downloads/ogg/se_maoudamashii_se_sound02.ogg" ]



def powerSpectrum2Brush(feature):
    ps = feature["power_spec"]
    db = int(max(feature["db"], -72) + 72)  # [0:72]
    p = feature["pitch"]

    img = np.ones((HEIGHT, WIDTH), dtype=np.uint8)*255
    deg = 45
    degdiff = max(db-30,0)
    step = int(SAMPLING_RATE / ((WIDTH-1) * 10))

    for t in range(deg-degdiff, deg+degdiff):
        for r in range(0, int(WIDTH/2)):
            x = int(r * cos(radians(t)) + WIDTH/2)
            y = int(r * sin(radians(t)) + HEIGHT/2)
            img[y, x] = 255-int(ps[r*step]*255)
            x = int(r * cos(radians(t+180)) + WIDTH/2)
            y = int(r * sin(radians(t+180)) + HEIGHT/2)
            img[y, x] = 255-int(ps[r*step]*255)

    #HSV時計周り方向に 青->緑->黄->赤->紫 で色がつくイメージ
    h = (180 - min(p / PITCH_MAX * 180, 180) + 120) % 180
    print(h)
    s = img
    v = np.ones((WIDTH, HEIGHT), dtype=np.uint8) * 255

    img_hsv = np.ndarray((WIDTH, HEIGHT, 3), dtype=np.uint8)
    for i, x in enumerate([h, s, v]):
        img_hsv[:, :, i] = x

    img_rgb = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2RGB)

    img_rgba = np.ndarray((WIDTH, HEIGHT, 4), dtype=np.uint8)
    for i, x in enumerate([img_rgb[:,:,2], img_rgb[:,:,1], img_rgb[:,:,0]]):
        img_rgba[:, :, i] = x

    img_rgba[:, :, 3] = 255-img

    return img_rgba

# feature => img


def generateBrush(feature):
    db = max(feature["db"], -72) + 72  # [0:72]

    img_filter = np.random.rand(WIDTH, HEIGHT)
    thr = db/72  # [0,1.0]
    p = feature["pitch"]
    print(thr)

    img_filter[img_filter > thr] = 255
    img_filter[img_filter < thr] = 0
    img_filter = img_filter.astype(np.uint8)

    print(p)

    h = (180 - min(p / PITCH_MAX * 180, 180) + 120) % 180
    s = np.ones((WIDTH, HEIGHT), dtype=np.uint8) * 255
    v = np.ones((WIDTH, HEIGHT), dtype=np.uint8) * 255

    for i in range(HEIGHT):
        for j in range(WIDTH):
            if(img_filter[i, j] == 255):
                s[i, j] = 0
                v[i, j] = 255

    img_hsv = np.ndarray((WIDTH, HEIGHT, 3), dtype=np.uint8)
    for i, x in enumerate([h, s, v]):
        img_hsv[:, :, i] = x

    img_rgb = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2RGB)
    return img_rgb


# for test
if __name__ == '__main__':
    # argc, argv = len(sys.argv), sys.argv
    # if argc != 5:
    #   print("usage: ./generatePen.py [WIDTH] [HEIGHT] [file-name] [audio-name]")
    #   quit()

    for file_name in FILE_LISTS:
        
        argv = ["xxx", "32", "32", file_name.replace(".wav", ".png"), file_name]

        # WIDTH, HEIGHT = [int(x) for x in argv[1:3]]
        file_name = argv[3]
        audio_name = argv[4]
        feature = extract(audio_name)
        # img = generateBrush(feature)
        img = powerSpectrum2Brush(feature)
        cv2.imwrite(file_name, img)
