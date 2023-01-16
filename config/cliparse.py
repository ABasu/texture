# -*- coding: utf-8 -*-

import logging
import codecs, os

####################################################################################################
class CliParse(object):
    """
    This module implements a simple command line parser that allows programs to accept dash-letter
    style command line options. For example: C{-o output.txt}. Parses True/False/Yes/No to boolean
    and numbers to integers or floats. Parses command line arguments as well as config.ini style
    files. Returns dictionary of all parameters. CLI arguments override config file parameters.

    C{config.ini} style files can have key=value style entries along with empty lines and comments
    (preceded by C{#}).

    This is not meant to replace Python's more versatile command line argument parser, but should
    make simple command line parsing easier to implement.

    Essentially, three categories of configs are progressively merged together each taking precedence
    over the previous ones:

        - keys: hard coded into the script. Format is C{[defaults, short key, required (optional),
        helpstring (optional)]}. This is used to create a basic list of keys and defaults.
        - config: Read from the config file.
        - argv: passed from the command line.

    Example usage:

    >>> cfg = txt.config.cliparse.CliParse(argv = sys.argv,
    ...     config_file = 'config.cfg',
    ...     help_str = "Some help text for the command line.",
    ...     keys = {'csv':['../data/csvfile.csv','c', True, 'CSV file to read'],
    ...         'outcsv':['../data/out.csv', 'o', True, 'File to write']},
    ...        summary = True).parse()

    """
    def __init__(self, \
            argv=None, \
            config_file=None, \
            version_str='', \
            help_str='', \
            keys={}, \
            summary=False, \
            expand_homedir = True):
        """
        @param argv: Argument list.
        @type  argv: list of strings (usually sys.argv)
        @param config_file: A configuration file that might contain default values (command line
        parameters will override config file values).
        @type  config_file: string
        @param version_str: Version information.
        @type  version_str: string
        @param help_str: Help string.
        @type  help_str: string
        @param keys: A dictionary with every argument as a key with a list in the following format:
        [default_val, short_key, required, "Help_str(optional)"].
        @type  keys: dict
        @param summary: Prints a summary of parameter settings before passing control to the program.
        Useful for debugging.
        @type  summary: boolean
        """
        self.argv = argv
        self.config_file = config_file
        self.version_str = version_str
        self.help_str = help_str
        self.keys = keys
        self.summary = summary
        self.expand_homedir = expand_homedir
        self.order = None


    def parse(self):
        """
        The main parsing function. Loads defaults from self.keys and then updates it first with config
        file (if it exists) and the with command line options.
        """
        self.keys = self.clean_keys(self.keys)

        # Extract all the keys that have default values assigned to a dict
        config = self.load_defaults(self.keys)

        # Update the dict with values from the config file if one exists
        if self.config_file:
            config.update(self.parse_config(self.config_file))

        # Parse out arguments from the command line and update the list
        if self.argv:
            config.update(self.parse_argv(self.argv, self.keys))

        # Clean up and regularize
        config = self.clean_config(config)

        # Check if any required args are omitted
        self.check_required_args(config, self.keys)

        # Display summary for debugging if set
        if self.summary:
            print((self.get_summary(config)))

        # Expand tilde to home directory path
        if self.expand_homedir:
            config = self.parse_homedir(config)

        return config

    def clean_keys(self, keys):
        """
        This function cleans up the default set of keys. It provides default for the third and fourth
        columns (False, '' repectively) if they are missing. This allows the user to omit the required
        flag or a helpstring.

        @param keys: The self.keys list
        @type  keys: dict

        @return: A cleaned keydict
        @rtype:    dict
        """
        cleaned_keys = {}
        for key in keys:
            # Bring the length of the list up to 4
            zeros = [0] * (4-len(keys[key]))
            keys[key].extend(zeros)

            key_fields = []
            # The first two fields -- default and short key -- are required
            key_fields.append(keys[key][0])
            key_fields.append(keys[key][1])
            if type(keys[key][2]) == bool:
                key_fields.append(keys[key][2])
            elif type(keys[key][3]) == bool:
                key_fields.append(keys[key][3])
            else:
                key_fields.append(False)
            if type(keys[key][2]) == str:
                key_fields.append(keys[key][2])
            elif type(keys[key][3]) == str:
                key_fields.append(keys[key][3])
            else:
                key_fields.append('')
            cleaned_keys[key] = key_fields

        return cleaned_keys

    def load_defaults(self, keys):
        """
        Accepts the dictionary of keys and parses out the ones that have a default value, returning
        a dictionary with keys and their default values. Keys that don't have defaults set are
        ignored.

        @param keys: A dictionary of parameters. Each entry is a list, the first item of which is assumed
        to be the default value(or None if no default is assigned)
        @type keys: dict

        @return: A dictionary in {key: default} format.
        @rtype: dict
        """
        config = {}
        for key in keys:
            if keys[key][0] != None:
                config[key] = keys[key][0]

        return config

    def parse_config(self, config_file):
        """
        Parses config file into a dictionary.

        @param config_file: Name of configuration file
        @type config_file: string
        """
        try:
            # Throw away empty lines, comments and invalid lines
            config_lines = [line for line in codecs.open(config_file, 'r', 'ascii').readlines() if line.strip() != '' if line[0] != '#' if line.find('=') != -1]
            config_list = [[kv.strip() for kv in line.split('=')] for line in config_lines]
            config_dict = dict((item[0], item[1].strip('\'"')) for item in config_list)
        except IOError:
            logging.warning("No config file found. Ignoring.")
            config_dict = {}

        return config_dict

    def parse_argv(self, argv, keys):
        """
        Parses the argv list. If -h or no arg is provided, prints the help string.

        @param argv: self.argv
        @type  argv: list
        @param keys: self.keys
        @type  keys: dict

        @return: A dictionary of parsed key: value configs
        @rtype: dict
        """
        args = {}
        short_keys = dict([(keys[k][1], k) for k in keys if keys[k][1] != None])
        n_args = len(argv)

        # Only command with no args - print help
        if n_args == 1:
            argv.append('-h')
            n_args += 1

        for a in range(1, n_args):
            if argv[a][0] == '-':
                arg = argv[a].lstrip('-')
                # Print help or version and exit
                if arg == 'h' or arg == 'help':
                    print("Option -h: Help")
                    print(self.version_str)
                    print(self.get_help_str(keys, self.help_str))
                    exit()
                if arg == 'v' or arg == 'version':
                    print("Option -v: Version")
                    print(self.version_str)
                    exit()
                # Check to see if last arg has been reached
                if a+1 == n_args:
                    val = ''
                else:
                    # '' is empty or next arg
                    val = '' if argv[a+1][0] == '-' else argv[a+1]

                if val != '':
                    if arg in short_keys:
                        arg = short_keys[arg]
                    if arg in args:
                        if isinstance(args[arg], str):
                            args[arg] = [args[arg]]
                        args[arg].append(val)
                    else:
                        args[arg] = val
        return args

    def get_help_str(self, keys, help_str):
        """
        Prints a help string and generates a summary of keys.

        @param keys: List of keys from self.keys.
        @type  keys: dict
        @param help_str: A help string.
        @type  help_str: str

        @return: A formatted help string
        @rtype : str
        """
        help_str += "\n"

        # Calculate column widths
        cl_col = max([len(keys[k][1]) for k in keys]) + 2
        key_col = max([len(k) for k in keys]) + 2
        de_col = max([len(str(keys[k][0])) for k in keys]) + 12
        # Go through sorted list of keys
        order = self.order if self.order else sorted(keys, key = lambda x: keys[x][1], reverse = False)
        for key in order:
            # the command_line flag for the option
            if keys[key][1]:
                cl = keys[key][1]
            else:
                cl = key
            # The help string if any
            try:
                ks = keys[key][3]
            except:
                ks = ''
            # The default value if any
            if keys[key][0] != None:
                de = "Default: " + str(keys[key][0])
            else:
                de = ''

            help_str += "    -{cl:<{cl_col}}{key:<{key_col}}{de:<{de_col}}{ks:<50}\n" \
                    .format(cl=cl+":", cl_col=cl_col, key=key, key_col=key_col, de=de,ks=ks, de_col=de_col)

        return help_str

    def get_summary(self, config):
        """
        Displays a summary of parsed values.

        @param config: Final config dictionary.
        @type config: dict
        """
        summary = ""
        for arg in config:
            summary += '{}: {}\n'.format(arg, str(config[arg]))

        return summary

    def clean_config(self, config):
        """
        Takes a dictionary and converts numbers to int or floats and yes, no, true, false to boolean.

        @param config: Config dictionary.
        @type  config: dict

        @return: Cleaned config
        @rtype: dict
        """
        for item in config:
            # Try convertint to float or int
            try:
                if '.' in config[item]:
                    config[item] = float(config[item])
                else:
                    config[item] = int(config[item])
            # Try converting to boolean for yes, no, true, false.
            # Otherwise, leave as string
            except:
                value = config[item]
                if isinstance(value, str):
                    value = value.lower()
                    if value in ['yes', 'true']:
                        config[item] = True
                    elif value in ['no', 'false']:
                        config[item] = False
                    else:
                        pass

        return config

    def check_required_args(self, config, keys):
        """
        Checks that no required config option is omitted
        """
        fail = False
        for key in keys:
            if keys[key][2] and key not in config:
                fail = True
                logging.warning('%s is a required argument.' % key)
        if fail:
            exit(-1)

        return self

    def parse_homedir(self, cfg):
        """
        Swap out ~ for home
        """
        home = os.path.expanduser('~')
        for k in cfg:
            if isinstance(cfg[k], str):
                cfg[k] = cfg[k].replace('~', home)
        return cfg

    def set_order(self, order):
        """
        Set the order to print help in
        """
        self.order = order

        return self

