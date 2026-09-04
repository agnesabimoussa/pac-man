import sys
from parser import Parser
from errors.file_errors import InvalidProgramArguments
from highscore.loader import HighscoreLoader


def main() -> None:
    try:
        if len(sys.argv) != 2:
            raise InvalidProgramArguments(
                "InvalidProgramArguments exception occured:"
                "provide configuration file.")
        config_file = sys.argv[1]
        config = Parser(config_file).parse_config()
        print(config)

        highscores = HighscoreLoader(config.highscore_filename).load()
        print(highscores)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
