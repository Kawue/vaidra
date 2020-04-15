<template>
  <v-card v-bind:id="canvasID +'-cardID'" class="image-card" height="99%" outlined tile>
    <!--  -->
    <v-card-title primary class="cardTitle">
      <span class="cardTitleText">{{headerText}}</span>
      <!--  -->
      <div v-if="rgb" id="rgbSelectorContainer" class="cardHeaderContainer">
        <v-select
          class="selectRGB"
          v-bind:placeholder="'R'"
          v-bind:items="selectList"
          v-model="selectedR"
        ></v-select>
        <v-select
          class="selectRGB"
          v-bind:placeholder="'G'"
          v-bind:items="selectList"
          v-model="selectedG"
        ></v-select>
        <v-select
          class="selectRGB"
          v-bind:placeholder="'B'"
          v-bind:items="selectList"
          v-model="selectedB"
        ></v-select>
        <v-btn id="buttonRGB" @click="triggerRGBImage()">Show</v-btn>
      </div>
      <!--  -->
      <div v-else id="imgSelectorContainer" class="cardHeaderContainer">
        <v-select
          class="selectField"
          v-bind:placeholder="selectPlaceholder"
          v-bind:items="selectList"
          v-model="selected"
          v-on:input="onChangeImage()"
        ></v-select>
      </div>
    </v-card-title>
    <!--  -->
    <div
      class="canvas-root"
      v-bind:id="canvasID + '-root'"
      v-bind:style=" 'position: relative;' + 'width:' + Math.round((scaledImageDimensions.width+2)) + 'px;' + 'height:'  + Math.round((scaledImageDimensions.height+2)) + 'px;'"
    >
      <canvas
        class="absolute-position"
        v-bind:id="canvasID"
        v-bind:width="scaledImageDimensions.width+2"
        v-bind:height="scaledImageDimensions.height+2"
      ></canvas>
      <canvas
        class="absolute-position"
        v-bind:id="canvasID+'-overlay'"
        v-bind:width="scaledImageDimensions.width+2"
        v-bind:height="scaledImageDimensions.height+2"
      ></canvas>
      <svg
        class="absolute-position"
        v-bind:class="'lassoSvg'"
        v-bind:id="canvasID+'-lassoSvg'"
        v-bind:width="scaledImageDimensions.width+2"
        v-bind:height="scaledImageDimensions.height+2"
      />
    </div>
  </v-card>
</template>

<script>
import { bus } from "../main";
import * as d3 from "d3";
//import lasso from "../services/canvaslasso.js";
import lasso from "../services/lasso.js";
//import axios from "axios";

