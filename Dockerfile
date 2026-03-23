FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --production

COPY index.js ./
COPY subs/ ./subs/

ENV PORT=7000
EXPOSE ${PORT}

CMD ["node", "index.js"]
