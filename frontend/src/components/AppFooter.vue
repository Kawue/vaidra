<template>
  <v-footer dark app id="footer">
    <v-snackbar v-model="snackbar" :timeout="4000" id="snackbar_footer">
      {{ snackbarText }}
      <v-btn color="grey" text @click="snackbar = false">Close</v-btn>
    </v-snackbar>
    <span class="white--text">Lillith Bitter, Karsten Wüllems - 2020</span>
  </v-footer>
</template>

<script>
import { bus } from "../main";

export default {
  data() {
    return {
      snackbar: false,
      snackbarText: "",
    };
  },

  mounted: function() {
    /* eslint-disable */
    bus.$on("Snackbar", s => {
      this.snackbarText = s;
      this.snackbar = true;
    });
  },

};
</script>
<style>
#footer {
  z-index: 170;
}

#snackbar_footer {
  position: absolute;
  bottom: 50px;
}
</style>