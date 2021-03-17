<template lang="pug">
  v-row(justify="center", align="center")
    v-col(cols="12", sm="8", md="6")
      div.text-center
        div.top-title
          h1
            | Hello, Login Workspace!
          div.button
            v-btn(color="success", large, @click="testPublicAPI")
              | public API access
            span
              | &nbsp;
            v-btn(color="info", large, @click="testPrivateAPI")
              | private API access
        div.codearea
          | {{ apiResult }}

</template>

<script>
export default {
  components: {},
  data() {
    return {
      errorMessage: '',
      apiResult: '',
    };
  },
  async fetch() {
    const { store, $axios } = this.$nuxt.context;
    try {
      const res = await $axios.get('/api/public/test', {
        headers: store.getters['auth/headers'](),
      });
      this.apiResult = res.data;
    } catch (error) {
      this.errorMessage = error.message;
    }
  },
  methods: {
    async testPublicAPI() {
      try {
        this.$set(this, 'errorMessage', '');
        const headers = await this.$cognito.headers();
        const res = await this.$axios.get('/api/public/test', {
          headers,
        });
        this.$set(this, 'apiResult', res.data);
      } catch (error) {
        this.$set(this, 'errorMessage', error.message);
      }
    },
    async testPrivateAPI() {
      try {
        this.$set(this, 'errorMessage', '');
        const headers = await this.$cognito.headers();
        const res = await this.$axios.get('/api/private/test', {
          headers,
        });
        this.$set(this, 'apiResult', res.data);
      } catch (error) {
        this.$set(this, 'errorMessage', error.message);
      }
    },
  },
};
</script>

<style>
div.top-title {
  margin-top: 4em;
  margin-bottom: 2em;
}

div.button {
  margin-top: 2em;
}

div.codearea {
  text-align: left;
  padding: 0.5rem;
  background-color: #cccccc;
  border: 1px solid;
  min-height: 300px;
}
</style>
