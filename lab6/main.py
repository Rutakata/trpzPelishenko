import os
import re

def sloc(path):
    total_lines = 0
    blank_lines = 0
    comment_lines = 0

    for root, file in os.walk(path):
        for file in file:
            if file.endswith(".py"):
                with open(os.path.join(root, file), 'r') as f:
                    lines = f.readlines()
                    total_lines += len(lines)

                    for line in lines:
                        if line == "\n":
                            blank_lines += 1
                            continue
                        if re.findall(r'(#[^!].*)|(?:\"\"\"(.|\n*)*?\"\"\")|(?:\'\'\'(.|\n*)*?\'\'\')', line):
                            comment_lines += 1

    comment_stats = comment_lines / total_lines
    return total_lines, blank_lines, comment_lines, comment_stats


sloc = sloc("./test/")
print(f'Physical SLOC: total lines {sloc[0]}, blank lines {sloc[1]}, comment lines {sloc[2]}, comment ratio {sloc[3]}')