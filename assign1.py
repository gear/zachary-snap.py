"""
Utility functions and implementation for assignment 1 of
the Tokyo Insitute of Technology - Fall 2015 Complex Network
- Instructor: Assoc. Prof. Tsuyoshi Murata
- Date: Nov 21, 2015
- Deadline: Nov 30, 2015
- Student: NGUYEN T. Hoang - M1
- StudentID: 15M54097
- Python version: 2.7.6
- SNAP version: 2.4 - SNAP: snap.stanford.edu
"""
import os
import snap
import urllib
import zipfile
import operator

SOURCE_URL = 'http://www-personal.umich.edu/~mejn/netdata/'

def maybe_download(filename, work_directory):
    """ Download the data, unless it's already there """
    """ Copied from input_data.py, Google's Tensorflow introduction"""
    if not os.path.exists(work_directory):
        os.mkdir(work_directory)
    filepath = os.path.join(work_directory, filename)
    if not os.path.exists(filepath):
        filepath, _ = urllib.urlretrieve(SOURCE_URL + filename, filepath)
        statinfo = os.stat(filepath)
        print('Successfully downloaded', filename, statinfo.st_size,' bytes.')
    return filepath

def extract_zip(filename, ext = 'gml'):
    """ Extract file with the extension ext from zip file """
    if not os.path.exists(filename):
        print('File not found %s' % filename)
        return filename
    else:
        dst_name = filename[:-3] + ext
        mzip = zipfile.ZipFile(filename, 'r')
        try:
            # Read the file with input extension in the zip file
            x_name = [i for i in mzip.namelist() if ext in i][-1]
        except IndexError:
            print 'There is no file has %s as extension' % ext
        file(dst_name, 'w').write(mzip.read(x_name))
        mzip.close()
        return dst_name


def GML_to_edgelist(filename):
    """ Convert GML file to edge list file for SNAP """
    # TODO: Fix -3 magic number to get file extension
    rootname = filename[:-3]
    rootname = rootname + 'txt'
    # Check for the input file
    if not os.path.exists(filename):
        print('File not found %s' % filename)
    # Already have the file with same name
    if os.path.exists(rootname):
        # Delete if the file is empty
        if not os.stat(rootname).st_size > 0:
            os.system('rm ' + rootname)
        else:
            return rootname
    else:
        pass
    # Check file extension
    if not filename[-3:].lower() == 'gml' :
        pass
        print('Input file is not GML file, please check.')
    else:
        gml = open(filename, 'r')
        edl = open(rootname, 'w')
        readEdge = False
        readSrc = False
        readDst = False
        for line in gml:
            if 'edge' in line:
                readEdge = True
            else:
                if readEdge :
                    if 'source' in line:
                        readSrc = True
                        intlist = [int(s) for s in line.split() if s.isdigit()]
                        assert len(intlist) == 1, 'Error reading node id in GML file'
                        edl.write(str(intlist[0]) + ' ')
                    else:
                        if 'target' in line:
                            readDst = True
                            intlist = [int(s) for s in line.split() if s.isdigit()]
                            assert len(intlist) == 1, 'Error reading node id in GML file'
                            edl.write(str(intlist[0]) + '\n')
                        else:
                            # TODO: I feel uneasy, is there better way to parse this?
                            if (readEdge and readSrc and readDst):
                                readEdge = False
                                readSrc = False
                                readDst = False
                            else:
                                pass
                else :
                    pass
        gml.close()
        edl.close()
    return rootname

