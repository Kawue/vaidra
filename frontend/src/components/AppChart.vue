<template>
  <v-card id="chartCard" class="image-card" outlined tile>
    <v-card-title primary id="chartToolboxTop" class="title">
      {{ this.selectedMethod }}
      <div id="select-pointsize-container">
        <v-select
          id="select-pointsize"
          v-model="pointSize"
          v-bind:items="[2,4,6,8,10]"
          v-on:change="updatePointSize()"
          label="Dot-Size"
        ></v-select>
      </div>

      <v-btn
        id="lasso-button"
        v-on:click="changeLassoMode"
      >{{this.lassoMode ? "Lasso on" : "Lasso off"}}</v-btn>

      <v-dialog v-model="dialog" width="500">
        <template v-slot:activator="{ on }">
          <v-btn id="metainfo-button" v-on="on">MetaInfos</v-btn>
        </template>
        <v-card>
          <v-card-title class="headline grey lighten-2" primary-title>Meta Informations</v-card-title>
          <v-card-text>
            Anzahl der Dimensionen: {{this.metaInfo_dim}}
            <br />
            Anzahl der Pixel: {{this.metaInfo_pix}}
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" text @click="dialog=false">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card-title>

    <v-container id="chartContainer">
      <svg id="axis-svg" class="plot" />
      <canvas
        id="scatter-canvas"
        class="plot"
        v-bind:style="{transform: 'translate(' + plotMargin.left + 'px,' + plotMargin.top + 'px)'}"
      ></canvas>
      <canvas
        id="lasso-canvas"
        class="plot"
        v-bind:style="{transform: 'translate(' + plotMargin.left + 'px,' + plotMargin.top + 'px)'}"
      ></canvas>
      <canvas
        id="highlight-canvas"
        class="plot"
        v-bind:style="{transform: 'translate(' + plotMargin.left + 'px,' + plotMargin.top + 'px)'}"
      ></canvas>
      <div id="annotationContainer">
        <svg
          id="annotation-group"
          v-bind:style="{transform: 'translate(' + plotMargin.left + 'px,' + plotMargin.top + 'px)'}"
        />
      </div>
      <svg
        class="absolute-position"
        v-bind:class="'lassoSvg'"
        v-bind:id="'scatter-lassoSvg'"
        v-bind:style="{transform: 'translate(' + plotMargin.left + 'px,' + plotMargin.top + 'px)'}"
      />
    </v-container>

    <v-container id="chartToolboxBottom">
      <v-row cols="12">
        <v-col cols="3">
          <v-select
            id="select-csv"
            label="Select CSV"
            class="selectField"
            v-bind:items="CSVList"
            v-model="selectedCSV"
            v-on:change="onChangeCSV"
          ></v-select>
        </v-col>

        <v-col cols="3">
          <v-text-field
            label="LABEL PIXEL"
            :rules="[rules.required, rules.label]"
            solo
            dense
            v-model="label"
          ></v-text-field>
        </v-col>

        <v-col cols="2">
          <v-btn v-on:click="labelPixel">
            Label
            <br />Pixel
          </v-btn>
        </v-col>
                <v-col cols="2">
          <v-btn v-on:click="resetZoom">
            Reset
            <br />Zoom
          </v-btn>
        </v-col>



        <v-col cols="2">
          <v-btn v-on:click="exportDataset">
            Export
            <br />Datasets
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template> 


<script>
import { bus } from "../main";
import * as d3 from "d3";
//import axios from "axios";
//import "chartjs-plugin-zoom";
import * as d3annotate from "d3-svg-annotation";
import lasso from "../services/lasso.js";
const API_URL = "http://localhost:5000";
import axios from "axios";

