import numpy as np
import pandas as pd
import sklearn.decomposition as skd
import sklearn.manifold as skm
import umap as uumap
from sys import argv, path
from collections import OrderedDict
import os
import argparse

class DimensionReducer:

    def __init__(self, data, n_components):
        self.data = data
        self.n_components = n_components

    def to_dframe(self, embedding, methodname):
        if type(pd.DataFrame()) != type(self.data):
            raise ValueError("Data is needed as DataFrame to use this function.")
        return pd.DataFrame(embedding, index=self.data.index, columns=[methodname.lower()+str(x) for x in range(embedding.shape[1])])


class PCA(DimensionReducer):
    def __init__(self, data, n_components, predict_components=False, whiten=False, random_state=0):
        super().__init__(data, n_components)
        self.whiten = whiten
        self.random_state = random_state
        if predict_components:
            self.n_components = "mle"

    def perform(self):
        pca = skd.PCA(n_components=self.n_components, whiten=self.whiten, random_state=self.random_state)
        transform = pca.fit_transform(self.data)
        pca.fit(self.data)
        # variance = pca.explained_variance_ratio_ #calculate variance ratios
        var=np.cumsum(np.round(pca.explained_variance_ratio_, decimals=3)*100)
        eigenvectors = pca.components_
        response = {"result": transform, "eigenvectors": eigenvectors, "eigenvalues": var}
        return response

class NMF(DimensionReducer):
    def __init__(self, data, n_components, init=None, random_state=None):
        super().__init__(data, n_components)
        if init not in [None, "random"]:
            raise ValueError("init parameter is restricted to None or 'random'.")
        
        self.init = init
        self.random_state = random_state

        if self.n_components > min(data.shape):
            self.init = "random"
            print("The high number of n_components forced the parameter random_state to be set to 'random'.")
            if random_state is None:
                self.random_state = 0
            else:
                self.random_state = random_state

    def perform(self):
        nmf = skd.NMF(n_components=self.n_components, init=self.init, random_state=self.random_state)
        transform = nmf.fit_transform(self.data)
        return transform

class LDA(DimensionReducer):
    def __init__(self, data, n_components, random_state=0):
        super().__init__(data, n_components)
        self.random_state = random_state

    def perform(self):
        lda = skd.LatentDirichletAllocation(n_components=self.n_components, random_state=self.random_state)
        transform = lda.fit_transform(self.data)
        return transform

class TSNE(DimensionReducer):
    def __init__(self, data, n_components, init="pca", metric="euclidean", random_state=0):
        super().__init__(data, n_components)
        if init not in ["pca", "random"]:
            raise ValueError("init parameter has to be 'pca' or 'random'.")
        if metric not in ["euclidean", "cosine", "correlation", "manhattan", "precomputed"]:
            raise ValueError("metric parameter is restricted to 'euclidean', 'cosine', 'correlation', 'manhattan' or 'precomputed'")
        if metric == "precomputed":
            print("With metric chosen as 'precomputed' data is expected to be a distance matrix!")
            if self.data.shape[0] != self.data.shape[1]:
                raise ValueError("data cannot be a distance matrix as dim[0] != dim[1].")
        self.init = init
        self.metric = metric
        self.random_state = random_state

    def perform(self):
        tsne = skm.TSNE(n_components=self.n_components, init=self.init, random_state=self.random_state, metric=self.metric)
        transform = tsne.fit_transform(self.data)
        return transform

class UMAP(DimensionReducer):
    def __init__(self, data, n_components, metric="euclidean", n_neighbors=15, min_dist=0.1, random_state=0):
        super().__init__(data, n_components)
        self.random_state = random_state
        if metric not in ["euclidean", "cosine", "correlation", "manhattan", "precomputed"]:
            raise ValueError("metric parameter is restricted to 'euclidean', 'cosine', 'correlation', 'manhattan' or 'precomputed'")
        if metric == "precomputed":
            print("With metric chosen as 'precomputed' data is expected to be a distance matrix!")
            if self.data.shape[0] != self.data.shape[1]:
                raise ValueError("data cannot be a distance matrix as dim[0] != dim[1].")
        self.metric = metric
        self.n_neighbors = n_neighbors
        self.min_dist = min_dist

    def perform(self):
        umap = uumap.UMAP(n_components=self.n_components, metric=self.metric, n_neighbors=self.n_neighbors, min_dist=self.min_dist, random_state=self.random_state)
        transform = umap.fit_transform(self.data)
        return transform

