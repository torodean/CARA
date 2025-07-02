# CARA

CARA (Changelog Automation & Release Assistant) is a lightweight, configurable tool that automatically generates and updates changelogs based on your Git history. Designed to be dropped into any project with minimal setup, CARA parses commits, tags, and branches to create structured, readable changelogs tailored to your workflow. It supports custom configuration, integrates with CI pipelines, and works out of the box.

## Quick Use

To use CARA, simply include the cara script and a configuration file in your project. Then, CARA can be called from the top level of your project with `python3 /path/to/cara.py -c /path/to/cara.conf`. For more information on the various configuration available, see the main docs in the `docs` folder.