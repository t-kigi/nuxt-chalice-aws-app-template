<template lang="pug">
  v-row(justify="center", align="center")
    v-col(cols="12", sm="8", md="6")
      div.text-center
        div.label
          p
            | ログアウト中です。 しばらくお待ちください。

</template>

<script>
export default {
  components: {},
  layout() {
    return 'notlogin'
  },
  data() {
    return {}
  },
  async mounted() {
    try {
      this.$store.dispatch('auth/logout', this.$cognito)
      await this.$axios.$get('/api/public/auth/logout')
      this.$router.push('/')
    } catch (error) {
      console.log(error)
    }
  },
}
</script>

<style>
div.label {
  margin: 1em 0;
}
</style>
