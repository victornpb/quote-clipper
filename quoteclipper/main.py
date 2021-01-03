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
@click.argument('directory', type=click.Path(dir_okay=True, exists=True, resolve_path=True), default=".")
@click.option('--match', '-m', 'tokens', type=str, required=True, multiple=True)
@click.option('--output', '-o', 'outputname', type=click.Path(file_okay=True, writable=True), help="Name of the output movie. [default: MATCHES.mp4]")
@click.option('--dry-run/--no-dry-run', type=bool, is_flag=True, help="Skip the generation of clips")
@click.option('--offset', '-t', 'offsets', type=(float, float), metavar='<start> <end>', default=[0.0, 0.0], show_default=True, help="Offset the start and end timestamps.\nFor example --offset -1.5 1.5 will make each clip 3s longer.")
@click.option('--case-sensitive', '-c', 'case_sensitive', is_flag=True, help="Case sensitive match (ignored by --regex)")
@click.option('--regex', '-re', 'is_regex', type=bool, is_flag=True, help="Interpret matches as regular expressions. Example '/foo \w+/i' ")
def main(tokens, directory, outputname, dry_run, offsets, is_regex, case_sensitive):
    """A tool for finding quotes in series/movies/animes and automatically creating compilations.

    \b
    Examples:
    $ quoteclipper -match Hello .
    $ quoteclipper -m "Morning" -m "Good Night" ./videos
    $ quoteclipper -o ~/Desktop/greetings.mp4 -m 'Hello' -m 'Hi' -m 'Whassup' .
    $ quoteclipper -re -m /Call 555.\d+/i 
    $ quoteclipper -re -m /Car?s|sandwich(es)?/i .
    """
    print('QuoteClipper')
    print('Directory:', directory, 'Matches:', tokens, 'Output:', outputname)
    
    tokens = list(tokens)

    if not outputname:
        terms = ', '.join(tokens)
        outputname = sanitize_filename('Compilation of %s.mp4' % terms)

    if is_regex:
        search_regxps = [regexp(m) for m in tokens]
    else:
        f = (re.I if case_sensitive == False else 0)
        search_regxps = [re.compile(r"\b"+m+r"\b", flags=f) for m in tokens]



    # find subtitles
    print('\n=> Scanning folder {} for videos with srt subtitles...'.format(directory))
    episodes_list = []
    for (dirpath, _dirnames, filenames) in walk(directory):
        for filename in filenames:
            if filename.endswith(('.mp4', '.mkv')) and not filename.startswith('._'):
                video_path = path.join(dirpath, filename)
                subtitles_path = None
                basename = path.splitext(path.basename(video_path))[0]

                # find corresponding subtitle file
                for ext in ['srt', 'ssa', 'ass', 'sub', 'txt']:
                    test = path.join(dirpath, basename + '.' + ext)
                    if path.isfile(test):
                        subtitles_path = test
                        break

                if subtitles_path:
                    episode = SimpleNamespace(
                        basename=basename,
                        video_path=video_path,
                        subtitles_path=subtitles_path,
                    )
                    episodes_list.append(episode)
                    print("\t* {}".format(subtitles_path))
                else:
                    print("\tNo subtitles found! {}".format(video_path))

    episodes_list = sorted(episodes_list, key=lambda k: k.basename)
    print("  Files found: {} videos with subtitles".format(len(episodes_list)))

    # read each subtitle
    print('\n=> Searching captions matching "{}" ...'.format('" or "'.join(tokens)))

    quotes = []
    for episode in episodes_list:
        print('\t* ', episode.basename)
        for caption in parser.parse(episode.subtitles_path):

            sanitized_captions = caption.text.strip().encode("ascii", "ignore").decode()

            if test_text(sanitized_captions, search_regxps):
                quote = SimpleNamespace(
                    episode=episode,
                    caption=caption,
                    clip=None,
                )
                quotes.append(quote)

                print('\t\t{} - [{} {} ~ {}] {}'.format(len(quotes),
                                                        caption.index, caption.start, caption.end, caption.text))
        print('\t')
    print('  Done scanning subtitles! Quotes found: {}'.format(len(quotes)))

    if len(quotes) > 0 and dry_run == False:
        # trim clips
        print('\n=> Creating subclips...')
        clips = []
        for i, quote in enumerate(quotes):

            t1 = time_to_seconds(quote.caption.start) + offsets[0]
            t2 = time_to_seconds(quote.caption.end) + offsets[1]
            print("\t[{}/{}] Clipping... ({:.2f}s) {}".format(i,
                                                              len(quotes), t2-t1, quote.caption.text))
            clip = VideoFileClip(quote.episode.video_path).subclip(t1, t2)

            # outputfile = './clips/{} [{}] {}.mp4'.format(quote.count, quote.index, quote.basename)
            # if path.exists(outputfile):
            #     print("\tAlready Exist, skipping...")
            #     continue
            # clip.to_videofile(outputfile, codec="libx264", temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')

            clips.append(clip)
            quote.clip = clip
        print('  Done creating subclips!')

        # join clips into a single video
        print('\n=> Rendering {} clips together...'.format(len(clips)))

        # fade_duration = 1 # 1-second fade-in for each clip
        # clips = [clip.crossfadein(fade_duration) for clip in clips]

        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(
            outputname, codec="libx264", temp_audiofile=outputname+'~audio.m4a', remove_temp=True, audio_codec='aac')

        # Generate new subtitles
        print('\n=> Creating new subtitles...')
        start = 0
        new_subtitles = []
        for i, quote in enumerate(quotes):
            end = start + quote.clip.duration
            line = SimpleNamespace(index=i+1, start=seconds_to_hhmmssms(start),
                                   end=seconds_to_hhmmssms(end), text=quote.caption.text)
            start = end
            new_subtitles.append(line)

        template = "{index}{eol}{start} --> {end}{prop}{eol}{text}{eol}"
        new_subtitles = [template.format(
            index=c.index,
            start=c.start,
            end=c.end,
            prop='',
            text=c.text,
            eol='\n',
        ) for c in new_subtitles]
        new_srt = '\n'.join(new_subtitles)

        with open(path.splitext(outputname)[0] + '.srt', 'wb') as file:
            file.write(new_srt.encode('utf8'))
        print('  Done creating new subtitles!')

    print('\nFinished!')


