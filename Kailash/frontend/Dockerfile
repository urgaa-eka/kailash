FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY yarn.lock ./
# No `|| yarn install` fallback, matching the frontend CI job: the lockfile
# determines what this image installs, so drift has to fail the build rather
# than be silently resolved into a different dependency set.
RUN yarn install --frozen-lockfile

COPY . .
# Same-origin by default: nginx proxies /api/ -> backend:8000, so the SPA
# calls relative URLs. Shell env beats .env.production in CRA, so this
# build arg overrides the hosted-deploy URL baked into .env.production.
ARG REACT_APP_BACKEND_URL=""
ENV REACT_APP_BACKEND_URL=${REACT_APP_BACKEND_URL} \
    DISABLE_ESLINT_PLUGIN=true \
    GENERATE_SOURCEMAP=false
RUN yarn build

FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
