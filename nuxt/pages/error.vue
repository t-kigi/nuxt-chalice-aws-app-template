<template lang="pug">
  v-row(justify="center", align="center")
    v-col(cols="12", sm="10", md="10")
      div
        v-alert(type="error", border="left", colored-border, elevation="2")
          | このページにはアクセスできません。 必要であれば、再度ログインしてください。
      div.text-center.to-top
        a(href="/")
          | ログインページへ

</template>

<script>
export default {
  layout() {
    return 'notlogin'
  },
  data() {
    return {
    }
  },
}
</script>

<style>
div.to-top {
  margin-top: 2rem;
  font-size: 1.5rem;
}
</style>
