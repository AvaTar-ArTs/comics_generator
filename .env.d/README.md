# Local environment directory

Create a private local environment file:

  mkdir -p ~/.env.d
  cp .env.template ~/.env.d/comics-generator.env
  chmod 600 ~/.env.d/comics-generator.env

The generator reads OPENAI_API_KEY and STABILITY_KEY from the process environment. Never commit populated files.
