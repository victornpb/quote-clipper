import click
import re
from os import path
from os import walk
from datetime import timedelta
from types import SimpleNamespace
from pysubparser import parser
from moviepy.editor import VideoFileClip
from moviepy.editor import *
from pathvalidate import sanitize_filename

@click.command()
@click.argument('matches', required=True, nargs=-1)
@click.option('--directory','-dir','-d', type=click.Path(dir_okay=True), default=".", show_default=True, help="Directory to be scanned")
@click.option('--output','-o', 'outputname', type=click.Path(file_okay=True), help="Name of the output movie. [default: MATCHES.mp4]")
@click.option('--dry-run/--no-dry-run', type=bool, is_flag=True, help="Skip the generation of clips")
@click.option('--offset', '-t', 'offsets', type=(float, float), metavar='<start> <end>', default=[0.0, 0.0], show_default=True, help="Offset the start and end timestamps.\nFor example --offset -1.5 1.5 will make each clip 3s longer.")
@click.option('--regex','-re', 'is_regex', type=bool, is_flag=True, help="Interpret matches as regular expressions")

def main(matches, directory, outputname, dry_run, offsets, is_regex):
    print('QuoteClipper')

    matches = list(matches)
    if outputname:
        outputname = sanitize_filename(outputname)
    else:
        outputname = sanitize_filename(', '.join(matches) + '.mp4')

    print('Directory:',directory, 'Matches:',matches, 'Output:',outputname);

    # find subtitles
    print('\n=> Scanning folder {} for videos with srt subtitles...'.format(directory));
    episodes_list = []
    for (dirpath, _dirnames, filenames) in walk(directory):
        for filename in filenames:
            if filename.endswith('.srt') and not filename.startswith('._'):
                srt_file = dirpath + '/' + filename
                basename = path.splitext(path.basename(srt_file))[0]
                video_file = None

                # find corresponding video for the subtitle
                extensions = ['mp4', 'mkv']
                for ext in extensions:
                    test = srt_file.replace('.srt','.'+ext)
                    if path.exists(test):
                        video_file = test
                
                if video_file:
                    episode = SimpleNamespace(
                        srt=srt_file,
                        video=video_file,
                        basename=basename
                    )
                    episodes_list.append(episode)
                else:
                    print("     Found srt subtitle without corresponding video! ({})".format(srt_file))

    episodes_list = sorted(episodes_list, key=lambda k: k.srt)
    print("  Files found: {} videos with srt subtitles".format(len(episodes_list)))


    # read each subtitle
    print('\n=> Searching captions matching "{}" ...'.format('" or "'.join(matches)))

    if is_regex:
        matches = [re.compile(m, flags=re.I) for m in matches]
    else:
        matches = [re.compile(r"\b"+m+r"\b", flags=re.I) for m in matches]

    quotes = []
    for episode in episodes_list:
        print('\t* ', episode.basename)
        for caption in parser.parse(episode.subtitles_path):

            sanitized_captions = caption.text.strip().lower().encode("ascii", "ignore").decode()

            if test_text(sanitized_captions, matches):
                quote = SimpleNamespace(
                    episode=episode,
                    caption=caption,
                    clip=None,
                )
                quotes.append(quote)

                print('\t\t{} - [{} {} ~ {}] {}'.format(len(quotes), caption.index, caption.start, caption.end, caption.text))
        print('\t')
    print('  Done scanning subtitles! Quotes found: {}'.format(len(quotes)))


    if len(quotes) > 0 and dry_run==False:
        # trim clips
        print('\n=> Creating subclips...')
        clips = []
        for i, quote in enumerate(quotes):
            
            # outputfile = './clips/{} [{}] {}.mp4'.format(quote.count, quote.index, quote.basename)
            # if path.exists(outputfile):
            #     print("\tAlready Exist, skipping...")
            #     continue

            t1 = timestamp_to_sec(quote.caption.start) + offsets[0]
            t2 = timestamp_to_sec(quote.caption.end) + offsets[1]
            print("\t[{}/{}] Clipping... ({:.2f}s) {}".format(i, len(quotes), t2-t1, " | ".join(quote.caption.content)))
            clip = VideoFileClip(quote.episode.video).subclip(t1, t2)

            # clip.to_videofile(outputfile, codec="libx264", temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')
            clips.append(clip)
        print('  Done creating subclips!')


        # join clips into a single video
        print('\n=> Rendering {} clips together...'.format(len(clips)))

        # fade_duration = 1 # 1-second fade-in for each clip
        # clips = [clip.crossfadein(fade_duration) for clip in clips]

        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(outputname, codec="libx264", temp_audiofile=outputname+'~audio.m4a', remove_temp=True, audio_codec='aac')


    print('\nFinished!')
           

def test_text(string, tests):
    for test in tests:
        if test.search(string):
            return True
    return False

def timestamp_to_sec(timestamp):
    timestamp = timestamp.replace(',', '.')
    h, m, s = map(float, timestamp.split(':'))
    return float(timedelta(hours=h, minutes=m, seconds=s).total_seconds())


if __name__ == '__main__':
    main()