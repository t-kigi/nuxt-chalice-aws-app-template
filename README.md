# Nuxt-Chalice AWS App Template

AWS 上でアプリケーションを公開する場合に利用することができるテンプレートプロジェクト。
以下の設定で構築されるアプリケーション構築に利用できます。

- FrontEnd のインフラ構成は CloudFront (CDN) + S3 (Static Files) + API Gateway + Lambda (API) の構成である
- FrontEnd に Nuxt.js (SPA) を利用する
- BackEnd (API) に API Gateway + Lambda を利用し、これらを AWS Chalice (Python) にて構築する
- Amazon Cognito UserPool を利用してユーザー管理を行う


## ローカル環境の構築

### 0. 事前準備

- IDaaS として利用する Cognito UserPool を作成して、各種 ID / ARN を取得する
- ローカル稼働に利用するアクセスキーがある場合 `aws configure --profile [YOUR PROFILE]` で利用可能なプロファイルを作成する
  (以下では、プロファイル名として `work` を利用する)


### 1. Chalice をローカル環境で動作させる

まず、以下の設定ファイル `local.yaml` を作成し、手順0. で準備した値を入れる。

- `api/chalicelib/env/local.yaml` (元ファイル: `api/chalicelib/env/local.yaml.tpl` )

その後、以下のコマンドでローカルでアクセス可能なエンドポイントを立てる。

```bash
$ cd api
$ pipenv run chalice local --stage local
Found credentials in shared credentials file: ~/.aws/credentials
Serving on http://127.0.0.1:8000
```

これで localhost:8000 に chalice のローカルエンドポイントが構築できる。
サンプルのままでれば、`/api/public/test` にアクセスすれば結果を得ることができる。

```bash
$ curl http://localhost:8000/api/public/test
{"hello":"public"}
```


### 2. Nuxt.js をローカル環境で動作させる

まず、以下の設定ファイル `env.local.js` を作成し、手順0. で準備した値を入れる。

- `nuxt/constants/env.local.js` (元ファイル: `nuxt/constants/env.local.js.tpl` ) その後、以下のコマンドで nuxt.js をローカルで稼働させる。

```bash
$ cd nuxt
$ yarn local
```

稼働次第、ブラウザで `http://localhost:3000/` にアクセスすれば UI 部分が表示される。


## AWS 環境へのデプロイ手順

ここでは、本番のドメイン `cfntest.t-kigi.net` で公開するウェブアプリケーションを作成する例を紹介する。
また、実行環境は Ubuntu 20.04 LTS である。


### 0. 事前準備

- IDaaS として利用する Cognito UserPool を作成して、各種 ID / ARN を取得する
- AWS Certificate Manager の **us-east-1** リージョンに
  `cfntest.t-kigi.net` で利用可能な SSL 証明書を作成 (or インポート) して、その証明書の ARN を取得する
- 新しい署名用の秘密鍵・公開鍵を作成する (ここでは、それぞれ cloudfront.pem, cloudfront.pub とする)
- `cfn/s3andcloudfront.yaml` の EncodedKey の項目を、ここで作成した `resources/cloudfront.pub` の値に差し替える


#### CloudFront 用署名用鍵の作成手順

CloudFront で署名付き Cookie によるアクセス制御を行う場合は秘密鍵を作成する必要がある。

`resources/fake.pem` をデフォルトの秘密鍵としているが、これはあくまで fake であり実際に利用しないこと。
実際に利用するには、コミット対象外とする PEM キーを以下のコマンドによって作成する。

```bash
# resources 以下に鍵のペアを作成
$ cd resources
$ openssl genrsa -out cloudfront.pem 2048
$ openssl rsa -pubout -in cloudfront.pem -out cloudfront.pub

# Lambda 上で読み込むときはパーミッションを引き継ぐため、others のパーミッションで読み込めるようにする
$ chmod 644 cloudfront.pem

# Lambda で署名するために Lambda で利用可能な位置にシンボリックリンクを作成する
$ cd ../api/chalicelib/env
$ unlink cloudfront.pem
$ ln -s ../../../resources/cloudfront.pem 
```


