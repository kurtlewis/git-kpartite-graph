"""
Kurt Lewis

"""
import networkx as nx
import argparse
import subprocess
import shutil
import re
import matplotlib.pyplot as plt

graph = nx.Graph()


def buildGraph(repoUrl):
    # define where we're dumping the repo data to
    folderName = 'repo.git'
    # clone the repo
    subprocess.call(['git', 'clone', repoUrl, '--bare', folderName],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # iterate through the log and parse it to build graph
    # output = str(subprocess.check_output(['git', 'log', '--name-only', '--reverse', '--pretty=format:"COMMIT_EMAIL: %ae"'], cwd=folderName))
    email = None
    emailRe = re.compile('COMMIT_EMAIL: (.*)\Z')
    fileRe = re.compile('(.+)\Z')
    for line in str(subprocess.check_output(['git', 'log', '--name-only',
                                             '--reverse',
                                             '--pretty=format:COMMIT_EMAIL: %ae'],
                                            cwd=folderName)).split('\\n'):
        emailMatch = emailRe.match(line)
        if emailMatch is not None:
            # update the email and exit the loop
            email = emailMatch.group(1)
            graph.add_node(email)
        elif email is not None:
            fileMatch = fileRe.match(line)
            if fileMatch is not None:
                file = fileMatch.group(1)
                # insert into the graph, or update existing edge
                # networkx ignores already existing nodes and edges
                # TODO - add weighting by number of commits
                graph.add_node(file)
                graph.add_edge(email, file)
    # clean up after building the graph
    shutil.rmtree(folderName)







if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--build', nargs=1,
                           help='Build the graph from a input piped git log')
    argparser.add_argument('--draw', action='store_true',
                           help='Draw the loaded graph.')
    args = argparser.parse_args()
    if args.build is not None:
        # build the graph
        buildGraph(args.build[0])

    if args.draw:
        # draw the graph
        sets = nx.algorithms.bipartite.sets(graph)
        plt.subplot(121)
        pos = nx.bipartite_layout(graph, sets[0])
        nx.draw(graph, with_labels=True, font_weight='bold', pos=pos)
        plt.show()