def test_text(string, regex_list):
    for regex in regex_list:
        if regex.search(string):
            return True
    return False


def time_to_seconds(time):
    s = time.second + (time.microsecond/1000000)
    return timedelta(hours=time.hour, minutes=time.minute, seconds=s).total_seconds()


def seconds_to_hhmmssms(sec):
    d = timedelta(seconds=sec)
    hrs, secs_remainder = divmod(d.seconds, 3600)
    hrs += d.days * 24
    mins, secs = divmod(secs_remainder, 60)
    msecs = d.microseconds / 1000
    return "%02d:%02d:%02d,%03d" % (hrs, mins, secs, msecs)


def regexp(string):
    m = re.match(r'^/(.*)/([aidlmsuxv]*)$', string, flags=re.DOTALL)
    if m:
        regex = m.group(1)
        f = m.group(2)
        flags = (
            (re.ASCII if 'a' in f else 0) |
            (re.IGNORECASE if 'i' in f else 0) |
            (re.DEBUG if 'd' in f else 0) |
            (re.LOCALE if 'l' in f else 0) |
            (re.MULTILINE if 'm' in f else 0) |
            (re.DOTALL if 's' in f else 0) |
            (re.UNICODE if 'u' in f else 0) |
            (re.VERBOSE if 'x' in f or 'v' in f else 0)
        )
        try:
            return re.compile(regex, flags=flags)
        except BaseException as err:
            raise click.BadOptionUsage('tokens', f'Bad regular expression!\n{regex}\n{err}')
    else:
        raise click.BadOptionUsage('tokens', f'Not a Regexp value!\n{string}\nRegular expression should be /re/ delimited. (https://en.wikipedia.org/wiki/Regular_expression#Delimiters)')


if __name__ == '__main__':
    main()
