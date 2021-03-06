#!/usr/bin/python3

# HLS transcoder/transmuxer.  Converts an input video into multiple output streams.

import sys
import os
import pymediainfo
import getch
import math
import argparse
import re
import tmdbsimple as tmdb
import time
import subprocess
import json
import pathlib

# Possible output resolutions and their associated maximum bitrates.
# Resolutions that are larger than the input media will be dropped.
# An original quality stream will also be produced.
# Output bitrate is clamped to input bitrate.
output_resolutions = [
    #RES   VRATE  FORCE
    #[144,  1000],
    #[240,  1000,  False],
    #[360,  2000,  False],
    #[480,  3000,  False],
    [720,  6000,  False],
    [1080, 10000, True],
    [2160, 25000, False]
]

# Encoding options
encoding_options = {
    # Preset determines encoding speed.  Options are [ultrafast, superfast,
    # veryfast, faster, fast, medium (default), slow, slower, veryslow, and
    # placebo (do not use)]
    "preset": "veryslow",
    # Keyframes interval, spec says 2 seconds
    "keyframes_interval": 2,
    # Seconds per HLS segment, should be a multiple of `keyframes_interval`
    "segment_size": 6,
    # Audio bitrate
    "audio_bitrate": "500k",
    # Codec
    "video_codec": "libx265"
}

##############################
# Parse Command Line Options #
##############################

parser = argparse.ArgumentParser(description='Transcode a media file into a multi-quality HLS stream')
parser.add_argument('input', metavar="i", type=str,
    help="path to the input file")
parser.add_argument('output', metavar="o", type=str,
    help="media output name without extension")

args = parser.parse_args()

#######################
# Validate user input #
#######################

input_file_name = args.input
if not os.path.exists(input_file_name):
    print("\033[31mError: Input file does not exist\033[0m")
    exit(-1)

