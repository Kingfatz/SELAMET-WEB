/**
 * static/js/socket-client.js
 * Connects to the Flask-SocketIO server and patches live-updating DOM
 * elements (data-live="..." attributes) whenever a "sensor_update" event
 * arrives — used on the Home page so KPI numbers refresh without a reload.
 * Fails silently if Socket.IO isn't reachable (falls back to whatever was
 * server-rendered on page load).
 */

(function () {
  "use strict";
  if (typeof io === "undefined") return;

  const socket = io({ transports: ["websocket", "polling"] });

  function setLiveText(key, value, suffix) {
    document.querySelectorAll(`[data-live="${key}"]`).forEach(function (el) {
      el.textContent = suffix ? `${value}${suffix}` : value;
    });
  }

  socket.on("sensor_update", function (payload) {
    setLiveText("indoor_temp_c", payload.indoor_temp_c, "°C");
    setLiveText("indoor_humidity_pct", payload.indoor_humidity_pct, "%");
    setLiveText("bee_health_score", Math.round(payload.bee_health_score));

    const liveBadge = document.querySelector("[data-live-badge]");
    if (liveBadge) {
      liveBadge.className = "badge-pill badge-" + payload.colony_status;
      liveBadge.querySelector(".label-text").textContent =
        payload.colony_status.charAt(0).toUpperCase() + payload.colony_status.slice(1);
    }

    const stamp = document.querySelector("[data-live-updated]");
    if (stamp) stamp.textContent = "Live · updated just now";
  });

  socket.on("connect_error", function () {
    // Silent — dashboard still works from server-rendered data + periodic reload.
  });
})();
