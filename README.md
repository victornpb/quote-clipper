# Quote Clipper

![quote-clipper](https://user-images.githubusercontent.com/3372598/175794893-c98b9be2-4f8b-4969-88a4-dd43b2af97d9.jpg)

A CLI Tool for finding quotes in series/movies/animes and automatically creating video compilations.

# Usage
```
Usage: quoteclipper [OPTIONS] [DIRECTORY]

Options:
  -m, --match TEXT                [required]
  -o, --output PATH               Name of the output movie.  [default:
                                  ./Compilation of {}.mp4]

  -e, --export-clips              Export individual clips
  -ed, --export-clips-dir PATH    Directory to export clips to (must exist)
                                  [default: .]

  -et, --export-clips-template TEXT
                                  Template to be used as clips filenames.
                                  (Variables: n, index, basename, quote,
                                  start, end, duration)  [default: {n} -
                                  {quote}.mp4]

  --dry-run / --no-dry-run        Skip the generation of clips
  -t, --offset <start> <end>      Offset the start and end timestamps. For
                                  example --offset -1.5 1.5 will make each
                                  clip 3s longer.  [default: 0.0, 0.0]

  -c, --case-sensitive            Case sensitive match (ignored by --regex)
  -re, --regex                    Interpret matches as regular expressions.
                                  Example '/foo \w+/i'

  --help                          Show this message and exit.
```
# Examples

### Finding occurences of a word
```sh
quoteclipper -match Hello
```

### Multiple words
You can use the parameter `-m` or `-match` as many times as you want
```sh
# find quotes containing Hello or Hey
quoteclipper -m Hello -m Hi -m Hey
```

### Sentences
You need to use quotes if a sentence contain spaces
```sh
quoteclipper -m "Good Morning" -m "Good Night"
```

### Specifying a folder
The last argument is the path it will scan files, by default it scans the current directory.
```sh
# Will look for every video inside the "video" folder
quoteclipper -m Hello "./videos"
```

### Changing the output filename and path
You can change the output file name and location with the `--output` or `-o` parameter.
```sh
quoteclipper -m Hello -o "~/Desktop/Greetings.mp4"
```

### Exporting individual clips
You can also export individual clips with `--export-clips` or `-e`.
For changing the default file name and location see `--export-clips-dir` and `--export-clips-template` in the Help
```sh
quoteclipper -m Hello --export-clips
```
#### Clip naming
When using `--export-clips` or `-e` you can change the default naming patter using `--export-clips-template` or `-et`
```sh
--export-clips-template "Clip {n} - {quote} from ({basename}).mp4"
```
Variables:
 - `n` - number (keep things in sequence and avoid overriding clips)
 - `index` - original subtitle index
 - `basename` - name of the original file without extension
 - `quote` - the quote text
 - `start` - original start timestamp
 - `end` - original end timestamp
 - `duration` - duration of the clip


## Extending clips
If you need to add extra time before and after each clip, you can offset the start and end cuts with the `--offset` or `-t`.
```sh
# starting 1.5s earlier and 1.5 after (3s longer)
quoteclipper -m Hello --offset -1.5 1.5
 ```


## Regular expressions
For a more advanced matching, you can use power of python regular expressions by enabling the `--regex` or `-re` flag.

Regular expressions need to be delimited by `-m "/re/flags"`

#### Case sensitiveness
Regular expressions are case sensitive by default, and the `--case-sensitive` or `-c` flag has no effect when this mode is enabled.
To make a regex insensitive add the `i` flag like `/re/i` to each regex.

#### Escaping
Due to the nature of POSIX commands, you need to use quotes around the regex if it contains spaces, and in some cases you also need to escape extra characters like ! needs to be scaped as "\!". 

```sh
quoteclipper -re -m "/foo/i"
quoteclipper -re -m "/foo/i" -m "/bar/i" 

quoteclipper -re -m "/Call 555.\d+/i" 
quoteclipper -re -m "/Car?s|sandwich(es)?/i"
quoteclipper -re -m "/(Ya?|You)'? ?Know\!/i"
```
# Instalation

Clone this repository and run
```sh
pip3 install .
```


