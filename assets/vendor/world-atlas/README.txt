Basemap for assets/plugins/map.js

countries-50m.js
  = https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json (world-atlas 2.0.2, downloaded 2026-10-05),
    unmodified, wrapped as `window.LPWorldAtlas["countries-50m"] = <json>;` so it loads with a <script> tag.
  TopoJSON, objects "countries" (241 geometries) and "land". Each country has `id` = ISO 3166-1 numeric code as a
  3-digit string ("356" = India, "004" = Afghanistan) and `properties.name` (e.g. "India"). A few have no id
  (Somaliland, Kosovo, N. Cyprus, Indian Ocean Ter., Siachen Glacier); "036" (Australia + Ashmore and Cartier Is.) appears twice.

Licenses (read from the downloaded files / publisher pages on 2026-10-05):
  - world-atlas packaging: ISC License, Copyright 2013-2019 Michael Bostock. Full text in LICENSE (copied from the npm package;
    package.json also says "license": "ISC").
  - Underlying data: Natural Earth 1:50m Admin 0 country boundaries, version 4.1.0 (per the world-atlas README).
    https://www.naturalearthdata.com/about/terms-of-use/ : "All versions of Natural Earth raster + vector map data found on
    this website are in the public domain." "No permission is needed to use Natural Earth." Credit optional: Made with Natural Earth.

Boundaries are Natural Earth's de facto ("on the ground") lines, e.g. in Kashmir; they are not an official position of any country.
