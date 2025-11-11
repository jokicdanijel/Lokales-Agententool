// assets/js/telemetry.js
export function sendEvent(id, props){
  try{
    // no-op logger; integrate real telemetry later
    console.debug('[telemetry]', id, props || {});
    // Example: navigator.sendBeacon('/telemetry', JSON.stringify({ id, ts:Date.now(), ...props }));
  }catch(_){}
}
