import argparse
from os import path
from os import walk
from datetime import timedelta
from types import SimpleNamespace

from moviepy.editor import VideoFileClip
from moviepy.editor import *


def timestamp_to_sec(timestamp):
    timestamp = timestamp.replace(',','.')
    h, m, s = map(float, timestamp.split(':'))
    return timedelta(hours=h, minutes=m, seconds=s).total_seconds()


def main(matches):

    mypath = './'

    # find subtitles
    print('\n=> Scanning folder for subtitle files...');
    srt_files = []
    for (dirpath, dirnames, filenames) in walk(mypath):
        for filename in filenames:
            if filename.endswith('.srt') and not filename.startswith('._'):
                srt_files.append(dirpath + '/' + filename)
    srt_files.sort()
    print("  Subtitles found: {} files.".format(len(srt_files)))


    # read each subtitle
    print('\n=> Searching subtitles matching {} ...'.format(matches))
    quotes = []
    for srt_file in srt_files:
        basename = path.splitext(path.basename(srt_file))[0]
        print('\t* ', basename)
        for matched_caption in parse_subtitles(srt_file, matches):
            print('\t\t{} - [{} {} ~ {}] {}'.format(len(quotes), matched_caption.index, matched_caption.t_start, matched_caption.t_end, ' | '.join(matched_caption.captions)))

            quotes.append(SimpleNamespace(
                count=len(quotes),
                index=matched_caption.index,
                t_start=matched_caption.t_start,
                t_end=matched_caption.t_end,
                captions=matched_caption.captions,
                basename=basename,
                source= srt_file.replace('.srt', ".mkv")
            ))
        print('\t')
    print('  Done scanning subtitles! Quotes found: {}'.format(len(quotes)))


    # trim clips
    print('\n=> Creating subclips...')
    clips = []
    for i, quote in enumerate(quotes):
        print("\t[{}/{}] Clipping... {}".format(i, len(quotes), " | ".join(quote.captions)))
        
        outputfile = './clips/{} [{}] {}.mp4'.format(quote.count, quote.index, quote.basename)
        if path.exists(outputfile):
            print("\tAlready Exist, skipping...")
            continue
        clip = VideoFileClip(quote.source).subclip(timestamp_to_sec(quote.t_start), timestamp_to_sec(quote.t_end))
        # clip.to_videofile(outputfile, codec="libx264", temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')
        clips.append(clip)
    print('  Done creating subclips!')


    # join clips into a video
    print('\n=> Stitching {} clips together...'.format(len(clips)))
    outputname = ', '.join(matches)

    # fade_duration = 1 # 1-second fade-in for each clip
    # clips = [clip.crossfadein(fade_duration) for clip in clips]

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile("./"+outputname+".mp4", codec="libx264", temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')


    print('\nFinished!')
           

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
                    yield SimpleNamespace(index=index, t_start=timestamps[0], t_end=timestamps[1], captions=captions)
                
            elif not line:
                # End of file
                break
            elif line.strip() == "":
                # Break line
                pass
            else:
                print('ERROR Reading line ({}:{})  "{}"'.format(filename, line_no, line))
                # raise NameError("Unexpected line content! ")


parser = argparse.ArgumentParser()
parser.add_argument("--match", "-m", nargs='+', required=True, help="Define matches")

# Read arguments from the command line
args = parser.parse_args()

main(args.match)