def snap_hash_to_dict(snap_hash, sort=True):
    """ Helper function to return normal [sorted by val] tuple list """
    ranking = {}
    for item in snap_hash:
        ranking[item] = snap_hash[item]
    if not sort:
        return ranking
    else :
        sorted_ranking = sorted(ranking.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_ranking

class UnweightedUndirectedGraph(object):
    # Init
    def __init__(self, edge_list_file, graph_name, fake_graph = False):
        if fake_graph:
            # TODO: Implement fake graph
            self._num_nodes = 50
        else:
            if not os.path.exists(edge_list_file):
                print('File not found: %s' % edge_list_file)
            else:
                self._filepath = edge_list_file
                self._graph = snap.LoadEdgeList(snap.PUNGraph, edge_list_file, 0, 1, ' ')
        self._file = edge_list_file
        self._num_nodes = self._graph.GetNodes()
        self._num_edges = self._graph.GetEdges()
        self._graph_name = str(graph_name)

    @property
    def graph(self):
        return self._graph
    @property
    def src_file(self):
        return self._file
    @property
    def num_nodes(self):
        return self._num_nodes
    @property
    def num_edges(self):
        return self._num_edges

    def quick_visualize_graph(self):
        """ Quickly visulaize the graph with node named by its Id """
        NIdName = snap.TIntStrH()
        for i in range(1, self._num_nodes + 1):
            NIdName[i] = str(i)
        snap.DrawGViz(self._graph, snap.gvCirco, self._graph_name + '.png', self._graph_name, NIdName)

    def seek_central(self, k, centrality_type):
        """ Return top-k node with highest centrality score in a
        specific centrality_type """
        assert k <= self._num_nodes, ('Invalid number of node selection, k=%d > %d' % (self._num_nodes))
        sel = centrality_type.lower()
        if (sel == 'degree'):
            return [self.rank_degree()[i][0] for i in range(0, k)]
        if (sel == 'pagerank'):
            return [self.rank_pagerank()[i][0] for i in range(0, k)]
        if (sel == 'eigenvec'):
            return [self.rank_eigvec()[i][0] for i in range(0, k)]
        return -1

    def snap_hash_to_dict(snap_hash, sorted=True):
        """ Helper function to return normal [sorted by val] dictionary """
        ranking = {}
        for item in snap_hash:
            ranking[item] = NIdEigenH[item]
        if not sorted:
            return ranking
        else :
            sorted_ranking = sorted(ranking.items(), key=operator.itemgetter(1))
            return sorted_ranking

    def rank_eigvec(self):
        """ Return dictionary of node ID and its eigenvector
        centrality score, in score order """
        NIdEigenH = snap.TIntFltH()
        snap.GetEigenVectorCentr(self._graph, NIdEigenH)
        assert len(NIdEigenH) == self._num_nodes, 'Number of nodes in centrality result must match number of nodes in graph'
        return snap_hash_to_dict(NIdEigenH)

    def rank_pagerank(self , C=0.85, Eps=1e-4, MaxIter=100):
        """ Return dictionary of node ID and its pagerank
        centrality score, in score order """
        PRankH = snap.TIntFltH()
        snap.GetPageRank(self._graph, PRankH, C, Eps, MaxIter)
        assert len(PRankH) == self._num_nodes, 'Number of nodes in centrality result must match number of nodes in graph'
        return snap_hash_to_dict(PRankH)

    def rank_degree(self):
        """ Return dictionary of node ID and its degree
        centrality score, in score order """
        DegreeCentr = {}
        for NI in self._graph.Nodes():
            deg = snap.GetDegreeCentr(self._graph, NI.GetId())
            DegreeCentr[NI.GetId()] = deg
        assert len(DegreeCentr) == self._num_nodes, 'Number of nodes must match'
        return snap_hash_to_dict(DegreeCentr)

    def approx_diameter(self, num_test_nodes):
        """ Perform BFS from random nodes to get approximation of the diameter """
        return snap.GetBfsFullDiam(self._graph, num_test_nodes, False) # False = undirected graph

    @property
    def density(self):
        return 2.0 * self._num_edges / (self._num_nodes*(self._num_nodes-1))

    @property
    def avg_path_length(self):
        """ Brute force average path length calculation """
        # TODO: Maybe add dynamic programming to speed up the operation
        total_path_length = 0
        num_path = 0
        for i in range(1, self._num_nodes):
            for j in range(i+1, self._num_nodes + 1):
                length = snap.GetShortPath(self._graph, i, j)
                if length > 0:
                    num_path += 1
                    total_path_length += length
                else:
                    pass
        return 1.0 * total_path_length / num_path

    @property
    def avg_degree(self):
        """ Return average degree of the graph """
        total_deg = 0
        for node in self._graph.Nodes():
            total_deg += node.GetDeg()
        return 1.0 * total_deg / self._num_nodes

    def get_quick_clust_coeff(self):
        """ Use random node to calculate quick approximation of clustering coeff """
        return snap.GetClustCf(self._graph)


### TODO: Create function for modularity and divide the graph stuff


