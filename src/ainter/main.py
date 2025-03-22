from ainter.io.cmd.parsers import create_program_parser


def main() -> None:
    parser = create_program_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()