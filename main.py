#!/usr/bin/env python3
"""
Music Streaming GUI Client

Entry point for the music streaming client application.
Launches the tkinter-based GUI for searching and playing music
from the music streaming server.

Usage:
    python main.py

The client will connect to the server at http://pi-server:8080 by default.
Make sure the music streaming server is running before launching the client.
"""

from gui_client import MusicGUIClient


def main():
    """Entry point for the GUI application."""
    app = MusicGUIClient()
    app.run()


if __name__ == "__main__":
    main()