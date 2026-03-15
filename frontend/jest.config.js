module.exports = {
  preset: 'ts-jest',
  collectCoverage: true,
  coverageReporters: ['json', 'text', 'lcov', 'clover'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  transform: {
    '^.+\.(js|tsx?)$': 'ts-jest',
  },
  transformIgnorePatterns: ['<rootDir>/node_modules/'],
  verbose: true,
};
