<template>
  <v-app>
    <v-content>
      <AppToolbar/>
      <AppOutput/>
      <AppFooter/>
    </v-content>


  </v-app>
</template>


<script>
//hier müssen die komponenten hinzugefügt werden
import AppToolbar from "./components/AppToolbar";
import AppOutput from "./components/AppOutput";
import AppFooter from "./components/AppFooter";




// hier müssen auch die komponenten hinzugefügt werden
export default {
  name: "App",
  components: {
    AppToolbar,
    AppOutput,
    AppFooter
  },
  data() {
    return {
      //
    };
  }
};
</script>
