module.exports = {
  env: {
    mocha: true,
  },
  plugins: ['chai-friendly'],
  extends: ['standard', 'prettier', 'prettier/standard'],
  root: true,
  rules: {
    'no-use-before-define': 'off',
    'no-unused-vars': [
      'error',
      {
        varsIgnorePattern: 'should|expect',
      },
    ],
    // disable the original no-unused-expressions use chai-friendly
    'no-unused-expressions': 'off',
    'chai-friendly/no-unused-expressions': 'error',
  },
};
