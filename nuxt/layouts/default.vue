<template lang="pug">
  v-app(light)
    v-navigation-drawer(v-model="drawer", :mini-variant="false"
                        clipped, fixed, app)
      v-list
        v-list-item(v-for="(item, i) in items", :key="i", :to="item.to", router, exact)
          v-list-item-action
            v-icon
              | {{ item.icon }}
          v-list-item-content
            v-list-item-title(v-text="item.title")

    v-app-bar(clipped-left, fixed, app)
      v-btn(icon, @click.stop="drawer = !drawer")
        v-icon
          | mdi-menu
      v-toolbar-title(v-text="title")
      v-spacer

    v-main
      v-container
        nuxt
</template>

<script>
export default {
  data() {
    return {
      drawer: true,
      items: [
        {
          icon: 'mdi-laptop',
          title: 'Top',
          to: '/m/index.html',
        },
        {
          icon: 'mdi-logout',
          title: 'Logout',
          to: '/logout.html',
        },
      ],
      miniVariant: false,
      title: 'Nuxt Chalice Webapp Template',
    }
  },
}
</script>
