from click.testing import CliRunner
from main import main

def test_hello_world():
  runner = CliRunner()
  result = runner.invoke(main, '-dir "/Volumes/SSD 1TB/Downloads/The Boys" -re --dry-run cunt')

  print(result.exception)

  assert not result.exception

  assert result.exit_code == 0

test_hello_world()