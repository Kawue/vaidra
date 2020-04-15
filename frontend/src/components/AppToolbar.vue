<template>
  <div id="toolbar">

    <app-drawer-left :aufzu="drawer"></app-drawer-left>

    <v-toolbar dark fixed>

        <v-btn icon>
          <v-icon @click.stop="drawer = !drawer">mdi-plus-circle</v-icon>
        </v-btn>

      <v-toolbar-title class="headline text-uppercase">
        <span>Projekt</span>
        <span class="font-weight-light">Dimensionsreduktion</span>
      </v-toolbar-title>


    </v-toolbar>

  </div>
</template>

<script>
import AppDrawerLeft from "../components/AppDrawerLeft";

export default {
  components: {
    AppDrawerLeft
  },
  data: () => ({
    drawer: false,
  })
};
</script>

<style>
</style>
