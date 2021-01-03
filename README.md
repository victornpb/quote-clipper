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
$ quoteclipper "hello" "bye"
```


# Help
```
Usage: quoteclipper [OPTIONS] MATCHES...

Options:
  -dir, -d, --directory PATH  Directory to be scanned  [default: .]
  -o, --output PATH           Name of the output movie. [default: MATCHES.mp4]
  --dry-run / --no-dry-run    Skip the generation of clips
  -t, --offset <start> <end>  Offset the start and end timestamps. For example
                              --offset -1.5 1.5 will make each clip 3s longer.
                              [default: 0.0, 0.0]

  -re, --regex                Interpret matches as regular expressions
  --help                      Show this message and exit.
```