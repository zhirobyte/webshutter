const test = require('node:test');
const assert = require('node:assert/strict');

const {
  validateDomain
} = require('../src/discovery');

test('accepts valid domains', () => {
  assert.equal(validateDomain('Example.COM'), 'example.com');
  assert.equal(validateDomain('example.com.'), 'example.com');
});

test('rejects invalid domains', () => {
  for (const value of [
    '',
    'https://example.com',
    'example.com/path',
    'example.com:8080',
    'localhost',
    '127.0.0.1'
  ]) {
    assert.throws(() => validateDomain(value));
  }
});