### 1. Chalice をデプロイ

ここでは `prod` 環境をデプロイする。
まず、以下の設定ファイルを作成し、手順0. で準備した値を入れる。

- `api/chalicelib/env/prod.yaml` (元ファイル: `api/chalicelib/env/prod.yaml.tpl`)
- `api/.chalice/policy-prod.json` (元ファイル: `api/.chalice/policy-prod.json.tpl`)


その後、例えば以下のコマンドで Chalice を AWS 環境にデプロイする。 
他にも `chalice package` を利用する方法もあるが、ここでは説明しない。

```bash
$ pipenv run chalice deploy --stage prod --profile work
Creating deployment package.
Creating IAM role: nuxt-chalice-api-prod
Creating lambda function: nuxt-chalice-api-prod
Creating Rest API
Resources deployed:
  - Lambda ARN: arn:aws:lambda:ap-northeast-1:************:function:nuxt-chalice-api-prod
  - Rest API URL: https://**********.execute-api.ap-northeast-1.amazonaws.com/prod/
```

### 2. CloudFormationによる S3 + CloudFront のデプロイ

`cfn/s3andcloudfront.yaml` のファイルを CloudFormation のテンプレートとしてアップロードし、S3とCloudFrontのリソースを作成する。
このとき、各パラメータに適切な値を入力する。

- apiEndpointDomain: 手順1. で作成した Rest API URL のドメイン `**********.execute-api.ap-northeast-1.amazonaws.com` を入力する
- applicationDomain: 本番用ドメインの `cfntest.t-kigi.net` を入力する
- certificateArn: 手順0. で準備した SSL 証明書の ARN を入力する
- これ以外のパラメータはデフォルトでも良いが、変更したい場合はその値を利用する


CloudFormation による生成が成功すれば、デプロイ用のS3バケットが準備される。
なお、何らかの理由で CloudFormation による生成に失敗した場合、S3バケットが残ってしまうので、
これは手動で削除しないとスクリプトの再実行はできない。


### 3. DNSレコードの設定

独自ドメインのレコード (ここでは `cfntest.t-kigi.net` ) を手順2. で作成した CDN のドメインに向ける。
Route 53 を使っているのであれば、エイリアスレコードで、それ以外であれば CNAME レコードで CDN のドメインを指すようにして、
構築したアプリケーションに準備したドメインでアクセスできるようにする。


### 4. Nuxt.js をS3へとデプロイする

まず、以下の設定ファイル `env.production.js` を作成し、手順0. で準備した値を入れる。

- `nuxt/constants/env.production.js` (元ファイル: `nuxt/constants/env.production.js.tpl` )

その後、以下のコマンドで `dist/` 以下に Hosting 用のリソースを生成する。

```bash
$ cd nuxt
$ yarn generate
```


その後、`dist/` 以下のファイルを手順2. で生成した S3 バケットへとアップロードする。
例えば、以下のコマンドでアップロードできる。
ここでは、デフォルトプロファイルを用いており、準備されたバケット名は `nuxt-chalice-hosting-prod-123456789012` である。

```bash
$ cd nuxt
$ aws s3 sync --delete dist/ s3://nuxt-chalice-hosting-prod-123456789012
```

その後、ブラウザで `https://cfntest.t-kigi.net/` にアクセスすれば UI 部分が表示される。


## 備考

### Nuxt.js Setup

以下のコマンドで Nuxt はセットアップを実施した。

```bash
$ npx create-nuxt-app nuxt

create-nuxt-app v3.5.2
✨  Generating Nuxt.js project in nuxt
? Project name: nuxt
? Programming language: TypeScript
? Package manager: Yarn
? UI framework: Vuetify.js
? Nuxt.js modules: Axios - Promise based HTTP client
? Linting tools: ESLint, Prettier
? Testing framework: Jest
? Rendering mode: Single Page App
? Deployment target: Static (Static/JAMStack hosting)
? Development tools: jsconfig.json (Recommended for VS Code if you're not using typescript)
? Continuous integration: None
? Version control system: None
```

