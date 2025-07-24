#!/bin/python3
"""
 Changelog Automation & Release Assistant (CARA)
 Created by: Antonius Torode
----------------------------------------------------------
 The purpose of this application/script is to provide some
 automation for updating a changelog by using the git log
 and git commit history. This app provides configuration
 in order to setup the changelog formatting and logging
 features to match various functionalities.
 See https://github.com/torodean/CARA/blob/main/docs/CARAManual.pdf
"""

from collections import defaultdict
import datetime
# Used for adding application parameters.
import argparse
import subprocess


class CLIArgs:
    """
    Handles parsing and storing command-line arguments for the 
    Changelog Automation & Release Assistant (CARA) application.

    Attributes:
        verbose (bool): Flag to enable verbose output.
        debug (bool): Flag to enable debug output.
        config (str or None): Path to the configuration file.
        input_file (str or None): Path to the input changelog file.
        output_file (str or None): Path to the output changelog file.
        repo_path (str or None): Path to the target Git repository.
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Changelog Automation & Release Assistant (CARA).'
        )
        self._add_arguments()
        self.args = self.parser.parse_args()

        self.verbose = self.args.verbose
        self.debug = self.args.debug
        self.config = self.args.config
        self.input_file = self.args.input
        self.output_file = self.args.output
        self.repo_path = self.args.repo

    def _add_arguments(self):
        """
        Defines and registers all expected command-line arguments.
        """
        self.parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            default=False,
            help="Enables verbose mode. This will output various program data for detailed output."
        )
        self.parser.add_argument(
            '-d', '--debug',
            action='store_true',
            default=False,
            help="Enables debug mode. This will output various program data for debugging."
        )
        self.parser.add_argument(
            '-c', '--config',
            action='store',
            default="cara.conf",
            help='The configuration file to use.'
        )
        self.parser.add_argument(
            '-i', '--input',
            action='store',
            default=None,
            help='The input changelog to use. Use this option to overwrite/update an existing changelog.'
        )
        self.parser.add_argument(
            '-o', '--output',
            action='store',
            default="CHANGELOG.md",
            help='The output file to use. Use this option to create a new changelog.'
        )
        self.parser.add_argument(
            '-r', '--repo',
            action='store',
            default=".",
            help='The repo path to use. This will default to the current directory.'
        )
        
        def print_values(self):
            """
            Prints the current values of all parsed command-line arguments.
            """
            print(f"--------------------------------------")
            print(f"----- Parse Configuration Values -----")
            print(f"Verbose Mode: {self.verbose}")
            print(f"Debug Mode: {self.debug}")
            print(f"Config File: {self.config}")
            print(f"Input File: {self.input_file}")
            print(f"Output File: {self.output_file}")
            print(f"Repository Path: {self.repo_path}")
            print(f"--------------------------------------")


class Config:
    """
    This class is used for parsing and storing the CARA configuration file. For
    detailed information on valid configuration values and what they do, see the main
    documentation.
    """
    def __init__(self, file = None):
        self.config_data = {}
        self.load_config_file(file, "=")
        
    def load_config_file(self, file, delimiter):
        if not file:
            return

        with open(file, "r") as f:
            for line in f:
                line = line.split("#", 1)[0].strip()  # Remove comments and whitespace
                if not line:
                    continue  # Skip empty lines
                if delimiter not in line:
                    continue  # Skip malformed lines
                key, value = line.split(delimiter, 1)
                self.config_data[key.strip()] = value.strip()
        
    def get(self, key, default = None):
        return self.config_data.get(key, default)

    def set(self, key, value):
        self.config_data[key] = value
        
    def print_config(self):
        """
        Prints all key-value pairs in the loaded configuration.
        """
        if not self.config_data:
            print("No configuration loaded.")
            return

        print("Current Configuration:")
        for key, value in self.config_data.items():
            print(f"{key} = {value}")


class GitLogEntry:
    """
    Represents a single Git commit entry.

    Attributes:
        commit (str): The full SHA-1 hash of the commit.
        author (str): The name of the author of the commit.
        full_date (str): The commit date containing enough details for parsing the info later.
        display_date (str): The commit date formatted based on the config file for display.
        message (str): The commit message summary.
    """
    def __init__(self, commit, author, full_date, display_date, message):
        self.commit = commit
        self.author = author
        self.full_date = full_date
        self.display_date = display_date
        self.message = message

    def __repr__(self):
        """
        Returns a concise string representation of the GitLogEntry instance.

        The output includes the first 7 characters of the commit hash,
        the author's name, and the commit display_date.

        Returns:
            str: A string in the format "<abc1234 - Author Name - Date>".
        """
        return f"<{self.commit[:7]} - {self.author} - {self.display_date}>"


class GitLog:
    """
    Handles parsing and storing Git log data for a given repository.

    Attributes:
        config (Config): The configuration to use for formatting.
        repo_path (str): Path to the Git repository.
        entries (list): A list of GitLogEntry objects parsed from the Git log.
    """
    def __init__(self, config=None, repo_path="."):
    
        self.repo_path = repo_path
        self.config = config
        self.entries = []
        
    def apply_filters(self):
        """
        Applies filtering based on configuration:
        - MIN_WORDS: Minimum number of words in a commit message.
        - MIN_CHARS: Minimum number of characters in a commit message.
        - EXCLUDE_KEYWORDS: List of keywords to exclude if found in the message.
        - INCLUDE_KEYWORDS: List of required keywords; only matching messages are kept.

        MIN_WORDS and MIN_CHARS are mutually exclusive; if both are set, MIN_WORDS takes priority.
        """
        min_words = self.config.get("MIN_WORDS")
        min_chars = self.config.get("MIN_CHARS")
        exclude_keywords = self.config.get("EXCLUDE_KEYWORDS", "").lower().split(",")
        include_keywords = self.config.get("INCLUDE_KEYWORDS", "").lower().split(",")

        def passes(entry):
            """
            Determines if a GitLogEntry satisfies all configured filters:
            minimum word/character count, inclusion, and exclusion keywords.

            Returns:
                bool: True if the entry passes all filters, False otherwise.
            """
            msg = entry.message.lower()

            if min_words is not None:
                if len(msg.strip().split()) < int(min_words):
                    return False
            elif min_chars is not None:
                if len(msg.strip()) < int(min_chars):
                    return False

            if exclude_keywords and any(kw.lower() in msg for kw in exclude_keywords):
                return False

            if include_keywords and not any(kw.lower() in msg for kw in include_keywords):
                return False

            return True

        self.entries = [entry for entry in self.entries if passes(entry)]


    def parse_log(self):
        """
        Executes 'git log' on the specified repository and parses each commit entry
        into GitLogEntry objects. Entries are stored in the 'entries' list.

        Ignores lines that do not match the expected format.
        """
        format_str = "%H|%an|%ad|%s"
        try:
            date_format = self.config.get("DATE_FORMAT")
            if (date_format != None):
                raw_output = subprocess.check_output(
                    ["git", "-C", self.repo_path, "log", f"--pretty=format:'{format_str}'", f"--date=format:{date_format}"],
                    universal_newlines=True
                )
            else: # default
                raw_output = subprocess.check_output(
                    ["git", "-C", self.repo_path, "log", f"--pretty=format:'{format_str}'"],
                    universal_newlines=True
                )
                
            # This is used for parsing dates later.
            full_date_output = subprocess.check_output(
                ["git", "-C", self.repo_path, "log", f"--pretty=format:'{format_str}'", f"--date=format:%Y,%m,%d,%A,%B"],
                universal_newlines=True
            )
        except subprocess.CalledProcessError:
            return

        lines = raw_output.strip().split("\n")
        full_dates = full_date_output.strip().split("\n")
        
        for idx, line in enumerate(lines):
            parts = line.split("|", 3)
            parts_full_date = full_dates[idx].split("|", 3)
            if len(parts) == 4:
                commit, author, display_date, message = parts
                _, _, full_date,_ = parts_full_date
                
                # There is an extra ' character at the start and end, the [1:] and [:-1] trims those.
                self.entries.append(GitLogEntry(commit[1:], author, full_date, display_date, message[:-1]))
               
        # Remove duplicate entries.
        self.entries = self.remove_duplicates_by_day_and_message(self.entries)

    def get_entries(self):
        return self.entries
        
    def print_entries(self):
        """
        Prints all parsed Git log entries in a formatted list.
        """
        for entry in self.entries:
            print(f"{entry.full_date} | {entry.author} | {entry.commit[:7]} - {entry.message}")
            
    def remove_duplicates_by_day_and_message(self, entries):
        """
        Removes duplicates from a list of GitLogEntry objects where entries
        have the same display_date and identical commit messages.

        Args:
            entries (list of GitLogEntry): List of commit entries.

        Returns:
            list of GitLogEntry: Filtered list with duplicates removed.
        """
        seen = set()
        unique_entries = []

        for entry in entries:
            key = (entry.display_date, entry.message.strip())

            if key not in seen:
                seen.add(key)
                unique_entries.append(entry)

        return unique_entries


class ChangelogGenerator:
    """
    Generates a changelog from a GitLog instance.

    Attributes:
        gitlog (GitLog): The GitLog instance containing parsed Git log entries.
        config (Config): The configuration to use for formatting.
        entries (list): Cached list of GitLogEntry objects from the GitLog.
        output (list): The output generated.
    """

    def __init__(self, gitlog, config):
        """
        Initializes the ChangelogGenerator.

        Args:
            gitlog (GitLog): An instance of the GitLog class containing commit entries.
        """
        self.gitlog = gitlog
        self.config = config
        self.entries = gitlog.get_entries()
        self.full_dates = self.entries[2] # the index of the full_dates field.
        self.output = []
        
    def format_entry(self, entry):
        """
        This will format the entry based on various parameters.
        """
        output_entries = self.config.get("OUTPUT_ENTRIES").split(" ")
        output = "- "
        
        if (output_entries == "all"):
            output = f"{entry.commit}: {entry.author} -> {entry.message}"
        else:
            if ("date" in output_entries):
                output += f"[{entry.display_date}] "
            if ("commit" in output_entries):
                output += f"{entry.commit}: "
            if ("author" in output_entries):
                output += f"{entry.author} -> "
            if ("message" in output_entries):
                output += f"{entry.message}"
        
        # Check if the output ends with a period, and add one if it doesn't
        if not output.endswith(".") and not output.endswith("?") and not output.endswith("!"):
            output += "."
        
        return output

    def generate(self):
        """
        Generates the raw changelog content from the Git log entries.

        Returns:
            str: A formatted changelog string.
        """
        unit = self.config.get("GROUP_BY", "day").lower()
        grouped = self.group_by_time_unit(unit)
        
        output = ["# Changelog\nThis changelog is auto-generated by CARA: https://github.com/torodean/CARA\n"]
        for key, entries in grouped.items():
            # Parse the key to extract date components
            if unit == "day":
                display_date = entries[0].display_date
                _, _, _, day_name, _ = entries[0].full_date.split(",")
                header = f"{display_date}"
                if day_name not in header:
                    header = f"{display_date} ({day_name})"
            elif unit == "month":
                _, _, _, _, month_name = entries[0].full_date.split(",")
                header = f"{key} ({month_name})"
            else:
                header = key  # Use key as is for week and year
        
            output.append(f"## {header}")
            for entry in entries:
                line = self.format_entry(entry)
                output.append(line)
                
            output.append("\n") # Add a newline between sections.

        return "\n".join(output)

    def write_to_file(self, path):
        """
        Writes the generated changelog to a file.

        Args:
            path (str): File path where the changelog should be written.
        """
        changelog = self.generate()
        with open(path, "w") as f:
            f.write(changelog)

    def group_by_time_unit(self, unit):
        """
        Groups entries by a given time unit: 'day', 'week', 'month', or 'year'.
        Returns a dictionary where keys are the time period identifiers and values are lists of entries.

        Args:
            unit (str): The time unit to group by. One of 'day', 'week', 'month', 'year'.

        Returns:
            dict: A dictionary grouped by time unit.
        """
        valid_units = {"day", "week", "month", "year"}
        if unit not in valid_units:
            raise ValueError(f"Invalid grouping unit '{unit}'. Choose from: {', '.join(valid_units)}")

        grouped = defaultdict(list)
        for entry in self.entries:
            y, m, d, _, _ = entry.full_date.split(",")
            y, m, d = int(y), int(m), int(d)
            dt = datetime.date(y, m, d)

            if unit == "day":
                key = dt.isoformat()
            elif unit == "week":
                iso_year, iso_week, _ = dt.isocalendar()
                key = f"{iso_year}-W{iso_week:02d}"
            elif unit == "month":
                key = f"{y}-{m:02d}"
            elif unit == "year":
                key = str(y)

            grouped[key].append(entry)
            
        # Sort entries within each group by full_date (descending)
        for key in grouped:
            grouped[key].sort(key=lambda x: datetime.date(*[int(i) for i in x.full_date.split(",")[:3]]), reverse=True)

        # Sort keys in descending order
        if unit == "day":
            sorted_keys = sorted(grouped.keys(), key=lambda x: datetime.date.fromisoformat(x), reverse=True)
        elif unit == "week":
            sorted_keys = sorted(grouped.keys(), key=lambda x: datetime.datetime.strptime(x + "-1", "%Y-W%W-%w"), reverse=True)
        elif unit == "month":
            sorted_keys = sorted(grouped.keys(), key=lambda x: datetime.datetime.strptime(x, "%Y-%m"), reverse=True)
        elif unit == "year":
            sorted_keys = sorted(grouped.keys(), key=int, reverse=True)

        # Create a new dictionary with sorted keys
        sorted_grouped = {key: grouped[key] for key in sorted_keys}
        
        return dict(sorted_grouped)











def main():
    """
    Main entry point for the CARA application. Handles argument parsing,
    configuration loading, Git log parsing, and basic flow control.
    """
    # Parse CLI arguments
    cli = CLIArgs()

    # Load configuration file
    config = Config(cli.config)

    # Parse git log
    gitlog = GitLog(config, repo_path=cli.repo_path)
    gitlog.parse_log()
    gitlog.apply_filters()

    # Display log entries if verbose mode is enabled
    if cli.verbose:
        print("Parsed configuration:")
        config.print_config()
        
        print("Detected git log entiries:")
        for entry in gitlog.get_entries():
            print(entry)

    # Generate the changelog
    generator = ChangelogGenerator(gitlog, config)
    generator.write_to_file(cli.output_file)



if __name__ == "__main__":
    main()
