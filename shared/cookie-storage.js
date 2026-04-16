// Terroir HUB — Cross-domain Cookie Storage for Supabase Auth
// Sets cookies on .terroirhub.com so all subdomains share the session
// Supports chunked storage for values > 3500 bytes (cookie 4KB limit)
(function(){
  'use strict';

  var DOMAIN = '.terroirhub.com';
  var MAX_AGE = 365 * 24 * 60 * 60; // 1 year
  var CHUNK_SIZE = 3500; // safe limit per cookie

  var isLocalhost = location.hostname === 'localhost' || location.hostname === '127.0.0.1';

  function encode(v) {
    try { return encodeURIComponent(v); } catch(e) { return v; }
  }
  function decode(v) {
    try { return decodeURIComponent(v); } catch(e) { return v; }
  }

  function setCookie(name, value, maxAge) {
    var parts = [name + '=' + value, 'path=/', 'max-age=' + maxAge, 'SameSite=Lax'];
    if (!isLocalhost) { parts.push('domain=' + DOMAIN); parts.push('Secure'); }
    document.cookie = parts.join(';');
  }

  function getCookie(name) {
    var escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    var match = document.cookie.match(new RegExp('(?:^|; )' + escaped + '=([^;]*)'));
    return match ? match[1] : null;
  }

  function deleteCookie(name) {
    setCookie(name, '', 0);
  }

  window.ThubCookieStorage = {
    getItem: function(key) {
      // Try single cookie first
      var val = getCookie(key);
      if (val) return decode(val);

      // Try chunked
      var chunks = [];
      for (var i = 0; i < 5; i++) {
        var chunk = getCookie(key + '.' + i);
        if (!chunk) break;
        chunks.push(chunk);
      }
      if (chunks.length === 0) return null;
      return decode(chunks.join(''));
    },

    setItem: function(key, value) {
      var encoded = encode(value);

      // Clear any old chunks first
      for (var i = 0; i < 5; i++) { deleteCookie(key + '.' + i); }

      if (encoded.length <= CHUNK_SIZE) {
        // Fits in single cookie
        setCookie(key, encoded, MAX_AGE);
      } else {
        // Remove single cookie, use chunks
        deleteCookie(key);
        for (var j = 0; j < encoded.length; j += CHUNK_SIZE) {
          setCookie(key + '.' + j / CHUNK_SIZE, encoded.substring(j, j + CHUNK_SIZE), MAX_AGE);
        }
      }
    },

    removeItem: function(key) {
      deleteCookie(key);
      for (var i = 0; i < 5; i++) { deleteCookie(key + '.' + i); }
    }
  };
})();