class ICA(DimensionReducer):
    def __init__(self, data, n_components, random_state=0):
        super().__init__(data, n_components)
        self.random_state = random_state
 
    def perform(self):
        ica = skd.FastICA(n_components=self.n_components, random_state=self.random_state)
        transform = ica.fit_transform(self.data)
        return transform

class KPCA(DimensionReducer):
    def __init__(self, data, n_components, kernel="rbf", random_state=0):
        super().__init__(data, n_components)
        if kernel == "linear":
            print("kernel parameter for Kernel PCA was chosen to be 'linear'. The result will be equal to standard PCA.")
        if kernel not in ["linear", "poly", "rbf", "sigmoid", "cosine"]:
            raise ValueError("kernel parameter is restricted to 'linear', 'poly', 'rbf', 'sigmoid', 'cosine'")
        self.kernel = kernel
        self.random_state = random_state

    def perform(self):
        kpca = skd.KernelPCA(n_components=self.n_components, kernel=self.kernel)
        transform = kpca.fit_transform(self.data)
        return transform 

class LSA(DimensionReducer):
    def __init__(self, data, n_components, random_state=0):
        super().__init__(data, n_components)
        self.random_state = random_state

    def perform(self):
        lsa = skd.TruncatedSVD(n_components=self.n_components, random_state=self.random_state)
        transform = lsa.fit_transform(self.data)
        return transform

class LLE(DimensionReducer):
    def __init__(self, data, n_components, n_neighbors=5, random_state=0):
        super().__init__(data, n_components)
        self.n_neighbors = n_neighbors
        self.random_state = random_state

    def perform(self):
        lle = skm.LocallyLinearEmbedding(n_neighbors=self.n_neighbors, n_components=self.n_components, random_state=self.random_state)
        transform = lle.fit_transform(self.data)
        return transform

class MDS(DimensionReducer):
    def __init__(self, data, n_components, dissimilarity='euclidean', random_state=0):
        super().__init__(data, n_components)
        if dissimilarity not in ["euclidean", "precomputed"]:
            raise ValueError("dissimilarity parameter is restricted to 'euclidean' or 'precomputed'")
        if dissimilarity == "precomputed":
            print("With dissimilarity chosen as 'precomputed' data is expected to be a dissimilarity matrix!")
            if self.data.shape[0] != self.data.shape[1]:
                raise ValueError("data cannot be a distance matrix as dim[0] != dim[1].")
        self.dissimilarity = dissimilarity
        self.random_state = random_state

    def perform(self):
        mds = skm.MDS(n_components=self.n_components, random_state=self.random_state)
        transform = mds.fit_transform(self.data)
        return transform

class Isomap(DimensionReducer):
    def __init__(self, data, n_components, n_neighbors):
        super().__init__(data, n_components)
        self.n_neighbors = n_neighbors

    def perform(self):
        isomap = skm.Isomap(n_neighbors=self.n_neighbors, n_components=self.n_components)
        transform = isomap.fit_transform(self.data)
        return transform