output_name = args.output
if not re.match(r"[a-zA-Z0-9_]*", output_name):
    print("\033[31mError: Output name contains illegal characters\033[0m")
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
        bitrate = track.bit_rate or track.nominal_bit_rate or 10000000
        fps = float(track.frame_rate) if track.frame_rate else 24.0
        print(f"    Resolution: \033[33m{track.width}x{track.height}\033[0m")
        print(f"    Bitrate: \033[33m{int(bitrate/1000)}kbps\033[0m")
        print(f"    Framerate: \033[33m{track.frame_rate}\033[0m")
        print(f"    Track ID: \033[33m{track.track_id}\033[0m")
        print(f"    Codec: \033[33m{track.codec_id_url}\033[0m")
        #print(dir(track))
        normalized_media_info.append({
            "type": "video",
            "num": i,
            "width": track.width,
            "height": track.height,
            "bitrate": track.bit_rate or track.nominal_bit_rate or 10000000,
            "fps": fps,
            "id": track.track_id - 1
        })
    elif track.track_type == "Audio":
        bitrate = track.bit_rate or track.nominal_bit_rate or -1000
        print(f"    Languate: \033[33m{track.language}\033[0m")
        print(f"    Bitrate: \033[33m{int(bitrate/1000)}kbps\033[0m")
        print(f"    Track ID: \033[33m{track.track_id}\033[0m")
        normalized_media_info.append({
            "type": "audio",
            "num": i,
            "language": track.language,
            "bitrate": track.bit_rate or track.nominal_bit_rate,
            "id": track.track_id - 1
        })
    elif track.track_type == "Text":
        print(f"    Language: \033[33m{track.language}\033[0m")
        normalized_media_info.append({
            "type": "text",
            "num": i,
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
def getyn():
    while True:
        c = getch.getch()
        if c == "Y" or c == "y":
            return "Y"
        elif c == "N" or c == "n":
            return "N"
# Attempt automatic track selection
autoselected = False
if True:
    duplicate = False
    video = None
    audio = None
    for track in normalized_media_info:
        if track is None: continue
        if track['type'] == 'audio':
            if audio is not None:
                duplicate = True
            else:
                audio = track['num']
        if track['type'] == 'video':
            if video is not None:
                duplicate = True
            else:
                video = track['num']
    if audio is not None and video is not None and not duplicate:
        selected_tracks['Audio'] = [audio]
        selected_tracks['Video'] = [video]
        autoselected = True
        print(f"Automatically selected video track \033[32m{video+1}\033[0m and audio track \033[32m{audio+1}\033[0m")
while True:
    if autoselected: break
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
    if getyn() == "N":
        continue
    selected_tracks = tracks
    break

##################################
# Get Extended Media Information #
##################################

print("Collecting extended media information for this title.")
extended_info = {
    "title": "",
    "year": "",
    "poster": "",
    "rating": "",
    "overview": "",
    "categories": ""
}
tmdb.API_KEY = open(os.path.expanduser("~/.config/tmdb/key"),"r").read()
tmdbsearch = tmdb.Search()
tmdbgenres = tmdb.Genres().movie_list()
genres = {}
for x in tmdbgenres['genres']: genres[x['id']] = x['name']
def getnum(min,max,msg):
    while True:
        raw = input(f"{msg}\033[32m")
        print("\033[0m",end="")
        try:
            value = int(raw)
            if value == "cancel":
                return None
            if value < min or value >= max:
                print("Out of range")
            return value
        except ValueError:
            print("Not a number")
while True:
    raw_movie_title = input("Movie Title for TMDb Query: \033[32m")
    print("\033[0m",end="")

    if raw_movie_title == "manual": break
    if raw_movie_title == "skip":
        extended_info['title'] = "skipped"
        extended_info['year'] = 0000
        extended_info['poster'] = "skipped"
        extended_info['rating'] = -1
        extended_info['overview'] = "skipped"
        extended_info['categories'] = "skipped"
        break

    print("Executing query...")
    results = []
    nextpage = 1
    while True:
        print(f"Querying page {nextpage}")
        try:
            tmdbresp = tmdbsearch.movie(query=raw_movie_title,page=nextpage)
        except:
            print("\033[31mError:\033[0m Failed to query database, try again!")
            break
        results += tmdbresp['results']
        if tmdbresp['page'] >= tmdbresp['total_pages']:
            break
        nextpage += 1
        time.sleep(.5)
    if(len(results) == 0):
        print("\033[31mError:\033[0m That movie was not found in TMDb")
        print("Enter another query or type \"manual\" to manually enter information")
        continue
    if(len(results) == 1):
        selected_movie = results[0]
    else:
        print("Found multiple movies!")
        for i, movie in enumerate(results):
            print(f"  {i}: \033[33m{movie['title']} \033[34m{movie['release_date'][0:4]}\033[0m")
        print("Enter a number or \"cancel\" to try a different query")
        num = getnum(0,len(results), "Movie: ")
        if num is None:
            continue
        selected_movie = results[num]

    print("Currently Selected:")
    print(f"  Title: \033[33m{selected_movie['title']}\033[0m")
    print(f"  Release Date: \033[33m{selected_movie['release_date']}\033[0m")
    categories = ", ".join([genres[x] for x in selected_movie['genre_ids']])
    print(f"  Categories: \033[33m{categories}\033[0m")
    print(f"  Poster: \033[33mhttps://image.tmdb.org/t/p/original{selected_movie['poster_path']}\033[0m")
    print(f"  Overview: \033[33m{selected_movie['overview']}\033[0m")
    print("Press \033[32mY\033[0m to confirm, \033[32mN\033[0m to retry:")
    if getyn() == "Y":
        extended_info['title'] = selected_movie['title']
        extended_info['year'] = selected_movie['release_date'][0:4]
        extended_info['poster'] = f"https://image.tmdb.org/t/p/original{selected_movie['poster_path']}"
        extended_info['rating'] = selected_movie['vote_average']
        extended_info['overview'] = selected_movie['overview']
        extended_info['categories'] = categories
        break

if extended_info['title'] == "":
    extended_info['title'] = input("Title: \033[32m")
    print("\033[0m",end="")
if extended_info['year'] == "":
    extended_info['year'] = input("Year: \033[32m")
    print("\033[0m",end="")
if extended_info['poster'] == "":
    extended_info['poster'] = input("Poster URL: \033[32m")
    print("\033[0m",end="")
if extended_info['rating'] == "":
    extended_info['rating'] = getnum(0,10.001, "Rating (/10): ")
    print("\033[0m",end="")
if extended_info['overview'] == "":
    extended_info['overview'] = input("Overview: \033[32m")
    print("\033[0m",end="")
if extended_info['categories'] == "":
    extended_info['categories'] = input("Categories: \033[32m")
    print("\033[0m",end="")

####################
# Generate outputs #
####################

video_track = normalized_media_info[selected_tracks["Video"][0]]
audio_track = normalized_media_info[selected_tracks["Audio"][0]]
output_params = []
for _resolution, _bitrate, _force in output_resolutions:
    if _resolution - 100 > video_track["height"] and not _force: continue
    bitrate = min(_bitrate, video_track["bitrate"] / 1000)
    # TESTING OVERRIDE - ALWAYS USE PRESET BITRATE
    bitrate = _bitrate
    resy = min(_resolution, video_track["height"])
    resx = int(video_track["width"] * (resy / video_track["height"]))
    if resx % 2 != 0:
        resx -= 1
    if resy % 2 != 0:
        resy -= 1
    # If resolution is unchanged, copy instead of transcoding
    output_params.append({
        "resname": f"{resy}p",
        "resx": resx,
        "resy": resy,
        "bitrate": bitrate
    })
    print(f"\033[33m{resy}p\033[0m @ \033[33m{bitrate}k\033[0m")

rootpath = pathlib.Path(__file__).parent.absolute()

# The ffmpeg command can be broken down into a few major parts.
# `inputenc`: Input and encoding arguments specyf input files and general encoding parameters
# `mapping`: Specifies the stupidly complicated ffmpeg mapping parameters
# `streams`: Specifies the encoding parameters for each of the quality streams
# `output`: Specifies how the resulting data should be written out

ffmpeg_params = {
    "inputenc": [],
    "mapping": [],
    "streams": [],
    "output": [],
    "filters": []
}

ffmpeg_params["inputenc"].append((None,"-hide_banner -loglevel warning -stats"))
ffmpeg_params["inputenc"].append(("analyzeduration","15000000")) # 15 seconds
ffmpeg_params["inputenc"].append(("probesize","15000000")) # 15 MB
ffmpeg_params["inputenc"].append(("i", f'"{input_file_name}"'))
ffmpeg_params["inputenc"].append(("g", math.ceil(video_track['fps'] * encoding_options['keyframes_interval'])))
ffmpeg_params["inputenc"].append(("sc_threshold", 0))
ffmpeg_params["inputenc"].append(("c:a", "aac")) # aac required for mp4
ffmpeg_params["inputenc"].append(("b:a", encoding_options['audio_bitrate'])) # good enough
ffmpeg_params["inputenc"].append(("pix_fmt", "yuv420p"))
ffmpeg_params["inputenc"].append(("to", "00:05:00.00"))
ffmpeg_params["output"].append(("max_muxing_queue_size", "1500"))
ffmpeg_params["output"].append(("ac", "2")) # Downmix to 2 channel audio
ffmpeg_params["output"].append(("master_pl_name", f"{output_name}.m3u8")) # TODO: customize
ffmpeg_params["output"].append(("f", "hls"))
ffmpeg_params["output"].append(("hls_time", encoding_options["segment_size"]))
ffmpeg_params["output"].append(("hls_list_size", 0)) # 0 is unlimited
ffmpeg_params["output"].append(("hls_segment_filename", f"{rootpath}/site/media/{output_name}/q_%v/seg%d.ts"))
ffmpeg_params["output"].append(("hls_playlist_type", "event"))
ffmpeg_params["output"].append((None, f"{rootpath}/site/media/{output_name}/q_%v/index.m3u8"))

# Generate mappings
var_stream_map = ""
for i, param in enumerate(output_params):
    # Generate the filter graph component
    filters = []
    #`filters.append(f"drawtext=fontfile=/home/nicholas/.local/share/fonts/Roboto-Medium.ttf:text='Codec\\: {encoding_options['video_codec']}':fontcolor=black:fontsize=90:x=2245:y=1445")
    #filters.append(f"drawtext=fontfile=/home/nicholas/.local/share/fonts/Roboto-Medium.ttf:text='Codec\\: {encoding_options['video_codec']}':fontcolor=#c0212f:fontsize=90:x=2240:y=1440")
    #filters.append(f"drawtext=fontfile=/home/nicholas/.local/share/fonts/Roboto-Medium.ttf:text='Bitrate\\: {param['bitrate']}kbps':fontcolor=black:fontsize=90:x=2245:y=1545")
    #filters.append(f"drawtext=fontfile=/home/nicholas/.local/share/fonts/Roboto-Medium.ttf:text='Bitrate\\: {param['bitrate']}kbps':fontcolor=#c0212f:fontsize=90:x=2240:y=1540")
    #filters.append(f"drawtext=fontfile=/home/nicholas/.local/share/fonts/Roboto-Medium.ttf:text='Resolution\\: {param['resx']}x{param['resy']}':fontcolor=black:fontsize=90:x=2245:y=1645")
    #filters.append(f"drawtext=fontfile=/home/nicholas/.local/share/fonts/Roboto-Medium.ttf:text='Resolution\\: {param['resx']}x{param['resy']}':fontcolor=#c0212f:fontsize=90:x=2240:y=1640")
    #filters.append(f"drawtext=fontfile=/home/nicholas/.local/share/fonts/Roboto-Medium.ttf:text='Frame\\: %{{frame_num}}':fontcolor=black:fontsize=90:x=2245:y=1745")
    #filters.append(f"drawtext=fontfile=/home/nicholas/.local/share/fonts/Roboto-Medium.ttf:text='Frame\\: %{{frame_num}}':fontcolor=#c0212f:fontsize=90:x=2240:y=1740")
    filters.append(f"scale={param['resx']}:{param['resy']}")
    filterstr = ",".join(filters)
    filterstr = f"[0:{video_track['id']}]{filterstr}[vtrack{i}];[0:{audio_track['id']}]anull[atrack{i}]"
    #filterstr = f"[0:v]{filterstr}[vtrack{i}];[1:a]anull[atrack{i}]"
    ffmpeg_params["filters"].append(filterstr)
    ffmpeg_params["mapping"].append(("map", f"[vtrack{i}]"))
    ffmpeg_params["mapping"].append(("map", f"[atrack{i}]"))
    ffmpeg_params["streams"].append((f"c:v:{i}", encoding_options['video_codec']))
    ffmpeg_params["streams"].append(("preset", encoding_options['preset']))
    ffmpeg_params["streams"].append((f"b:v:{i}", f"{param['bitrate']}k"))
    var_stream_map += f"v:{i},a:{i} "
filternet = ";".join(ffmpeg_params["filters"])
print(filternet)
ffmpeg_params["streams"].append(("filter_complex", f'"{filternet}"'))
ffmpeg_params["streams"].append(("var_stream_map", f'"{var_stream_map[:-1]}"'))


print("Generating command...")
command = f"time nice -n 19 /usr/bin/ffmpeg "
for param in (ffmpeg_params["inputenc"] + ffmpeg_params["mapping"] + ffmpeg_params["streams"] + ffmpeg_params["output"]):
    if param[0] is not None:
        command += f"-{param[0]} {param[1]} "
    else:
        command += f"{param[1]} "

#print("debug")
print(f"\033[31m{command}\033[0m")
print("Write to job file?")
if getyn() == "Y":
    jobfile = open('job.sh','a')
    jobfile.write(f"echo Transcoding \033[33m{output_name}\033[0m...\n")
    jobfile.write(f"time {command}\n")
else:
    print("Transcoding...")
    subprocess.run(command, shell=True)

print("Generating media manifest file...")
media_manifest = {}
media_manifest.update(extended_info)
media_manifest['resolutions'] = []
for output in output_params:
    media_manifest['resolutions'].append(f"{output['resname']} @ {output['bitrate']}k")
mfile = open(f"{rootpath}/site/media/{output_name}.json","w")
mfile.write(json.dumps(media_manifest))
mfile.close()

print("\033[42;1m DONE! \033[0m")
