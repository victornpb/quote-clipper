from os import walk
import subprocess
import re
from os import path

tool_path = "/Applications/MKVToolNix-51.0.0.app/Contents/MacOS/"
dir = "./"

def find_files(dir, ext):
    file_list = []
    for (dirpath, dirnames, filenames) in walk(dir):
        for filename in filenames:
            if filename.endswith(ext) and not filename.startswith('._'):
                file_list.append(dirpath + '/' + filename)
    file_list.sort()
    return file_list

for file in find_files(dir, ".mkv"):
    basename = file.replace(".mkv", "")
    
    if path.exists(basename+".srt") or path.exists(basename+".ssa"):
        print("Already Exist, skipping...", basename)
        continue

    # Find subtitle track
    result = subprocess.run([tool_path + "mkvmerge", "-i", file], stdout=subprocess.PIPE, check=True)
    
    # SubRip .srt
    srt_track = re.search(r'Track ID (\d+): subtitles \(SubRip/SRT\)', str(result.stdout)) 
    if srt_track:
        srt_track = "{}:{}.{}".format(srt_track.group(1), basename, "srt")

    # SubStation Alpha .ssa
    ssa_track = re.search(r'Track ID (\d+): subtitles \(SubStationAlpha\)', str(result.stdout)) 
    if ssa_track:
        ssa_track = "{}:{}.{}".format(ssa_track.group(1), basename, "ssa")

    if not srt_track and not ssa_track:
        print('No SRT track found!', file, str(result.stdout))
        continue


    # Extract SRT
    subprocess.run(list(filter(None, [tool_path+"mkvextract", "tracks", file, srt_track, ssa_track])), check=True)

print("Finished!");
