#!/usr/bin/python3

# HLD transcoder/transmuxer.  Converts an input video into multiple output streams.

import sys
import os
import pymediainfo
import getch

# Possible output resolutions and their associated maximum bitrates.
# Resolutions that are larger than the input media will be dropped.
# An original quality stream will also be produced.
# Output bitrate is clamped to input bitrate.
output_resolutions = [
    [144, 1000],
    [240, 1000],
    [360, 1000],
    [480, 2500],
    [720, 5000],
    [1080, 10000],
    [2160, 20000]
]

#######################
# Validate user input #
#######################

if len(sys.argv) != 2:
    print("\033[31mError: Missing input file name\033[0m")
    print(f"Usage: {sys.argv[0]} <filename>")
    exit(-1)

input_file_name = sys.argv[1]
if not os.path.exists(input_file_name):
    print("\033[31mError: Input file does not exist\033[0m");
    exit(-1)

###################################
# Get media and track information #
###################################

supported_track_types = ["Video","Audio","Text"]
input_media_info = pymediainfo.MediaInfo.parse(input_file_name)
normalized_media_info = []
print(f"Input file contains \033[32m{len(input_media_info.tracks)}\033[0m tracks:")
for i, track in enumerate(input_media_info.tracks):
    print(f"  \033[32m{i+1}\033[0m: {track.track_type}")
    if track.track_type == "Video":
        bitrate = track.bit_rate or track.nominal_bit_rate or -1000
        print(f"    Resolution: \033[33m{track.width}x{track.height}\033[0m")
        print(f"    Bitrate: \033[33m{int(bitrate/1000)}kbps\033[0m")
        normalized_media_info.append({
            "width": track.width,
            "height": track.height,
            "bitrate": track.bit_rate or track.nominal_bit_rate
        })
    elif track.track_type == "Audio":
        bitrate = track.bit_rate or track.nominal_bit_rate or -1000
        print(f"    Languate: \033[33m{track.language}\033[0m")
        print(f"    Bitrate: \033[33m{int(bitrate/1000)}kbps\033[0m")
        normalized_media_info.append({
            "language": track.language,
            "bitrate": track.bit_Rate or track.nominal_bit_rate
        })
    elif track.track_type == "Text":
        print(f"    Language: \033[33m{track.language}\033[0m")
        normalized_media_info.append({
            "language": track.language
        })
    else:
        print(f"    \033[3mThis track type is not supported and will not be transmuxed\033[0m")
        normalized_media_info.append(None)

selected_tracks = {
    "Audio": [],
    "Video": [],
    "Text": []
}
while True:
    selected_tracks_raw = input("Select tracks: \033[32m")
    print("\033[0m",end="")
    tracks = {
        "Audio": [],
        "Video": [],
        "Text": []
    }
    errored = False
    for i in selected_tracks_raw.split(" "):
        try:
            value = int(i) - 1
            if value < 0 or value >= len(input_media_info.tracks):
                print(f"\033[31mError:\033[0m Track \033[32m{i}\033[0m is out of range")
                errored = True
                continue
            ttype = input_media_info.tracks[value].track_type
            if ttype not in supported_track_types:
                print(f"\033[31mError:\033[0m Track \033[32m{i}\033[0m is of unsupported type \033[32m{ttype}\033[0m")
                errored = True
                continue
            if value in tracks[ttype]:
                print(f"\033[33mWarning:\033[0m Track \033[32m{i}\033[0m selected multiple times")
            else:
                tracks[ttype].append(value)
        except ValueError:
            print(f"\033[31mError:\033[0m Input \033[32m{i}\033[0m is not a valid number")
            errored = True
    if len(tracks["Video"]) == 0:
        print("\033[31mError:\033[0m No video track was selected!")
        errored = True
    if len(tracks["Video"]) > 1:
        print("\033[31mError:\033[0m Multiple video tracks selected, this is not supported :(")
        errored= True
    # Temporarily block multiple audio and subtitle tracks because I'm not sure if I can actually make that work
    if len(tracks["Audio"]) == 0:
        print("\033[31mError:\033[0m No audio track was selected!")
        errored = True
    if len(tracks["Audio"]) > 1:
        print("\033[31mError:\033[0m Multiple audio tracks selected, this is not supported :(")
        errored = True
    if len(tracks["Text"]) > 1:
        print("\033[31mError:\033[0m Multiple subtitle tracks selected, this is not supported :(")
        errored = True

    if errored:
        print("\033[31mInvalid selection, please try again\033[0m")
        continue
    print(f"You selected:")
    print(f"  Video Track: \033[32m{' '.join([str(x+1) for x in tracks['Video']])}\033[0m")
    print(f"  Audio Track(s): \033[32m{' '.join([str(x+1) for x in tracks['Audio']])}\033[0m")
    print(f"  Text Track(s): \033[32m{' '.join([str(x+1) for x in tracks['Text']])}\033[0m")
    print("Press \033[32mY\033[0m to confirm, \033[32mN\033[0m to change")
    while True:
        c = getch.getch()
        if c == "Y" or c == "y":
            break
        elif c == "N" or c == "n":
            errored = True
            break
    if errored: continue
    selected_tracks = tracks
    break

####################
# Generate outputs #
####################

video_track = normalized_media_info[selected_tracks["Video"][0]]
output_params = []
for _resolution, _bitrate in output_resolutions:
    if _resolution > video_track["height"]: continue
    bitrate = min(_bitrate, video_track["bitrate"])
    output_params.append(_resolution)