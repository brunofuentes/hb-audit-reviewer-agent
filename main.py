import asyncio
from src.cli.parser import create_parser
from src.database.session import init_db


async def main():
    init_db()

    parser = create_parser()
    args = parser.parse_args()

    # If no arguments provided, show help
    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    # Execute the command function that was attached to the parser
    return await args.func(args)


if __name__ == "__main__":
    asyncio.run(main())
