import argparse
parser = argparse.ArgumentParser(description='Create a new agent.')
parser.add_argument('--mode', type=str, help='Agent name for the script.')

print(parser.parse_args().mode)