<template>
  <v-navigation-drawer fixed :value="aufzu" app width="300" id="drawer">
    <v-card>
      <v-list>
        <v-subheader>Upload Dataset</v-subheader>
        <v-file-input
          id="datsetfile-input1"
          multiple
          clearable
          counter
          label=".h5 dataset file upload"
          ref="datasetfile1"
          accept=".h5"
          v-model="datasetfile_list1"
        />
        <v-subheader>Choose Dimensions</v-subheader>
        <v-list-item>
          <template v-slot:default="{ active, toggle }">
            <v-list-item-action class="file-upload">
              <v-text-field
                v-model="selectedDimensions"
                class="mx-4"
                max="50"
                min="2"
                step="1"
                style="width: 125px"
                type="number"
              ></v-text-field>
            </v-list-item-action>
            <v-list-item-content></v-list-item-content>
          </template>
        </v-list-item>

        <v-subheader>Select Methods</v-subheader>
        <v-select
          class="mx-4"
          v-model="checkedMethods"
          v-bind:items="dimred_methods"
          placeholder="Select Methods"
          multiple
          chips
          style="width: 225px"
        ></v-select>
        <v-btn
          small
          id="btnDimred"
          :disabled="btn_disable"
          v-on:click="calculateEmbedding()"
          class="mx-4"
        >Run Dimension Reduction</v-btn>
        <v-progress-circular
          class="hidden"
          indeterminate
          color="grey"
          size="20"
          width="3"
          id="loader1"
        ></v-progress-circular>

        <v-divider></v-divider>
        <v-subheader>Upload Dataset</v-subheader>
        <v-file-input
          id="datsetfile-input2"
          clearable
          multiple
          counter
          label=".h5 dataset file upload"
          ref="datasetfile2"
          v-model="datasetfile_list2"
          accept=".h5"
        />
        <v-subheader>Upload Embedding</v-subheader>
        <v-file-input
          id="embedding-input"
          counter
          clearable
          multiple
          label=".h5 embedding file upload"
          ref="embeddingfile"
          v-model="embedding_list"
          accept=".h5"
        />

        <v-subheader>Upload CSV</v-subheader>
        <v-file-input
          id="csv-input"
          counter
          clearable
          multiple
          label=".csv label file upload"
          ref="csvfile"
          v-model="csv_list"
          accept=".csv"
        />

        <v-btn small v-on:click="upload()" class="mx-4">Upload Data</v-btn>
        <v-progress-circular
          class="hidden"
          indeterminate
          color="grey"
          size="20"
          width="3"
          id="loader2"
        ></v-progress-circular>
      </v-list>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import { bus } from "../main";
import axios from "axios";
const API_URL = "http://localhost:5000";
import * as path from "path";

export default {
  name: "AppDrawerLeft",
  props: ["aufzu"],
  components: {},
  data: () => ({
    checkedMethods: [],
    btn_disable: false,
    csv_list: [],
    embedding_list: [],
    datasetfile_list1: [],
    datasetfile_list2: [],
    selectedDimensions: 0,
    dimred_methods: [
      "PCA",
      "NMF",
      "LDA",
      "TSNE",
      "UMAP",
      "ICA",
      "KPCA",
      "LSA",
      "LLE",
      "MDS",
      "Isomap",
      "SpectralEmbedding"
    ]
  }),
  watch: {
    /* eslint-disable */
    value(datasetfile_list1) {
      console.error("value", datasetfile_list1);
    }
  },

  methods: {
    calculateEmbedding() {
      /* eslint-disable */
      let formData = new FormData();
      let filenames = [];
      for (let i = 0; i < this.datasetfile_list1.length; i++) {
        let name = path.basename(this.datasetfile_list1[i].name, ".h5");
        let file = this.datasetfile_list1[i];
        formData.append(name, file);
        filenames.push(name);
      }
      formData.append("dataset_name", filenames);
      formData.append("methods", this.checkedMethods);
      formData.append("dim", this.selectedDimensions);
      // es muss eine datei und min eine Methode ausgewählt werden
      const url_calcEmbedding = API_URL + "/calculateEmbedding";
      if (
        this.datasetfile_list1.length > 0 &&
        this.checkedMethods.length > 0 &&
        this.selectedDimensions > 0
      ) {
        document.getElementById("loader1").style.visibility = "visible";
        this.btn_disable = true;
        axios
          .post(url_calcEmbedding, formData)
          .then(response => {
            console.log(response);
            console.log("SUCCESS!!");
            let s = "Embedding calculated!";
            bus.$emit("NewData", s);
            // bis hierhin kommt er
            this.checkedMethods = [];
            this.datasetfile_list1 = [];
            this.selectedDimensions = undefined;
            //TODO .value funktioniert nicht "", [], undefined, null probiert
            console.log(document.getElementById("datsetfile-input1"));
            document.getElementById("datsetfile-input1").value = null;
            document.getElementById("loader1").style.visibility = "hidden";
            this.btn_disable = false;
          })
          .catch(error => {
            console.log(error);
            console.log("FAILURE!!");
          });
      } else {
        console.log("Please select correctly");
      }
    },
    upload() {
      /* eslint-disable */
      let self = this;

      function writeInFormData() {
        document.getElementById("loader2").style.visibility = "visible";
        let fD = new FormData();
        if (self.datasetfile_list2.length > 0) {
          let filenames = [];
          for (let i = 0; i < self.datasetfile_list2.length; i++) {
            let name = path.basename(self.datasetfile_list2[i].name, ".h5");
            let file = self.datasetfile_list2[i];
            fD.append(name, file);
            filenames.push(name);
          }
          fD.append("dataset_names", filenames);
        }
        if (self.embedding_list.length > 0) {
          let filenames = [];
          for (let i = 0; i < self.embedding_list.length; i++) {
            let name = path.basename(self.embedding_list[i].name, ".h5");
            let file = self.embedding_list[i];
            fD.append(name, file);
            filenames.push(name);
          }
          fD.append("embedding_names", filenames);
        }
        if (self.csv_list.length > 0) {
          let filenames = [];
          for (let i = 0; i < self.csv_list.length; i++) {
            let name = path.basename(self.csv_list[i].name, ".csv");
            let file = self.csv_list[i];
            fD.append(name, file);
            filenames.push(name);
          }
          fD.append("csv_names", filenames);
        }
        // for (var key of fD.keys()) {
        //   console.log(key);
        // }

        return fD;
      }

      const url_submitData = API_URL + "/submitData";
      var formData = writeInFormData();

      axios
        .post(url_submitData, formData)
        .then(response => {
          console.log(response.data);
          this.embeddingfile = "";
          this.datasetfile_list2 = [];
          this.csv_list = [];
          this.embedding_list = [];
          document.getElementById("loader2").style.visibility = "hidden";
          let s = "Data uploaded!";
          bus.$emit("NewData", s);
        })
        .catch(error => {
          console.log(error);
          console.log("Failure!!");
        });
    }
  },
  created() {}
};
</script>

<style>
#datsetfile-input1 {
  min-width: 100%;
  width: 100%;
}
/* .file-upload > input {
  display: none;
}
.file-upload {
  width: 80px;
  cursor: pointer;
} */

#drawer {
  z-index: 171
}
</style>