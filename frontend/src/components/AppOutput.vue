<template>
  <div id="output">
    <v-container class="fill height">
      <v-row no-gutters>
        <v-col cols="4">
          <v-card class="image-card" outlined tile id="select-embedding-card">
            <v-select
              id="select-embedding"
              v-model="selectedEmbedding"
              v-bind:items="embeddingList"
              placeholder="Select Embedding"
              v-on:change="onChangeEmbedding"
            ></v-select>
          </v-card>
        </v-col>
        <v-col cols="4">
          <v-card class="image-card" outlined tile>
            <v-select
              multiple
              id="select-datasets"
              v-model="selectedDatasets"
              v-bind:items="datasetList"
              placeholder="Select corresponding Datasets"
              v-on:change="onChangeDatasets"
            >
              <template v-slot:selection="{ item , index }">
                <span v-if="index === 0">{{ item.slice(0,23) }}</span>
                <span
                  v-if="index === 1"
                  class="grey--text caption"
                >(+{{ selectedDatasets.length - 1 }})</span>
              </template>
            </v-select>
          </v-card>
        </v-col>
        <v-col cols="4">
          <v-card class="image-card" outlined tile>
            <v-select
              id="select-dataset"
              v-model="selectedDataset"
              v-bind:items="selectedDatasets"
              placeholder="Show Data From Dataset"
              v-on:change="onChangeDataset"
            ></v-select>
          </v-card>
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col id="chartGrid" cols="8">
          <app-chart v-bind:dataObject="dataObject" v-bind:selectedDataset="selectedDataset"></app-chart>
        </v-col>

        <v-col cols="4">
          <mzImage
            v-bind:imageDimensions="imageDimensions"
            v-bind:selectList="mzList"
            v-bind:canvasID="'mzImage'"
            v-bind:selectPlaceholder="'Select mz Channel'"
            v-bind:rgb="false"
            v-bind:headerText="'mz Channel'"
          ></mzImage>
        </v-col>
      </v-row>

      <v-row no-gutters>
        <v-col cols="4">
          <mzImage
            v-bind:imageDimensions="imageDimensions"
            v-bind:selectList="dimList"
            v-bind:canvasID="'dimxImage'"
            v-bind:selectPlaceholder="'Select Dimension'"
            v-bind:rgb="false"
            v-bind:headerText="'Dimension X'"
          ></mzImage>
        </v-col>

        <v-col cols="4">
          <mzImage
            v-bind:imageDimensions="imageDimensions"
            v-bind:selectList="dimList"
            v-bind:canvasID="'dimyImage'"
            v-bind:selectPlaceholder="'Select Dimension'"
            v-bind:rgb="false"
            v-bind:headerText="'Dimension Y'"
          ></mzImage>
        </v-col>

        <v-col cols="4">
          <mzImage
            v-bind:imageDimensions="imageDimensions"
            v-bind:selectList="dimList"
            v-bind:canvasID="'rgbImage'"
            v-bind:rgb="true"
            v-bind:headerText="'RGB Image'"
          ></mzImage>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { bus } from "../main";
import AppChart from "./AppChart";
import axios from "axios";
import mzImage from "./mzImage";
//import { log } from 'util';
const API_URL = "http://localhost:5000";

