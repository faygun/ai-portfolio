FROM node:20-alpine

WORKDIR /app

COPY package*.json /app
RUN npm ci

COPY ./ /app

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN echo "VITE_API_URL at build: $VITE_API_URL"

# ARG REACT_APP_API_URL
# ENV REACT_APP_API_URL=$REACT_APP_API_URL
# RUN echo "REACT_APP_API_URL at build: $REACT_APP_API_URL"


# RUN npm install
RUN npm run build

# #Serve with a lightweight web server
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "3000"]
