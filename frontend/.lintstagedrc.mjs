export default {
  "*.{ts,tsx}": ["oxlint --fix", "prettier --write"],
  "*.{js,cjs,mjs,json,css,md}": ["prettier --write"],
};
