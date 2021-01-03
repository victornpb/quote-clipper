# quote-clipper

dependencies
```sh
pip3 install --trusted-host pypi.python.org moviepy
pip3 install imageio-ffmpeg
```

install
```sh
pip3 install -e .
```

run
```sh
$ quoteclipper -m "hello" -m "bye" ./Videos
```


# Help
```
Usage: quoteclipper [OPTIONS] [DIRECTORY]

  A tool for finding quotes in series/movies/animes and automatically
  creating compilations.

  Examples:
  $ quoteclipper -match Hello .
  $ quoteclipper -m "Morning" -m "Good Night" ./videos
  $ quoteclipper -o ~/Desktop/greetings.mp4 -m 'Hello' -m 'Hi' -m 'Whassup' .
  $ quoteclipper -re -m "/Call 555.\d+/i" 
  $ quoteclipper -re -m "/Car?s|sandwich(es)?/i" .
  $ quoteclipper -re -m "/(Ya?|You)'? ?Know\!/i"

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