export default {
  components: {
    "app-chart": AppChart,
    mzImage: mzImage
  },

  data() {
    return {
      imageDimensions: { height: 100, width: 100 },
      selectedDimX: null,
      selectedDimY: null,
      mzList: [],
      dimList: [],
      embeddingList: [],
      datasetList: [],
      selectedEmbedding: null,
      selectedDatasets: [],
      dataObject: null,
      selectedDataset: null
    };
  },

  methods: {
    // Anzahl der Dimensionen/Components
    request_number_of_components() {
      /* eslint-disable */
      const url =
        API_URL + "/embeddings/" + this.selectedEmbedding + "/componentsnumber";
      axios
        .get(url)
        .then(response => {
          this.dimList = [...Array(response.data).keys()];
          bus.$emit("NumberOfComponents", this.dimList.length);
        })
        .catch(err => {
          console.log(err);
        });
    },

    request_mzvalues(datasetname) {
      /* eslint-disable */
      const url = API_URL + "/mzImage/" + datasetname + "/mzvalues";
      axios
        .get(url)
        .then(response => {
          this.mzList = response.data;
          // this.mzListRounded = this.mzList.map(function(each_element) {
          //   return Number(each_element.toFixed(2));
          // });
        })
        .catch(err => {
          console.error(err);
        });
    },

    request_selected_embedding() {
      /* eslint-disable */
      const postData = {
        selectedDimX: this.selectedDimX,
        selectedDimY: this.selectedDimY
      };
      const url = API_URL + "/embeddings/" + this.selectedEmbedding + "/data";
      axios
        .post(url, postData)
        .then(response => {
          this.dataObject = response.data;
        })
        .catch(err => {
          console.error(err);
        });
    },

    request_embeddings() {
      /* eslint-disable */
      const url = API_URL + "/embeddings";
      axios
        .get(url)
        .then(response => {
          this.embeddingList = response.data;
        })
        .catch(err => {
          console.error(err);
        });
    },

    request_datasets(selectedEmbedding) {
      /* eslint-disable */
      const url = API_URL + "/datasets" + "/" + selectedEmbedding;
      axios
        .get(url)
        .then(response => {
          this.datasetList = response.data;
        })
        .catch(err => {
          console.error(err);
        });
    },
    // Anzahl der Pixel -> MetaInfos
    request_pixel_data() {
      const url = API_URL + "/datasets/" + this.selectedDataset + "/pixeldata";
      axios
        .get(url)
        .then(response => {
          this.pixels = response.data.pixels;
          bus.$emit("NumberOfPixels", this.pixels.length);
        })
        .catch(err => {
          console.error(err);
        });
    },

    // original Höhe Breite des Bildes
    request_imageDimensions(name, embeddingFlag) {
      /* eslint-disable */
      let flag = "";
      if (embeddingFlag) {
        flag = "embedding";
      } else {
        flag = "dataset";
      }
      const url =
        API_URL + "/datasets/" + name + "/" + flag + "/imagedimensions";

      axios
        .get(url)
        .then(response => {
          this.imageDimensions = response.data;
          console.log("requestImageDimensions sucessful");
        })
        .catch(err => {
          console.error(err);
        });
    },

    request_component_image(datasetname, embeddingname, drawElement, canvasID) {
      /* eslint-disable */
      const postData = {
        colorscale: "Viridis",
        drawElement: drawElement
      };
      let url = "";
      if (canvasID === "dimxImage" || canvasID === "dimyImage") {
        url =
          API_URL +
          "/datasets/" +
          datasetname +
          "/" +
          embeddingname +
          "/componentimage";
      } else if (canvasID === "rgbImage") {
        url =
          API_URL +
          "/datasets/" +
          datasetname +
          "/" +
          embeddingname +
          "/rgbimage";
      } else if (canvasID === "mzImage") {
        url = API_URL + "/datasets/" + datasetname + "/mzimage";
      } else {
        console.error(
          "Error in Method 'request_component_image()' in Component 'AppOutput'."
        );
      }

      axios
        .post(url, postData)
        .then(response => {
          bus.$emit("postImageChange", response.data, canvasID);
        })
        .catch(err => {
          console.error(err);
        });
    },

    onChangeEmbedding(embedding) {
      /* eslint-disable */
      this.selectedEmbedding = embedding;
      this.dataObject = null;
      this.selectedDimX = null;
      this.selectedDimY = null;
      this.datasetList = [];
      this.selectedDataset = null;
      this.selectedDatasets = [];
      this.selectedR = null;
      this.selectedG = null;
      this.selectedB = null;
      this.selectedMz = null;
      this.selectedDimX = null;
      this.selectedDimY = null;
      this.mzList = [];
      this.dimList = [];

      bus.$emit("embeddingChanged", embedding);
      this.request_datasets(this.selectedEmbedding);
    },

    onChangeDatasets(datasets) {
      /* eslint-disable */
      this.selectedDatasets = datasets;
      this.selectedDimX = null;
      this.selectedDimY = null;
      this.selectedDataset = null;
      this.selectedR = null;
      this.selectedG = null;
      this.selectedB = null;
      this.selectedMz = null;
      this.selectedDimX = null;
      this.selectedDimY = null;
      this.mzList = [];
      this.dimList = [];

      bus.$emit("selectedDatasetsChanged", this.selectedDatasets);
    },

    onChangeDataset(dataset) {
      this.selectedDataset = dataset;
      this.mzList = [];
      this.request_mzvalues(dataset);
      this.request_imageDimensions(dataset, false);
      this.request_number_of_components();
      // this.request_imageDimensions(this.selectedEmbedding, true);
      this.request_pixel_data();
      bus.$emit("selectedDatasetChanged", this.selectedDataset);
    }
  },

  mounted: function() {
    /* eslint-disable */

    this.request_embeddings();

    bus.$on("NewData", () => {
      this.request_embeddings();
    });
  },

  created: function() {
    /* eslint-disable */

    bus.$on("requestImageChange", (componentIndex, canvasID) => {
      this.request_component_image(
        this.selectedDataset,
        this.selectedEmbedding,
        componentIndex,
        canvasID
      );
    });

    bus.$on("postSelectedImageChange", (componentIndex, canvasID) => {
      if (canvasID === "dimxImage") {
        this.selectedDimX = componentIndex;
      } else if (canvasID === "dimyImage") {
        this.selectedDimY = componentIndex;
      }

      if (
        (canvasID === "dimxImage" || canvasID === "dimyImage") &&
        (this.selectedDimX || this.selectedDimX === 0) &&
        (this.selectedDimY || this.selectedDimY === 0) &&
        this.selectedDatasets.length > 0 &&
        this.selectedDataset !== null
      ) {
        this.request_selected_embedding();
      }
    });
  }
};
</script>

 <style>
.hidden {
  visibility: hidden;
}

.image-card {
  margin: 0.2em;
}

#output {
  position: relative;
  z-index: 109;
}
#select-embedding {
  position: relative;
  z-index: 161;
}
#select-datasets {
  position: absolute;
  z-index: 162;
}
#select-dataset {
  position: absolute;
  z-index: 163;
}
</style>