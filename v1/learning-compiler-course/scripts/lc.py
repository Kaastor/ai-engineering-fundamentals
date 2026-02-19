#!/usr/bin/env python3
"""Thin CLI wrapper.

Business logic lives in `learning_compiler/`. This script exists so students can run
things without worrying about packaging entrypoints during labs.
"""

from __future__ import annotations

import sys

from learning_compiler.cli import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
