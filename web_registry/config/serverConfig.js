/**
 * Executed during page load/render, a minimal synchronous script to retrieve server configuration.
 *
 * Intended to be removed when the React client can obtain SERVER_CONFIG on its own.
 */

serverconfig_xhr = new XMLHttpRequest();

// Be robust to presence or absence of trailing slash
serverconfig_flaskBaseUrl = CLIENT_CONFIG.flaskBaseUrl
if (serverconfig_flaskBaseUrl.charAt(serverconfig_flaskBaseUrl.length - 1) === "/") {
    serverconfig_flaskBaseUrl = serverconfig_flaskBaseUrl.slice(0, -1);
}

serverconfig_xhr.open(
    "GET",
    [serverconfig_flaskBaseUrl, "app/config"].join("/"),
    false
);

serverconfig_xhr.send();

const SERVER_CONFIG = JSON.parse(serverconfig_xhr.response);

delete serverconfig_xhr
delete serverconfig_flaskBaseUrl
