#!/bin/bash

cd web \
    && rm -rf node_modules \
    && npm install \
    && npm run dev:docker &
make backend