export default {
  props: [
    "imageDimensions",
    "headerText",
    "rgb",
    "selectPlaceholder",
    "canvasID",
    "selectList"
  ],
  name: "MzImage",
  data() {
    return {
      canvas: null,
      base64Image: null,
      lassoInstance: null,
      selectedR: null,
      selectedG: null,
      selectedB: null,
      selected: null,
      scaledImageDimensions: { width: 10, height: 10 },
      scale: 1,
      selectedPixelOnScatter: []
    };
  },

  watch: {
    /* eslint-disable */

    base64Image() {
      if (this.base64Image != null) {
        this.drawImage();
        if (this.selectedPixelOnScatter.length > 0) {
          this.redraw(this.selectedPixelOnScatter);
        } else if (this.selectedPixelOnScatter.length == 0) {
          this.redraw([]);
        }
      } else {
        this.drawImage();
      }
    },

    imageDimensions() {
      let scale = this.findScale(this.imageDimensions);
      this.scaledImageDimensions.height = this.imageDimensions.height * scale;
      this.scaledImageDimensions.width = this.imageDimensions.width * scale;

      d3.selectAll(".lasso-group rect")
        .attr("width", this.imageDimensions.width + 2)
        .attr("height", this.imageDimensions.height + 2);

      d3.selectAll(".lasso-group").attr("transform", "scale(" + scale + ")");

      if (this.canvasID != "mzImage") {
        if (
          this.base64Image !== null &&
          this.selectedPixelOnScatter.length > 0
        ) {
          this.redraw(this.selectedPixelOnScatter);
        } else if (
          this.base64Image !== null &&
          this.selectedPixelOnScatter.length == 0
        ) {
          this.redraw([]);
        }
      }
    }
  },

  created() {
    /* eslint-disable */
    bus.$on("postImageChange", (base64Image, canvasID) => {
      if (this.canvasID === canvasID) {
        this.base64Image = base64Image;
      }
    }),
      bus.$on("lassoOnScatterChanged", selection => {
        this.selectedPixelOnScatter = selection;
        this.redraw(selection);
      });
  },

  mounted() {
    /* eslint-disable */
    this.canvas = d3.select("#" + this.canvasID);
    this.lassoInstance = lasso();
    this.lassoInstance.on("end", this.handleLassoEnd);
    let lassoSvg = d3.select("#" + this.canvasID + "-lassoSvg");
    lassoSvg.call(this.lassoInstance);

    bus.$on("embeddingChanged", embedding => {
      this.lassoInstance = null;
      this.selectedR = null;
      this.selectedG = null;
      this.selectedB = null;
      this.selected = null;
      this.selectedPixelOnScatter = [];
      var can = document.getElementById("" + this.canvasID + "");
      var canvasOverlay = document.getElementById(
        "" + this.canvasID + "-overlay"
      );
      can.getContext("2d").clearRect(0, 0, can.width, can.height);
      canvasOverlay
        .getContext("2d")
        .clearRect(0, 0, canvasOverlay.width, canvasOverlay.height);
      d3.select("#" + this.canvasID + "-lassoSvg")
        .select("#lassopath")
        .remove();
      this.base64Image = null;
    });

    bus.$on("selectedDatasetsChanged", datasets => {
      this.lassoInstance = null;
      this.selectedR = null;
      this.selectedG = null;
      this.selectedB = null;
      this.selected = null;
      this.selectedPixelOnScatter = [];
      var can = document.getElementById("" + this.canvasID + "");
      var canvasOverlay = document.getElementById(
        "" + this.canvasID + "-overlay"
      );
      can.getContext("2d").clearRect(0, 0, can.width, can.height);
      canvasOverlay
        .getContext("2d")
        .clearRect(0, 0, canvasOverlay.width, canvasOverlay.height);
      this.base64Image = null;
      d3.select("#" + this.canvasID + "-lassoSvg")
        .select("#lassopath")
        .remove();
    });

    bus.$on("selectedDatasetChanged", dataset => {
      this.selectedPixelOnScatter = [];
      d3.select("#" + this.canvasID + "-lassoSvg")
        .select("#lassopath")
        .remove();
      this.base64Image = null;
      let self = this;
      if (this.canvasID == "mzImage") {
        this.selected = null;
      } else if (
        this.canvasID == "rgbImage" &&
        this.selectedR != null &&
        this.selectedG != null &&
        this.selectedB != null
      ) {
        bus.$emit(
          "requestImageChange",
          [self.selectedR, self.selectedG, self.selectedB],
          self.canvasID
        );
        self.redraw([]);
      } else if (this.canvasID != "mzImage" && this.selected != null) {
        bus.$emit("requestImageChange", self.selected, self.canvasID);
        self.redraw([]);
      }
    });

    bus.$on("CSVChanged", formattedData => {
      d3.select("#" + this.canvasID + "-lassoSvg")
        .select("#lassopath")
        .remove();
      this.redraw(formattedData);
    });
    bus.$on("redrawImage", data => {
      this.selectedPixelOnScatter = [];
      this.redraw(data);
    });
    bus.$on("pixelDeleted", data => {
      // draw new image+
    });
    bus.$on("clearLasso", () => {
      this.selectedPixelOnScatter = [];
      this.redraw([]);
    });
  },

  computed: {},

  methods: {
    handleLassoEnd(lassoPolygon) {
      /* eslint-disable */
      if (this.base64Image != null) {
        let bbox = d3
          .select("#lassopath")
          .node()
          .getBBox();
        const selectedPoints = [];
        for (
          let i = Math.floor(bbox.x);
          i <
          Math.min(
            this.imageDimensions.width + 1,
            Math.ceil(bbox.x + bbox.width)
          );
          i++
        ) {
          for (
            let j = Math.floor(bbox.y);
            j <
            Math.min(
              this.imageDimensions.height + 1,
              Math.ceil(bbox.y + bbox.height)
            );
            j++
          ) {
            if (d3.polygonContains(lassoPolygon, [i, j])) {
              selectedPoints.push([i, j]);
            }
          }
        }
        bus.$emit("lassoOnImageChanged", selectedPoints);
        bus.$emit("redrawImage", []);
      }
    },

    redraw(pixels) {
      /* eslint-disable */
      let canvas = document.getElementById(this.canvasID + "-overlay");
      let ctx = canvas.getContext("2d");
      ctx.imageSmoothingEnabled = false;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      let dummyCanvas = document.createElement("canvas");
      dummyCanvas.width = this.imageDimensions.width;
      dummyCanvas.height = this.imageDimensions.height;
      let dummyCtx = dummyCanvas.getContext("2d");
      dummyCtx.imageSmoothingEnabled = false;
      let image = new Image();
      image.onload = () => {
        dummyCtx.drawImage(image, 0, 0);
        let rootCanvas = document.getElementById(this.canvasID);
        let rootCtx = rootCanvas.getContext("2d");
        let scale = this.findScale(this.imageDimensions);
        setTimeout(function() {
          rootCtx.save();
          rootCtx.imageSmoothingEnabled = false;

          if (pixels.length === 0) {
            rootCtx.globalAlpha = 1;
          } else {
            rootCtx.globalAlpha = 0.4;
            rootCtx.fillStyle = "gray";
            rootCtx.fillRect(0, 0, canvas.width, canvas.height);

            pixels.forEach(pixel => {
              let p = dummyCtx.getImageData(pixel.px, pixel.py, 1, 1).data;
              if (
                this.selected !== null ||
                (this.selectedR !== null &&
                  this.selectedG !== null &&
                  this.selectedB !== null)
              ) {
                ctx.save();
                ctx.fillStyle =
                  "rgba(" + p[0] + "," + p[1] + "," + p[2] + ", 255)";
                ctx.scale(scale, scale);
                ctx.fillRect(pixel.px, pixel.py, 1, 1);
                ctx.restore();
              }
            });
          }

          rootCtx.scale(scale, scale);
          rootCtx.clearRect(0, 0, rootCanvas.width, rootCanvas.height);
          rootCtx.drawImage(image, 0, 0);
          rootCtx.restore();
        }, 1);
      };

      image.src = this.base64Image;
    },

    findScale(panel) {
      /* eslint-disable */
      let cardWidth = parseInt(
        d3.select("#" + this.canvasID + "-cardID").style("width")
      );
      let scaleWidth = cardWidth / panel.width;
      let scale = scaleWidth;
      return scale;
    },

    drawImage() {
      /* eslint-disable */
      let scale = this.findScale(this.imageDimensions);
      if (this.base64Image != null) {
        let image = new Image();
        image.onload = () => {
          const ctx = this.canvas.node().getContext("2d");
          ctx.save();
          ctx.imageSmoothingEnabled = false;
          ctx.scale(scale, scale);
          ctx.drawImage(image, 0, 0);
          ctx.restore();
        };

        image.src = this.base64Image;
      } else {
        const ctx = this.canvas.node().getContext("2d");
        ctx.clearRect(0, 0, this.width, this.height);
      }
    },

    triggerRGBImage() {
      /* eslint-disable */
      if (
        (this.selectedR || this.selectedR === 0) &&
        (this.selectedG || this.selectedG === 0) &&
        (this.selectedB || this.selectedB === 0)
      ) {
        bus.$emit(
          "requestImageChange",
          [this.selectedR, this.selectedG, this.selectedB],
          this.canvasID
        );
      } else {
        let s = "Select one Component for each Channel!";
        bus.$emit("Snackbar", s);
      }
    },

    onChangeImage() {
      /* eslint-disable */
      console.log("onChangeImage " + this.canvasID);
      bus.$emit("requestImageChange", this.selected, this.canvasID);
      bus.$emit("postSelectedImageChange", this.selected, this.canvasID);
      bus.$emit("redrawImage", []);
    }
  }
};
</script>

<style lang="scss" scoped>
.cardHeaderContainer {
  display: flex;
  &#rgbSelectorContainer {
    //flex:3;
    min-width: 5vw;
    max-width: 13vw;
    margin-right: 0px;
    #buttonRGB {
      margin-top: 0.7vw;
    }
  }
  &#imgSelectorContainer {
    //flex:2;
    .selectField {
      margin: 1vw;
      min-width: 5vw;
      max-width: 10vw;
    }
  }
}

.cardTitleText {
  //flex:1;
  min-width: 7vw;
}

.cardTitle {
  display: flex;
  height: 12vh;
  padding-top: 0px;
}

#buttonRGB {
  width: 1em;
  margin-right: 0px;
}

.absolute-position {
  position: absolute;
  top: 0;
  left: 0;
}
</style>