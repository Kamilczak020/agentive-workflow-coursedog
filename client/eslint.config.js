import globals from 'globals'
import js from '@eslint/js'
import typescriptEslint from '@typescript-eslint/eslint-plugin'
import typescriptEslintParser from '@typescript-eslint/parser'

export default [js.configs.recommended, {
  plugins: {
    '@typescript-eslint': typescriptEslint
  },
  files: [
    'src/**/*.ts',
    'documents/**/*.ts'
  ],
  ignores: ['**/coverage/**/*.js'],
  languageOptions: {
    parser: typescriptEslintParser,
    parserOptions: {
      project: 'tsconfig.json'
    },
    globals: {
      ...globals.node,
    }
  },
  rules: {
    'no-useless-constructor': 'off',
    'no-unused-vars': 0,
    '@typescript-eslint/no-unused-vars': ['error', { ignoreRestSiblings: true }],
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-misused-promises': 'warn',
    '@typescript-eslint/no-redundant-type-constituents': 'warn',
    '@typescript-eslint/no-empty-interface': 'off',
    '@typescript-eslint/no-unsafe-declaration-merging': 'off',
    'no-extend-native': ['error', { exceptions: ['Array'] }],
    'no-global-assign': ['error', { exceptions: ['self'] }],
    'generator-star-spacing': 'off',
    'array-bracket-spacing': ['error', 'always'],
    'arrow-body-style': ['warn', 'as-needed'],
    'standard/no-callback-literal': 0,
    'no-invalid-this': 'error',
    'comma-dangle': [
      'warn',
      {
        arrays: 'always-multiline',
        objects: 'always-multiline',
        imports: 'never',
        exports: 'never',
        functions: 'ignore',
      },
    ],
    curly: ['warn', 'multi-line'],
    'eol-last': ['error', 'always'],
    indent: ['error', 2, { SwitchCase: 1, VariableDeclarator: 1 }],
    'max-len': [
      'off',
      {
        code: 140,
        ignoreComments: true,
        ignoreTrailingComments: true,
        ignoreStrings: true,
        ignorePattern: '.+=".+"',
      },
    ],
    'no-multiple-empty-lines': ['error', { max: 1, maxEOF: 1 }],
    'no-prototype-builtins': 0,
    'object-curly-spacing': ['error', 'always'],
    'object-property-newline': ['error', { allowAllPropertiesOnSameLine: true }],
    'padded-blocks': 'off',
    'prefer-const': ['error', { destructuring: 'all' }],
    'prefer-template': 'error',
    'quote-props': ['error', 'consistent-as-needed'],
    quotes: [
      'error',
      'single',
      {
        avoidEscape: true,
        // TODO: Remove this rule and autofix,
        // as we don't need useless template literals
        allowTemplateLiterals: true,
      },
    ],
    semi: ['error', 'never', { beforeStatementContinuationChars: 'never' }],
    'space-before-function-paren': ['warn', 'always'],
    'spaced-comment': [
      'error',
      'always',
      {
        block: {
          markers: ['!'],
        },
      },
    ],
  },
}]
