"""Entry point for Apify actor when run via 'python -m src'."""

import asyncio
from .main import main

if __name__ == '__main__':
    asyncio.run(main())
