const CONFIG = {
    BASE_URL: "http://127.0.0.1:12347",
    VERSION: "2.0.0",
    BUILD_DATE: "2025-11-29",
    PORTIER_COMPLIANCE: "3.0"
};

// Development Override
if (window.location.hostname === 'localhost' && window.location.port === '8088') {
    CONFIG.BASE_URL = "http://127.0.0.1:12347"; // Docker dev setup
}

// Production Override
if (window.location.protocol === 'https:') {
    CONFIG.BASE_URL = CONFIG.BASE_URL.replace('http:', 'https:');
}

console.log('OpenWebUI Agent V2 Panel loaded:', CONFIG);