export default {
  //mixins: [Scatter],
  props: ["dataObject", "selectedDataset"],
  data() {
    return {
      CSVList: [],
      selectedCSV: null,
      sheet: false,
      brushData: [],
      metaInfo_dim: "",
      metaInfo_pix: "",
      dimx: null,
      dimy: null,
      lassoMode: false,
      dialog: false,
      selectedMethod: "No Embedding Selected",
      selectedDatasets: [],
      selectedEmbedding: null,
      width: null,
      height: null,
      offset: null,
      lassoInstance: null,
      lassoSelectedData: [],
      label: "",
      labledPixels: [],
      exsistingLabels: [],
      plotMargin: { top: 50, right: 50, bottom: 50, left: 50 },
      plotFullwidth: null,
      plotFullheight: null,
      plotWidth: null,
      plotHeight: null,
      xScale: null,
      yScale: null,
      prevPointSize: 2,
      pointSize: 2,
      zoomedPointSize: 2,
      transform: { k: 1, x: 0, y: 0 },
      lastNearestPoint: { x: null, y: null },
      scatterCanvas: null,
      lassoCanvas: null,
      highlightCanvas: null,
      zoom: null,
      pointsFillColors: ["steelblue", "red", "green", "purple", "grey", "teal", "fuchsia", "maroon", "coral", "navy", "darkgoldenrod", "darkslategray", "darkseagreen", "darkkhaki", "chartreuse", "mediumspringgreen", "mediumorchid", "mediumvioletred", "limegreen", "orangered"],
      lassoPointsFillColor: ["orange"],
      highlightPointsFillColor: "crimson",
      loadedLabledData: [],
      start: true,
      rules: {
        required: value => !!value || "Required.",
        label: value => {
          const pattern = /^[0-9a-zA-Z]+$/;
          return pattern.test(value) || "Only letters or numbers!";
        }
      }
    };
  },

  watch: {
    /* eslint-disable */
    selectedDataset() {
      if (this.selectedDataset) {
        // console.log("AppChart: Dataset angekommen");
      }
    },
    dataObject() {
      if (this.dataObject) {
        // TODO nur die ausgewählten DatensatzDaten in das pointsArray
        this.pointsArray = Object.keys(this.dataObject.intensities)
          .filter(key =>
            this.selectedDatasets.includes(
              this.dataObject.intensities[key].dataset
            )
          )
          .map(key => {
            return this.dataObject.intensities[key];
          });
        this.drawBaseplot(this.pointsArray, this.pointsFillColors);
        if (this.lassoMode) {
          d3.select("#scatter-lassoSvg").style("pointer-events", "auto");
          this.lassoInstance = lasso();
          this.lassoInstance.on("end", this.handleLassoEnd);
          let lassoSvg = d3
            .select("#scatter-lassoSvg")
            .call(this.lassoInstance);
        }
        if (this.brushData.length > 0) {
          this.convertPixelDataToIntensityData(this.lassoSelectedData);
          this.redraw();
        }

        this.request_csvs(this.selectedDataset);
      }
    }
  },

  created: function() {
    /* eslint-disable */

    bus.$on("lassoOnImageChanged", selectedPoints => {

      this.selectedCSV = undefined;
      this.label = null;
      if (selectedPoints.length > 0) {
        if (Object.keys(selectedPoints[0]).length == 3) {
          this.lassoSelectedData = selectedPoints;
          this.convertPixelDataToIntensityData(selectedPoints);
        } else if (Object.keys(selectedPoints[0]).length == 2) {
          this.convertDataIntensities(selectedPoints);
          this.convertArrayToObjectArray(selectedPoints);
        }
console.log(this.brushData);
        this.drawPoints(
          this.brushData,
          this.lassoPointsFillColor,
          this.lassoCanvas.getContext("2d")
        );
      } else {
        this.brushData = [];
        this.lassoCanvas
          .getContext("2d")
          .clearRect(0, 0, this.lassoCanvas.width, this.lassoCanvas.height);
      }
    });
  },

  mounted: function() {
    /* eslint-disable */

    this.scatterCanvas = document.getElementById("scatter-canvas");
    this.lassoCanvas = document.getElementById("lasso-canvas");
    this.highlightCanvas = document.getElementById("highlight-canvas");

    bus.$on("NumberOfComponents", number => {
      this.metaInfo_dim = number;
    });

    bus.$on("NumberOfPixels", number => {
      this.metaInfo_pix = number;
    });

    bus.$on("embeddingChanged", embedding => {
      if (this.selectedMethod == "No Embedding Selected") {
        this.selectedEmbedding = embedding;
        let infos = embedding.split("_");
        this.selectedMethod = infos[infos.length - 2];
      } else {
        let infos = embedding.split("_");
        this.selectedMethod = infos[infos.length - 2];
        this.brushData = [];
        this.metaInfo_dim = "";
        this.metaInfo_pix = "";
        this.selectedDatasets = [];
        this.labledPixels = [];
        this.CSVList = [];
        this.quadtree = [];
        this.dimx = null;
        this.dimy = null;
        this.label = "";
        this.pointsArray = [];
        this.start = true;
        this.lassoCanvas
          .getContext("2d")
          .clearRect(0, 0, this.lassoCanvas.width, this.lassoCanvas.height);
        this.scatterCanvas
          .getContext("2d")
          .clearRect(0, 0, this.scatterCanvas.width, this.scatterCanvas.height);
        this.highlightCanvas
          .getContext("2d")
          .clearRect(
            0,
            0,
            this.highlightCanvas.width,
            this.highlightCanvas.height
          );

        if (this.lassoMode) {
          this.changeLassoMode();
        }
      }
    });

    bus.$on("selectedDatasetsChanged", datasets => {
      this.selectedDatasets = datasets;
      this.clearLasso();
      this.start = true;
      this.labledPixels = [];
      this.CSVList = [];
      this.quadtree = [];
      this.label = "";
      this.dimx = null;
      this.dimy = null;
      this.pointsArray = [];
      this.lassoCanvas
        .getContext("2d")
        .clearRect(0, 0, this.lassoCanvas.width, this.lassoCanvas.height);
      this.scatterCanvas
        .getContext("2d")
        .clearRect(0, 0, this.scatterCanvas.width, this.scatterCanvas.height);
      this.highlightCanvas
        .getContext("2d")
        .clearRect(
          0,
          0,
          this.highlightCanvas.width,
          this.highlightCanvas.height
        );
      if (this.lassoMode) {
        this.changeLassoMode();
      }
      d3.select("#axis-svg")
        .selectAll("g")
        .remove();
    });

    bus.$on("selectedDatasetChanged", dataset => {
      if (this.start == false) {
        this.clearLasso();
        this.labledPixels = [];
        this.label = "";
        this.CSVList = [];
        this.brushData = [];
        this.lassoSelectedData = [];
        this.highlightCanvas
          .getContext("2d")
          .clearRect(
            0,
            0,
            this.highlightCanvas.width,
            this.highlightCanvas.height
          );
        // let scatterCanvas = d3.select("#scatter-canvas");
        // let lassoCanvas = d3.select("#lasso-canvas");
        // scatterCanvas.call(this.zoom.transform, d3.zoomIdentity);
        // lassoCanvas.call(this.zoom.transform, d3.zoomIdentity);
      } else {
        this.start = false;
      }
    });

    bus.$on("postSelectedImageChange", (componentIndex, canvasID) => {
      d3.select("#lassopath").remove();
      this.brushData = [];
      this.lassoSelectedData = [];
      if (canvasID === "dimxImage") {
        this.dimx = componentIndex;
      } else if (canvasID === "dimyImage") {
        this.dimy = componentIndex;
      }
    });
  },

  computed: {},

  methods: {
    resetZoom() {
        let scatterCanvas = d3.select("#scatter-canvas");
        let lassoCanvas = d3.select("#lasso-canvas");
      scatterCanvas.call(this.zoom.transform, d3.zoomIdentity);
      scatterCanvas.call(this.zoom);
      lassoCanvas.call(this.zoom.transform, d3.zoomIdentity);
      lassoCanvas.call(d3.zoom().scaleExtent([1, 10]));
          d3.select("#scatter-lassoSvg")
            .selectAll("g").attr(
            "transform",
            "translate(" +
              0 +
              "," +
              0 +
              ")" +
              " scale(" +
              1 +
              ")"
          );
    },
    onChangeCSV() {
      this.request_csv();
      d3.select("#lassopath").remove();
      this.clearLasso();
    },
    convertDataIntensities(data) {
      this.brushData = [];
      data.map(tuple => {
        let point = this.dataObject.intensities[
          tuple[0] + ";" + tuple[1] + ";" + this.selectedDataset
        ];
        if (point !== undefined) {
          this.brushData.push(point);
        } else {
          this.brushData = data;
        }
      });
    },
    convertPixelDataToIntensityData(data) {
      this.brushData = [];
      data.map(tuple => {
        let point = this.dataObject.intensities[
          tuple.px + ";" + tuple.py + ";" + this.selectedDataset
        ];
        if (point !== undefined) {
          this.brushData.push(point);
        }
      });
    },
    convertArrayToObjectArray(data) {
      this.lassoSelectedData = [];
      data.map(tuple => {
        let obj = { px: tuple[0], py: tuple[1], dataset: this.selectedDataset };
        this.lassoSelectedData.push(obj);
      });
    },
    convertDataPixel(rawdata) {
      var formattedData = [];
      rawdata.map(tuple => {
        let obj = { px: tuple[0], py: tuple[1], dataset: this.selectedDataset };
        formattedData.push(obj);
      });
      return formattedData;
    },
    request_csv() {
      const url = API_URL + "/csv/data";
      let formData = new FormData();
      formData.append("csv_name", this.selectedCSV);

      axios
        .post(url, formData)
        .then(response => {
          let rawData = response.data;
          this.label = rawData[0][2];
          //console.log(rawData[0]);
          let arr = [];
          rawData.map(a => arr.push([a[0], a[1]]));
          this.loadedLabledData = arr.map(a => a.map(Number));
          this.convertDataIntensities(this.loadedLabledData);
          this.drawPoints(
            this.brushData,
            this.lassoPointsFillColor,
            this.lassoCanvas.getContext("2d")
          );
          bus.$emit("CSVChanged", this.convertDataPixel(this.loadedLabledData));
        })
        .catch(err => {
          console.error(err);
        });
    },
    request_csvs(selectedDataset) {
      /* eslint-disable */
      const url = API_URL + "/csvs/" + selectedDataset;
      axios
        .get(url)
        .then(response => {
          this.CSVList = response.data;
          this.CSVList.map(element => {
            let el = element.split("_");
            let ele = el[el.length - 1].split(".")[0];
            this.exsistingLabels.push(ele);
          });
        })
        .catch(err => {
          console.error(err);
        });
    },
    handleLassoEnd(lassoPolygon) {
      /* eslint-disable */
      this.lassoSelectedData = [];
      this.brushData = [];
      let bbox = d3
        .select("#lassopath")
        .node()
        .getBBox();
      Object.keys(this.dataObject.intensities)
        .filter(
          key =>
            this.selectedDataset === this.dataObject.intensities[key].dataset
        )
        .map(key => {
          let x = this.dataObject.intensities[key].x;
          let y = this.dataObject.intensities[key].y;
          let d = this.dataObject.intensities[key].dataset;
          
          if (
            d3.polygonContains(lassoPolygon, [this.xScale(x), this.yScale(y)])
          ) {
            let kkey = x + ";" + y + ";" + d;
            if (this.dataObject.pixels[kkey] !== undefined){
            this.brushData.push([this.dataObject.pixels[kkey].px,this.dataObject.pixels[kkey].py]);
            this.lassoSelectedData.push(this.dataObject.pixels[kkey]);
            } else {
              console.log(kkey)
            }
          }
        });
      // this.lassoCanvas
      //   .getContext("2d")
      //   .clearRect(0, 0, this.lassoCanvas.width, this.lassoCanvas.height);
      bus.$emit("lassoOnScatterChanged", this.lassoSelectedData);
      this.label = "";
      this.selectedCSV = undefined;
      d3.select("#lassopath").remove();

      bus.$emit("lassoOnImageChanged", this.brushData);
    },
    exportDataset() {
      /* eslint-disable */
      if (this.CSVList.length == 0) {
        bus.$emit("Snackbar", "Please Label Pixel first!");
      } else {
        const url_createNewDataset = API_URL + "/createDataset";

        axios
          .post(url_createNewDataset)
          .then(response => {})
          .catch(error => {
            console.log(error);
            console.log("Create Dataset FAILURE!!");
          });
        let s = "You created new Datasets!";
        bus.$emit("Snackbar", s);
      }
    },
    labelPixel() {
      /* eslint-disable */
      var letterNumber = /^[0-9a-zA-Z]+$/;
      console.log(this.label);
      if (this.lassoSelectedData.length === 0) {
        bus.$emit("Snackbar", "Choose Pixel with lasso first!");
      } else if (this.labledPixels.length > 0) {
        let s = "There are already labled pixel! Clear or export first!";
        bus.$emit("Snackbar", s);
      } else if (this.label === "") {
        let s = "Choose a label name first!";
        bus.$emit("Snackbar", s);
      } else if (this.exsistingLabels.includes(this.label)) {
        let s = "Label already exists. Choose different label!";
        bus.$emit("Snackbar", s);
      } else if (!this.label.match(letterNumber)) {
        let s =
          "Label must only contain numbers and letters. Choose different label!";
        bus.$emit("Snackbar", s);
      } else if (this.label.match(letterNumber)) {
        this.labledPixels = [];
        for (let i = 0; i < this.lassoSelectedData.length; i++) {
          if (
            this.lassoSelectedData[i].px != undefined &&
            this.lassoSelectedData[i].py != undefined
          ) {
            this.labledPixels.push(
              this.lassoSelectedData[i].px,
              this.lassoSelectedData[i].py,
              this.label
            );
          }
        }
        const url_submitLabeling = API_URL + "/submitLabel";
        let formData = new FormData();
        formData.append("pixel", this.labledPixels);
        formData.append("labelname", this.label);
        formData.append("dataset", this.selectedDataset);

        axios
          .post(url_submitLabeling, formData)
          .then(response => {
            //console.log(response.data);
            this.label = "";
            this.request_csvs(this.selectedDataset);
            this.labledPixels = [];
          })
          .catch(error => {
            console.log(error);
            console.log("Export Labels to FAILURE!!");
          });
        let s =
          "Labeling was successful! Stored in: " +
          this.selectedEmbedding.split("_")[0] +
          "_" +
          this.label +
          ".csv";
        bus.$emit("Snackbar", s);
      }
    },

    changeLassoMode() {
      /* eslint-disable */
      this.lassoMode = !this.lassoMode;
      if (this.lassoMode) {
        d3.select("#scatter-lassoSvg").style("pointer-events", "auto");
        this.lassoInstance = lasso();
        this.lassoInstance.on("end", this.handleLassoEnd);
        let lassoSvg = d3.select("#scatter-lassoSvg").call(this.lassoInstance);
      } else {
        d3.select("#scatter-lassoSvg")
          .select(".lasso-group")
          .remove();
        d3.select("#scatter-lassoSvg").style("pointer-events", "none");
        this.clearLasso();
      }
    },

    clearLasso() {
      /* eslint-disable */
      d3.select("#lassopath").remove();
      this.brushData = [];
      this.lassoSelectedData = [];
      bus.$emit("lassoOnScatterChanged", this.lassoSelectedData);
    },

    drawBaseplot(pointsFillColors) {
      let self = this;
      /* eslint-disable */
      this.plotFullwidth = document.getElementById("chartGrid").offsetWidth;
      this.plotFullheight =
        document.getElementById("chartGrid").offsetHeight -
        document.getElementById("chartToolboxTop").offsetHeight -
        document.getElementById("chartToolboxBottom").offsetHeight;
      this.plotWidth =
        this.plotFullwidth - this.plotMargin.left - this.plotMargin.right;
      this.plotHeight =
        this.plotFullheight - this.plotMargin.top - this.plotMargin.bottom;

      let scatterCanvas = d3
        .select("#scatter-canvas")
        .attr("width", this.plotWidth)
        .attr("height", this.plotHeight)
        .on("mouseleave", mouseLeave);

      function mouseLeave() {
        d3.select("#annotation-group")
          .selectAll("g")
          .remove();
        self.highlightCanvas
          .getContext("2d")
          .clearRect(0, 0, self.plotWidth, self.plotHeight);
      }

      let lassoCanvas = d3
        .select("#lasso-canvas")
        .attr("width", this.plotWidth)
        .attr("height", this.plotHeight);

      let highlightCanvas = d3
        .select("#highlight-canvas")
        .attr("width", this.plotWidth)
        .attr("height", this.plotHeight);

      d3.select("#scatter-lassoSvg")
        .attr("width", this.plotWidth)
        .attr("height", this.plotHeight);

      d3.select("#annotation-group")
        .attr("width", this.plotFullwidth)
        .attr("height", this.plotFullheight);

      this.quadtree = d3
        .quadtree()
        .x(function(d) {
          return d.x;
        })
        .y(function(d) {
          return d.y;
        })
        .addAll(this.pointsArray);

      // Build axes
      d3.select("#axis-svg")
        .selectAll("g")
        .remove();
      let svg = d3
        .select("#axis-svg")
        .attr("width", this.plotFullwidth)
        .attr("height", this.plotFullheight)
        .append("g")
        .attr(
          "transform",
          "translate(" + this.plotMargin.left + "," + this.plotMargin.top + ")"
        );

      // Set ranges [min, max]
      let xRange = [
        this.dataObject.intensities.xmin,
        this.dataObject.intensities.xmax
      ];
      let yRange = [
        this.dataObject.intensities.ymin,
        this.dataObject.intensities.ymax
      ];

      // Build scales
      this.xScale = d3
        .scaleLinear()
        .domain([xRange[0] - this.pointSize, xRange[1] + this.pointSize])
        .range([0, this.plotWidth]);
      this.yScale = d3
        .scaleLinear()
        .domain([yRange[0] - this.pointSize, yRange[1] + this.pointSize])
        .range([this.plotHeight, 0]);

      // Configure axes
      let xAxis = d3.axisBottom(this.xScale).ticks(10, "s");
      let yAxis = d3.axisLeft(this.yScale).ticks(10, "s");
      let xAxisSvg = svg
        .append("g")
        .attr("id", "xAxis")
        .attr("transform", "translate(0," + this.plotHeight + ")")
        .call(xAxis);
      // Add X axis label:
      svg
        .append("text")
        .attr("text-anchor", "middle")
        .attr(
          "transform",
          "translate(" +
            this.plotWidth / 2 +
            " ," +
            (this.plotHeight + 40) +
            ")"
        )
        .text("Dimension " + this.dimx);
      let yAxisSvg = svg
        .append("g")
        .attr("id", "yAxis")
        .call(yAxis);
      // Add Y axis label:
      svg
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - 50)
        .attr("x", 0 - this.plotHeight / 2)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Dimension " + this.dimy);
      let scatterCtx = this.scatterCanvas.getContext("2d");
      let lassoCtx = this.lassoCanvas.getContext("2d");
      let highlightCtx = this.highlightCanvas.getContext("2d");
      this.zoom = d3
        .zoom()
        .scaleExtent([1, 10])
        .on("zoom", zoomed);
      scatterCanvas.call(this.zoom.transform, d3.zoomIdentity);
      scatterCanvas.call(this.zoom);
      lassoCanvas.call(this.zoom.transform, d3.zoomIdentity);
      lassoCanvas.call(d3.zoom().scaleExtent([1, 10]));

      function zoomed() {
        console.log("ZOOMED")
        if (self.pointsArray[0] !== undefined) {
          // Annotation Rect clear
          self.highlightCanvas
            .getContext("2d")
            .clearRect(0, 0, self.plotWidth, self.plotHeight);

          self.transform = d3.event.transform;
          d3.select("#annotation-group")
            .selectAll("g")
            .remove();

          d3.select("#scatter-lassoSvg").attr(
            "transform",
            "translate(" +
              self.transform.x +
              "," +
              self.transform.y +
              ")" +
              " scale(" +
              self.transform.k +
              ")"
          );

          self.drawPoints(self.pointsArray, self.pointsFillColors, scatterCtx);
          if (self.brushData.length > 0) {
            self.drawPoints(
              self.brushData,
              self.lassoPointsFillColor,
              lassoCtx
            );
          }

          xAxisSvg.call(xAxis.scale(self.transform.rescaleX(self.xScale)));
          yAxisSvg.call(yAxis.scale(self.transform.rescaleY(self.yScale)));
          self.zoomedPointSize = self.pointSize / self.transform.k;
        }
      }

      // Highlighting
      scatterCanvas.on("mousemove", this.highlightPoint);

      this.drawPoints(this.pointsArray, this.pointsFillColors, scatterCtx);
    },

    /*
    zoomed() {
      console.log("ZOOMED2")
      if (this.pointsArray[0] !== undefined) {
        // Annotation Rect clear
        this.highlightCanvas
          .getContext("2d")
          .clearRect(0, 0, this.plotWidth, this.plotHeight);

        this.transform = d3.event.transform;
        d3.select("#annotation-group")
          .selectAll("g")
          .remove();

        d3.select("#scatter-lassoSvg").attr(
          "transform",
          "translate(" +
            this.transform.x +
            "," +
            this.transform.y +
            ")" +
            " scale(" +
            this.transform.k +
            ")"
        );
      }
    },*/

    updatePointSize() {
      this.clearLasso();
      this.zoomedPointSize =
        (this.zoomedPointSize / this.prevPointSize) * this.pointSize;
      this.prevPointSize = this.pointSize;
      this.redraw();
    },

    redraw() {
      let scatterCtx = this.scatterCanvas.getContext("2d");
      this.drawPoints(this.pointsArray, this.pointsFillColors, scatterCtx);
      if (this.brushData.length > 0) {
        let lassoCtx = this.lassoCanvas.getContext("2d");
        this.drawPoints(this.brushData, this.lassoPointsFillColor, lassoCtx);
      }
    },

    drawPoints(pointsArray, pointsFillColors, ctx) {
      ctx.save();
      ctx.clearRect(0, 0, this.plotWidth, this.plotHeight);
      ctx.translate(this.transform.x, this.transform.y);
      ctx.scale(this.transform.k, this.transform.k);
      var colorChange = 0;

      if (pointsFillColors.length === 1) {
        ctx.fillStyle = pointsFillColors[colorChange];
        pointsArray.forEach(point => {
          let cx = this.xScale(point.x) - this.zoomedPointSize / 2;
          let cy = this.yScale(point.y) - this.zoomedPointSize / 2;
          ctx.fillRect(cx, cy, this.zoomedPointSize, this.zoomedPointSize);
        });
      } else {
        var trackingDict = new Object();

        pointsArray.forEach(point => {
          if (trackingDict[point.dataset] == undefined) {
            trackingDict[point.dataset] = pointsFillColors[colorChange];
            colorChange++;
            ctx.fillStyle = trackingDict[point.dataset];
          } else {
            ctx.fillStyle = trackingDict[point.dataset];
          }

          let cx = this.xScale(point.x) - this.zoomedPointSize / 2;
          let cy = this.yScale(point.y) - this.zoomedPointSize / 2;
          ctx.fillRect(cx, cy, this.zoomedPointSize, this.zoomedPointSize);
        });
      }
      ctx.restore();
    },

    highlightPoint() {
      function calcDistance(x1, y1, x2, y2) {
        //return ((x2-x1) * (x2-x1)) + ((y2-y1) * (y2-y1));
        return Math.abs(x2 - x1) + Math.abs(y2 - y1);
      }

      function drawHighlight(self, point, pointsFillColor) {
        ctx.save();
        ctx.fillStyle = pointsFillColor;
        ctx.lineWidth = 1;
        ctx.strokeStyle = pointsFillColor;

        // hier werden die transformationen wieder rausgerechnet
        ctx.clearRect(0, 0, self.plotWidth, self.plotHeight);
        ctx.translate(self.transform.x, self.transform.y);
        ctx.scale(self.transform.k, self.transform.k);
        let cx = self.xScale(point.x) - self.zoomedPointSize / 2;
        let cy = self.yScale(point.y) - self.zoomedPointSize / 2;
        ctx.fillRect(cx, cy, self.zoomedPointSize, self.zoomedPointSize);
        ctx.restore();
      }

      function createAnnotation(self, point) {
        let key =
          point.x.toString() +
          ";" +
          point.y.toString() +
          ";" +
          point.dataset.toString();
        let vx = point.x;
        let vy = point.y;
        let px = self.dataObject.pixels[key].px;
        let py = self.dataObject.pixels[key].py;
        let dataset = self.dataObject.pixels[key].dataset;
        // schwarzer punkt vom tooltip
        const annotationProperty = [
          {
            note: {
              title: dataset,
              bgPadding: { top: 4, right: 10, left: 10, bottom: 5 }
            },
            x: self.xScale(point.x) * self.transform.k + self.transform.x,
            y: self.yScale(point.y) * self.transform.k + self.transform.y,
            dx: 30,
            dy: 30,
            color: "black",
            type: d3annotate.annotationCalloutCircle
          }
        ];
        let annotation = d3
          .select("#annotationContainer #annotation-group")
          .call(d3annotate.annotation().annotations(annotationProperty));
        let bbox = d3
          .select(".annotation-note-content")
          .node()
          .getBoundingClientRect();
        d3.select(".annotation-note-bg")
          .attr("width", bbox.width)
          .attr("height", bbox.height * 4)
          .attr("fill", "lightgray")
          .attr("fill-opacity", 0.4);
        d3.select(".annotation-note-label")
          .append("tspan")
          .attr("x", 0)
          .attr("dy", "1.2em")
          .text(`vx: ${vx}`);
        d3.select(".annotation-note-label")
          .append("tspan")
          .attr("x", 0)
          .attr("dy", "1.2em")
          .text(`vy: ${vy}`);
        d3.select(".annotation-note-label")
          .append("tspan")
          .attr("x", 0)
          .attr("dy", "1.2em")
          .text(`px: ${px}`);
        d3.select(".annotation-note-label")
          .append("tspan")
          .attr("x", 0)
          .attr("dy", "1.2em")
          .text(`py: ${py}`);
      }

      let ctx = this.highlightCanvas.getContext("2d");
      let mouse = d3.mouse(this.scatterCanvas);
      // map mouse to scaled data space
      let xMouse = (mouse[0] - this.transform.x) / this.transform.k;
      let yMouse = (mouse[1] - this.transform.y) / this.transform.k;
      let xMouseInvert = this.xScale.invert(xMouse);
      let yMouseInvert = this.yScale.invert(yMouse);
      let nearestPoint = this.quadtree.find(xMouseInvert, yMouseInvert);
      let distance = calcDistance(
        xMouseInvert,
        yMouseInvert,
        nearestPoint.x,
        nearestPoint.y
      );

      if (distance < this.zoomedPointSize) {
        drawHighlight(this, nearestPoint, this.highlightPointsFillColor);
        createAnnotation(this, {
          x: nearestPoint.x,
          y: nearestPoint.y,
          dataset: nearestPoint.dataset
        });
        this.lastNearestPoint = { x: nearestPoint.x, y: nearestPoint.y };
      }
    }
  }
};
</script>



 <style>
.title {
  justify-content: space-around;
}

#select-pointsize-container {
  position: relative;
  max-width: 5vw !important;
  z-index: 109;
}

.image-card {
  margin: 0.2em;
}

#chartContainer {
  height: 50vh;
}

.plot {
  position: absolute;
}

#axis-svg {
  position: absolute;
  z-index: 101;
}

#scatter-canvas {
  position: absolute;
  z-index: 102;
  /* overflow: auto; */
}

#lasso-canvas {
  position: absolute;
  z-index: 104;
  pointer-events: none;
}

#highlight-canvas {
  position: absolute;
  z-index: 108;
  pointer-events: none;
}

#scatter-lassoSvg {
  position: absolute;
  z-index: 105;
  pointer-events: none;
}

#annotation-group {
  position: absolute;
  z-index: 106;
  pointer-events: none;
}
</style>