class SpectralEmbedding(DimensionReducer):
    def __init__(self, data, n_components, affinity="nearest_neighbors", random_state=0, n_neighbors=None):
        super().__init__(data, n_components)
        if affinity not in ["nearest_neighbors", "rbf"]:
            raise ValueError("affinity parameter is restricted to 'nearest_neighbors' or 'rbf'")
        if affinity != "nearest_neighbors" and n_neighbors is not None:
            raise ValueError("n_neighbors parameter is only usable with affinity set to 'nearest_neighbors'.")
        self.affinity = affinity
        self.random_state = random_state
        self.n_neighbors = n_neighbors

    def perform(self):
        spem = skm.SpectralEmbedding(n_components=self.n_components, affinity=self.affinity, random_state=self.random_state, n_neighbors=self.n_neighbors)
        transform = spem.fit_transform(self.data)
        return transform

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-r", "--readpath", type=str, required=True, nargs='+', help="Path to h5 files.")
    parser.add_argument("-s", "--savepath", type=str, required=True, help="Path to save output.")
    parser.add_argument("-sn", "--savename", type=str, required=False, default=[], nargs='+', help="Name to save the output.")
    parser.add_argument("-m", "--method", type=str, required=True, choices=["pca", "nmf", "lda", "tsne", "umap", "ica", "kpca", "lsa", "lle", "mds", "isomap", "spectralembedding"], help="Path to save output.")
    parser.add_argument("-n", "--ncomponents", type=int, required=True, help="Number of dimensions to reduce to.")
    parser.add_argument("--merge", required=False, action='store_true', help="Merge all selected data sets before dimension reduction.")
    args=parser.parse_args()

    readpath = args.readpath
    savepath = args.savepath
    savename = args.savename
    method = args.method.lower()
    n_components = args.ncomponents

    method_dict = {
        "pca": PCA,
        "nmf": NMF,
        "lda": LDA,
        "tsne": TSNE,
        "umap": UMAP,
        "ica": ICA,
        "kpca": KPCA,
        "lsa": LSA,
        "lle": LLE,
        "mds": MDS,
        "isomap": Isomap,
        "spectralembedding": SpectralEmbedding
        }

    def set_savepath(path, name):
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def read_h5_files(pathlist):
        h5_files = []
        fnames = []
        paths = []

        if len(pathlist) > 1:
            for path in pathlist:
                if not os.path.isfile(path):
                    raise ValueError(f"Path: {path} does not exist.")

            for path in pathlist:
                h5_file = pd.read_hdf(path)
                h5_files.append(h5_file)
                fnames.append(os.path.basename(path).split(".")[0])
        else:
            path = pathlist[0]
            if os.path.isfile(path):
                h5_file = pd.read_hdf(path)
                h5_files.append(h5_file)
                fnames.append(os.path.basename(path).split(".")[0])
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for f in files:
                        h5_file = pd.read_hdf(os.path.join(root,f))
                        h5_files.append(h5_file)
                        fnames.append(f.split(".")[0])

        if len(h5_files) == 0:
            raise ValueError("No HDF5 data sets found!")

        return h5_files, fnames


    h5_files, fnames = read_h5_files(readpath)

    if args.merge:
        if len(h5_files) > 1:
            merged_dframe = pd.DataFrame()
            for idx, dframe in enumerate(h5_files):
                merged_dframe = merged_dframe.append(dframe)
            merged_dframe.fillna(0, inplace=True)
            
            if len(savename) > 0:
                fnames = [savename]
            else:
                fnames = ["-".join(fnames)]
                if len(fnames[0]) > 100:
                    fnames = ["your-name-is-way-too-long-you-silly-next-time-provide-a-name"]
            h5_files = [merged_dframe]
        else:
            raise ValueError("Only one File was found. No merge possible!")
    else:
        if len(savename) > 0:
            if len(savename) != len(readpath):
                raise ValueError("Number of savenames must be equal to the number of given files.")

    
    for idx, h5_file in enumerate(h5_files):
        DR = method_dict[method](h5_file, n_components)
        embedding = DR.perform()
        savepath = set_savepath(savepath, fnames[idx])
        embedding_dframe = DR.to_dframe(embedding, method)
        add = f"_{method}_{n_components}"
        print(embedding_dframe)
        print(os.path.join(savepath, fnames[idx] + add + ".h5"))
        embedding_dframe.to_hdf(os.path.join(savepath, fnames[idx] + add + ".h5"), key=fnames[idx]+add, complib="blosc", complevel=9, mode='w')



