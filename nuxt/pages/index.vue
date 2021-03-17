<template lang="pug">
  v-row(justify="center", align="center")
    v-col(cols="12", sm="8", md="6")
      div.text-center
        div.top-title
          h1
            | Nuxt Chalice App Template
        v-alert(v-if="errorMessage", type="error", border="left", colored-border, elevation="2")
          | {{ errorMessage }}
        v-form(v-model="loginInput.valid", ref="loginForm", lazy-validation)
          v-text-field(v-model="loginInput.username", label="ユーザー名", maxlength="64", :counter="64",
                       @keyup.enter="login()"
                       :rules="[(v) => !!v||'ユーザー名が入力されていません。']")
          v-text-field(v-model="loginInput.password", type="password", label="パスワード", maxlength="64", :counter="64",
                       @keyup.enter="login()"
                       :rules="[(v) => !!v||'パスワードが入力されていません。']")
        div(v-if="newPasswordRequired")
          v-alert(type="info", border="left", colored-border, elevation="2")
            | パスワードを変更してください。
          v-form(v-model="changePasswordInput.valid", ref="changePasswordForm", lazy-validation)
            v-text-field(v-model="changePasswordInput.newPassword", type="password",
                         label="新規パスワード", maxlength="64", :counter="64",
                         :rules="passwordValidation")
            v-text-field(v-model="changePasswordInput.confirmPassword", type="password",
                         label="新規パスワード(確認)", maxlength="64", :counter="64",
                         :rules="confirmPasswordRules")
          div.button
            v-btn(color="success", large, block, @click="loginAndChangePassword")
                v-icon(left)
                | パスワードを変更してログイン
        div(v-else)
          div.button
            v-btn(color="success", large, block, @click="login")
                v-icon(left)
                | ログイン

</template>

<script>
export default {
  components: {
  },
  layout() {
    return 'notlogin'
  },
  data() {
    return {
      loginState: '',
      errorMessage: '',
      loginInput: {
        valid: false,
        username: '',
        password: '',
      },
      changePasswordInput: {
        valid: false,
        newPassword: '',
        confirmPassword: '',
      },
      passwordValidation: [
        (v) => {
          if (/^.{1,7}$/.test(v)) {
            return 'パスワードは8文字以上必要です。'
          }
          if (/^[a-zA-Z]+$/.test(v)) {
            return '数字か記号をパスワード中に1文字は含めてください。'
          }
          return true
        },
      ],
    }
  },
  computed: {
    newPasswordRequired() {
      return this.loginState === 'newPasswordRequired'
    },
    confirmPasswordRules() {
      return [
        (v) =>
          this.changePasswordInput.newPassword ===
            this.changePasswordInput.confirmPassword ||
          '入力されたパスワードが一致しません。',
      ]
    },
  },
  methods: {
    async _set_cookie(session) {
      await this.$store.dispatch('auth/updateSignedCookie', {
        session,
        axios: this.$axios,
      })
    },
    /**
     * ログインを実施
     */
    async login() {
      this.$set(this, 'loginState', '')
      this.$set(this, 'errorMessage', '')
      if (!this.$refs.loginForm.validate()) {
        return
      }
      try {
        const res = await this.$cognito.login(
          this.loginInput.username,
          this.loginInput.password
        )
        this.$set(this, 'loginState', res.type)
        if (!res.session) {
          return
        }
        // ログイン先へリダイレクト
        this._set_cookie(res.session)
        this.$router.push('/m/index.html')
      } catch (error) {
        this.$set(this, 'loginState', 'failed')
        this.$set(this, 'errorMessage', error.message)
      }
    },
    /**
     * ログイン時に必要なのでパスワード変更を実施
     */
    async loginAndChangePassword() {
      this.$set(this, 'errorMessage', '')
      if (
        !this.$refs.loginForm.validate() ||
        !this.$refs.changePasswordForm.validate()
      ) {
        return
      }
      try {
        const res = await this.$cognito.login(
          this.loginInput.username,
          this.loginInput.password,
          this.changePasswordInput.newPassword
        )
        this.$set(this, 'loginState', res.type)
        if (!res.session) {
          return
        }
        // ログイン先へリダイレクト
        this._set_cookie(res.session)
        this.$router.push('/m/index.html')
      } catch (error) {
        this.$set(this, 'loginState', 'failed')
        this.$set(this, 'errorMessage', error.message)
      }
    },
  },
}
</script>

<style>
div.top-title {
  margin-top: 4em;
  margin-bottom: 2em;
}

div.button {
  margin-top: 2em;
}
</style>
