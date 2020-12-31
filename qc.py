from os import path
from os import walk
from datetime import timedelta
from types import SimpleNamespace

from moviepy.editor import VideoFileClip
from moviepy.editor import *

matches = ['fuck']

def stitch(clips_dir, name):

    # find subtitles
    list_files = []
    for (dirpath, dirnames, filenames) in walk(clips_dir):
        for filename in filenames:
            if filename.endswith('.mp4') and not filename.startswith('._'):
                list_files.append(dirpath + '/' + filename)
    list_files.sort()

    clips = []
    for filename in list_files:
        clips.append(VideoFileClip(filename))

    # fade_duration = 1 # 1-second fade-in for each clip
    # clips = [clip.crossfadein(fade_duration) for clip in clips]

    final_clip = concatenate_videoclips(clips)

    # You can write any format, in any quality.
    final_clip.write_videofile("./"+name+".mp4", codec="libx264", temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')


def timestamp_to_sec(timestamp):
    timestamp = timestamp.replace(',','.')
    h, m, s = map(float, timestamp.split(':'))
    return timedelta(hours=h, minutes=m, seconds=s).total_seconds()


def main():

    mypath = './'

    # find subtitles
    srt_files = []
    for (dirpath, dirnames, filenames) in walk(mypath):
        for filename in filenames:
            if filename.endswith('.srt') and not filename.startswith('._'):
                srt_files.append(dirpath + '/' + filename)
    srt_files.sort()

    print("Found {} files".format(len(srt_files)))

    count = 0
    quotes = []

    # read each subtitle
    for srt_file in srt_files:
        basename = path.splitext(path.basename(srt_file))[0]
        for (index, timestamp, caption) in parse_subtitles(srt_file, matches):
            count += 1
            print(count, index, basename, timestamp, caption)

            quotes.append(SimpleNamespace(
                index=index,
                count=count,
                basename=basename,
                t_start=timestamp[0],
                t_end=timestamp[1],
                caption=caption,
                source= srt_file.replace('.srt', ".mkv")
            ))

   # trim clips
    for i, quote in enumerate(quotes):
        print("[{}/{}] Extracting clip... {}".format(i, len(quotes), " ".join(quote.caption)))
        
        outputfile = './clips/{} [{}] {}.mp4'.format(quote.count, quote.index, quote.basename)
        if path.exists(outputfile):
            print("Already Exist, skipping...")
            continue
        clip = VideoFileClip(quote.source).subclip(timestamp_to_sec(quote.t_start), timestamp_to_sec(quote.t_end))
        clip.to_videofile(outputfile, codec="libx264", temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')
    
    print('Done')

    print('Stitching clips together...')
    outputname = ' '.join(matches)
    stitch('./clips', outputname)

           

def parse_subtitles(filename, matches):
    with open(filename, mode='r', encoding='utf-8-sig') as file:

        index = 0
        timestamps = None
        captions = []

        line_no = 0

        while True:
            
            index = 0
            timestamps = None
            captions = []

            line_no += 1
            line = file.readline()
            if line.rstrip().isnumeric():
                index = int(line.rstrip())

                # read timestamp
                line_no += 1
                line = file.readline().rstrip()
                timestamps = line.split(" --> ")

                while True:
                    line_no += 1
                    line = file.readline().rstrip()
                    if line != "":
                        captions.append(line)
                    else:
                        break

                # print(index, timestamps, captions)

                sanitized_captions = ' '.join(captions).lower().encode("ascii", "ignore").decode()

                if any(x in sanitized_captions for x in matches):
                    yield (index, timestamps, captions)
                
            elif not line:
                # End of file
                break
            elif line.strip() == "":
                # Break line
                pass
            else:
                print('ERROR Reading line ({}:{})  "{}"'.format(filename, line_no, line))
                # raise NameError("Unexpected line content! ")

main()
