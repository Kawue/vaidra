from flask import Flask, jsonify, abort, make_response
from flask_cors import CORS
from flask import request
import os
import base64
from sys import argv
import pandas as pd
import h5py
import numpy as np
import json
from io import BytesIO
from PIL import Image
from pyscripts.msi_dimension_reducer import PCA, NMF, LDA, TSNE, UMAP, ICA, KPCA, LSA, LLE, MDS, Isomap, SpectralEmbedding
from pyscripts.mzDataset import MzDataSet, DimRedDataSet
import csv


# --------------- Data Variables -------------------
datasets = {}
embeddings = {}

# --------------- Image Variables -------------------
colorscales = {
    'Viridis': 'viridis',
    'Magma': 'magma',
    'Inferno': 'inferno',
    'Plasma': 'plasma',
    'PiYG': 'PiYG'
}

aggregation_methods = {
    'mean': np.mean,
    'median': np.median,
    'min': np.min,
    'max': np.max,
}

# --------------- Dimension Reduction Variables -------------------
dimensionreducer_dict = {
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


# --------------- Read files in folders -------------------
def readDatasets():
    for dataset in os.listdir(DATASET_FOLDER):
        path = os.path.join(DATASET_FOLDER, dataset)
        name = dataset.split(".h5")[0]
        datasets[name] = pd.read_hdf(path)


def readEmbeddings():
    for embedding in os.listdir(EMBEDDING_FOLDER):
        path = os.path.join(EMBEDDING_FOLDER, embedding)
        name = embedding.split(".h5")[0]
        embeddings[name] = pd.read_hdf(path)


app = Flask(__name__, static_url_path='')
DATASET_FOLDER = os.path.join(app.root_path, 'datasets')
EMBEDDING_FOLDER = os.path.join(app.root_path, 'embeddings')
CSV_FOLDER = os.path.join(app.root_path, 'label_csv')
PCA_FOLDER = os.path.join(app.root_path, 'pca_data')
if not os.path.exists(DATASET_FOLDER):
    os.mkdir(DATASET_FOLDER)
if not os.path.exists(EMBEDDING_FOLDER):
    os.mkdir(EMBEDDING_FOLDER)
if not os.path.exists(CSV_FOLDER):
    os.mkdir(CSV_FOLDER)
if not os.path.exists(PCA_FOLDER):
    os.mkdir(PCA_FOLDER)
#app.config["DATASET_FOLDER"] = DATASET_FOLDER
#app.config["EMBEDDING_FOLDER"] = EMBEDDING_FOLDER
#app.config["CSV_FOLDER"] = CSV_FOLDER
#app.config["PCA_FOLDER"] = PCA_FOLDER
readDatasets()
readEmbeddings()
CORS(app)


# --------------- Error Controls -------------------
def dataset_names():
    return list(datasets.keys())


# --------------- Non Image Getters -------------------
# Get data set names
@app.route('/datasets/<selected_embedding>')
def get_datasets(selected_embedding):
    correspondingDatasets = set(
        embeddings[selected_embedding].index.get_level_values("dataset"))
    return json.dumps(list(correspondingDatasets))

# Get embedding names
@app.route('/embeddings')
def get_embeddings():
    return json.dumps(list(embeddings.keys()))

# Get csv label file names
@app.route('/csvs/<dataset_name>')
def get_csvs(dataset_name):
    csv_list = []
    for csv in os.listdir(CSV_FOLDER):
        e_name = dataset_name.split(".h5")[0]
        ce_name = csv.split("_")[0]
        if (ce_name in e_name):
            csv_list.append(csv)
    return json.dumps(csv_list)

# Get mz values from data set
@app.route('/mzImage/<dataset_name>/mzvalues')
def mzvalues(dataset_name):
    mzs = MzDataSet(datasets[dataset_name]).getMzValues()
    response = json.dumps(mzs)
    return response

# Get number of components in selected embedding
@app.route('/embeddings/<embedding_name>/componentsnumber')
def components(embedding_name):
    try:
        embedding = embeddings[embedding_name]
    except Exception as e:
        print("Embedding fehlt!")
        print(e)
    component_no = embedding.shape[1]
    response = json.dumps(component_no)
    return response


@app.route('/datasets/<data_name>/<flag>/imagedimensions', methods=['GET'])
def dataset_image_dimension(data_name, flag):
    if flag == "embedding":
        shape = MzDataSet(embeddings[data_name]).getCube().shape
    elif flag == "dataset":
        shape = MzDataSet(datasets[data_name]).getCube().shape
    else:
        raise ValueError("Flag has to be 'dataset' or 'embedding'.")
    return json.dumps({'height': shape[0], 'width': shape[1]})

# Get pixel data
@app.route('/datasets/<dataset_name>/pixeldata', methods=['GET'])
def get_dataset_pixel(dataset_name):
    ##print(datasets)
    ##print("-----")
    ##print(datasets.keys())
    ##print("-----")
    ##print(dataset_name)
    ##print("-----")
    #print(datasets[dataset_name])
    ##print("-----")
    pixels = zip(datasets[dataset_name].index.get_level_values(
        "grid_x"), datasets[dataset_name].index.get_level_values("grid_y"))
    response = {
        "pixels": list(pixels)
    }
    return json.dumps(response)

# Get csv data
@app.route('/csv/data', methods=['POST'])
def get_csv_data():
    csv_file_name = request.form["csv_name"]
    if not csv_file_name:
        return "No File"

    path = os.path.join(CSV_FOLDER, csv_file_name)
    with open(path, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        response = []
        for row in spamreader:
            response.append(row)
            # a = []
            # for i in range(len(row)-1):
            #     a.append(row[i])
            # response.append(a)

    return json.dumps(response)

# Get embedding data
@app.route('/embeddings/<embedding_name>/data', methods=['POST'])
def get_embedding_data(embedding_name):
    try:
        post_data = request.get_data()
        post_data_json = json.loads(post_data.decode('utf-8'))
        selected_dim_x = int(post_data_json['selectedDimX'])
        selected_dim_y = int(post_data_json['selectedDimY'])
    except:
        return abort(400)

    dr_method = embedding_name.split("_")[-2].lower()
    '''
    response = {
        "xData": list(embeddings[embedding_name][dr_method + str(selected_dim_x)]),
        "yData": list(embeddings[embedding_name][dr_method + str(selected_dim_y)])
    }
    '''
    ex = embeddings[embedding_name][dr_method + str(selected_dim_x)]
    ey = embeddings[embedding_name][dr_method + str(selected_dim_y)]
    intensities = {}
    pixels = {}

    for (gx, gy, ds), val in ex.items():
        gx = int(gx)
        gy = int(gy)
        if type(ey[(gx, gy, ds)]) != np.float64 and type(ey[(gx, gy, ds)]) != float:
            yval = round(float(ey[(gx, gy, ds)].mean()), 10)
        else:
            yval = round(float(ey[(gx, gy, ds)]), 10)
        xval = round(float(val), 10)

        key = "{:.10f}".format(xval).rstrip("0") + ";" + "{:.10f}".format(yval).rstrip("0") + ";{:s}".format(ds)
        pixels[key] = {
            "px": gx,
            "py": gy,
            "dataset": ds
        }

        key = "{:d};{:d};{:s}".format(gx, gy, ds)
        intensities[key] = {
            "x": xval,
            "y": yval,
            "dataset": ds
        }

    intensities["xmin"] = float(round(ex.min(), 10))
    intensities["xmax"] = float(round(ex.max(), 10))
    intensities["ymin"] = float(round(ey.min(), 10))
    intensities["ymax"] = float(round(ey.max(), 10))

    gx_ex = ex.index.get_level_values("grid_x")
    gy_ex = ex.index.get_level_values("grid_y")
    pixels["xmin"] = int(gx_ex.min())
    pixels["xmax"] = int(gx_ex.max())
    pixels["ymin"] = int(gy_ex.min())
    pixels["ymax"] = int(gy_ex.max())
    
    response = {"pixels": pixels, "intensities": intensities}
    return json.dumps(response)

# --------------- mz Image -------------------
@app.route('/datasets/<dataset_name>/mzimage', methods=['POST'])
def datasets_imagedata_mz(dataset_name):
    if dataset_name not in dataset_names():
        return abort(400)
    try:
        post_data = request.get_data()
        post_data_json = json.loads(post_data.decode('utf-8'))
        colorscale = post_data_json['colorscale']
        post_data_mz_value = post_data_json['drawElement']
    except:
        return abort(400)

    if not post_data_mz_value:
        return abort(400)

    mzDataSet = MzDataSet(datasets[dataset_name])

    img_io = BytesIO()
    Image.fromarray(
        mzDataSet.getColorImage(
            post_data_mz_value,
            cmap=colorscales[colorscale]),
        mode='RGBA'
    ).save(img_io, 'PNG')
    img_io.seek(0)
    response = make_response('data:image/png;base64,' +
                             base64.b64encode(img_io.getvalue()).decode('utf-8'), 200)
    response.mimetype = 'text/plain'
    return response

# --------------- Component Image -------------------
@app.route('/datasets/<dataset_name>/<embedding_name>/componentimage', methods=['POST'])
def datasets_imagedata_component(dataset_name, embedding_name):
    if dataset_name not in dataset_names():
        return abort(400)
    try:
        post_data = request.get_data()
        post_data_json = json.loads(post_data.decode('utf-8'))
        colorscale = post_data_json['colorscale']
        post_data_component = post_data_json['drawElement']
    except:
        return abort(400)

    # if not post_data_component:
    #     return abort(400)

    dimRedDataSet = DimRedDataSet(
        datasets[dataset_name], dataset_name, embeddings[embedding_name])

    img_io = BytesIO()
    Image.fromarray(
        dimRedDataSet.getColorImage(
            post_data_component,
            cmap=colorscales[colorscale]),
        mode='RGBA'
    ).save(img_io, 'PNG')
    img_io.seek(0)
    response = make_response('data:image/png;base64,' +
                             base64.b64encode(img_io.getvalue()).decode('utf-8'), 200)
    response.mimetype = 'text/plain'
    return response

# --------------- RGB Image -------------------
@app.route('/datasets/<dataset_name>/<embedding_name>/rgbimage', methods=['POST'])
def datasets_imagedata_rgb(dataset_name, embedding_name):
    if dataset_name not in dataset_names():
        return abort(400)
    try:
        post_data = request.get_data()
        post_data_json = json.loads(post_data.decode('utf-8'))
        post_data_components = [int(i) for i in post_data_json['drawElement']]
    except:
        return abort(400)

    if len(post_data_components) == 0:
        return abort(400)

    dimRedDataSet = DimRedDataSet(
        datasets[dataset_name], dataset_name, embeddings[embedding_name])

    img_io = BytesIO()
    Image.fromarray(
        dimRedDataSet.getRGBImage(
            post_data_components),
        mode='RGBA'
    ).save(img_io, 'PNG')
    img_io.seek(0)
    response = make_response('data:image/png;base64,' +
                             base64.b64encode(img_io.getvalue()).decode('utf-8'), 200)
    response.mimetype = 'text/plain'
    return response

# --------------- App Chart ---------------------
@app.route("/createDataset/<csv_name>", methods=["POST"])
def createDataset(csv_name):
    ##print(csv_name)
    #for csv_file in os.listdir(app.config["CSV_FOLDER"]):
    #new_df_name = csv_file.split(".csv")[0]
    #path = os.path.join(app.config["CSV_FOLDER"], csv_file)
    #dataset = new_df_name.split("_")[0]
    path = os.path.join(CSV_FOLDER, csv_name+".csv")
    dataset = csv_name.split(f"_{csv_name}")[0]

    with open(path, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        new_dframe = pd.DataFrame()

        for row in spamreader:
            x_dframe = datasets[dataset].loc[datasets[dataset].index.get_level_values(
                "grid_x") == int(row[0])]
            y_dframe = x_dframe.loc[x_dframe.index.get_level_values(
                "grid_y") == int(row[1])]
            y_dframe = y_dframe.droplevel("dataset")
            y_dframe.loc[:, "dataset"] = csv_name
            y_dframe.set_index("dataset", append=True, inplace=True)
            #new_dframe = new_dframe.append(y_dframe)
            new_dframe = pd.concat([new_dframe,y_dframe])
        ##print(new_dframe)
        new_df_filename = csv_name + ".h5"
        path = os.path.join(DATASET_FOLDER, new_df_filename)
        # an existing file with the same name will be deleted
        new_dframe.to_hdf(path, key=csv_name, format='table', mode='w')
        test_dframe = pd.DataFrame()
        test_dframe = pd.concat([test_dframe, pd.read_hdf(path)])
        ##print(len(test_dframe.index))

    return "Creation successful!"


# --------------- POST METHODS -------------------
@app.route("/calculateEmbedding", methods=["POST"])
def calculateEmbedding():
    dataset_names = request.form["dataset_name"].split(",")
    multiple_dframe = pd.DataFrame()
    for i in range(len(dataset_names)):
        path = os.path.join(DATASET_FOLDER, dataset_names[i] + ".h5")
        if dataset_names[i] not in datasets.keys():
            request.files[dataset_names[i]].save(path)
        # dframe = h5py_to_dframe(request.files[dataset_names[i]], dataset_names[i])
        multiple_dframe = pd.concat([multiple_dframe, pd.read_hdf(path)]).fillna(0)

    dimensions = int(request.form["dim"])
    if (len(multiple_dframe.index) >= dimensions):
        methods = request.form["methods"].split(",")
        dim = request.form["dim"]

        for method in methods:
            dataset_merged_name = '_'.join(dataset_names)
            embedding_name = str(dataset_merged_name +
                                 "_" + method + "_" + dim)
            if embedding_name not in embeddings.keys():
                dimred = dimensionreducer_dict[method.lower()](
                    multiple_dframe, dimensions)
                #if (method == "PCA"):
                if (method == "CURRENTLY_DISABLED_FUNCTION"):
                    embedding = dimred.perform()
                    embedding_dframe = dimred.to_dframe(embedding["result"], method)
                    pca_filename_PATH = os.path.join(PCA_FOLDER, embedding_name + ".csv")
                    if pca_filename_PATH not in os.listdir(PCA_FOLDER):
                        with open(pca_filename_PATH, 'w', newline='') as csvfile:
                            spamwriter = csv.writer(
                                csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                            for i in embedding:
                                if i != "result":
                                    for j in range(len(embedding[i])):
                                            spamwriter.writerow(
                                                [embedding[i][j]])
                else:
                    embedding = dimred.perform()
                    embedding_dframe = dimred.to_dframe(embedding, method)
                path = os.path.join(EMBEDDING_FOLDER, embedding_name + ".h5")
                embedding_dframe.to_hdf(
                    path, key=embedding_name, complib="blosc", complevel=9)
                embeddings[embedding_name] = embedding_dframe

        return "Calculation Successful"
    else:
        return "Number of Components to high"


@app.route("/submitData", methods=["POST"])
def submitData():
    try:
        dataset_names = request.form["dataset_names"].split(",")
        for i in range(len(dataset_names)):
            datafile = request.files[dataset_names[i]]
            if datafile.filename not in datasets.keys():
                path = os.path.join(DATASET_FOLDER, datafile.filename)
                ##print(path)
                datafile.save(path)
                msidframe = pd.read_hdf(path)
                datasets[datafile.filename] = msidframe
                internal_name = msidframe.index.get_level_values("dataset")[0]
                if datafile.filename != internal_name:
                    raise ValueError("Data set filename does not equal internally saved name. The filename is %s, but %s is saved internally! Please rename!" % (
                        internal_name, datafile.filename))
    except Exception as e:
        print(e)
        print("No dataset file given!")
    
    try:
        embedding_names = request.form["embedding_names"].split(",")
        for i in range(len(embedding_names)):
            embedding_file = request.files[embedding_names[i]]
            if embedding_file.filename not in embeddings.keys():
                path = os.path.join(EMBEDDING_FOLDER, embedding_file.filename)
                embedding_file.save(path)
                embedding_dframe = pd.read_hdf(path)
                embeddings[embedding_file.filename] = embedding_dframe
    except Exception as e:
        print(e)
        print("No embedding data file given!")

    try:
        csv_names = request.form["csv_names"].split(",")
        for i in range(len(csv_names)):
            csv_file = request.files[csv_names[i]]
            if (csv_file.filename not in os.listdir(CSV_FOLDER)):
                path = os.path.join(CSV_FOLDER, csv_file.filename)
                ##print(path)
                csv_file.save(path)
    except Exception as e:
        print(e)
        print("No csv data file given!")

    return "Uploaded"


@app.route("/submitLabel", methods=["POST"])
def label():
    labellist = request.form['pixel'].split(",")
    d_name = request.form['dataset']
    csv_filename_PATH = d_name + '_' + \
        request.form['labelname'].strip() + '.csv'
    ##print(labellist)
    ##print(len(labellist))
    if csv_filename_PATH not in os.listdir(CSV_FOLDER):
        with open('label_csv/' + csv_filename_PATH, 'w', newline='') as csvfile:
            spamwriter = csv.writer(
                csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in range(len(labellist)):
                if (i % 3) == 0:
                    spamwriter.writerow(
                        [int(labellist[i]), int(labellist[i+1]), labellist[i+2]])
        return "Label submitted"
    else:
        return "Choose a different filename"


# --------------- MAIN -------------------
if __name__ == '__main__':
    print("FLASK Server is running")
    # app.run(host='127.0.0.1', port=5000)
    app.run(debug=True)
