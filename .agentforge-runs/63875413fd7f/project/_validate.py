from __future__ import annotations

import app


def main() -> None:
    demo = app.build_app()
    print(type(demo).__name__)
    print("validation_ok")


if __name__ == "__main__":
    main()
