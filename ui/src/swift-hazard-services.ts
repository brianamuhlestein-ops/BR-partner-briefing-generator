/** Shared launcher-hosted demo workspace. Configure URL before this module loads. */
export {}
declare global { interface Window { SWIFT_HAZARD_SERVICES_URL?: string } }
const configured = window.SWIFT_HAZARD_SERVICES_URL
const host = new URL(configured || `${location.protocol}//${location.hostname}:5177/`)
if (!['http:', 'https:'].includes(host.protocol)) throw Error('Hazard Services requires HTTP(S)')
const style = document.createElement('style')
style.textContent = `
[data-swift-hazard-anchor]{display:inline-flex;align-items:center;margin-right:8px}
.swift-hazard-button{position:relative;display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;border-radius:50%;border:1px solid #476075;background:#20364a;color:#b6c8d8;cursor:pointer;flex-shrink:0}
.swift-hazard-button svg{width:22px;height:22px}.swift-hazard-button[data-available=true]{color:#f2c568}.swift-hazard-button small{position:absolute;right:-5px;top:-5px;font:10px Arial;background:#192a39;border:1px solid currentColor;border-radius:8px;padding:1px 3px}
.swift-hazard-button:focus-visible{outline:2px solid #5bc9ff;outline-offset:3px}.swift-hazard-pulse{animation:swift-hazard-pulse .8s ease-in-out 3}@keyframes swift-hazard-pulse{50%{box-shadow:0 0 0 5px #f2c56855}}@media(prefers-reduced-motion:reduce){.swift-hazard-pulse{animation:none}}
.swift-hazard-dialog{position:fixed;inset:0;margin:auto;padding:0;width:min(1180px,95vw);max-width:95vw;height:85vh;max-height:95vh;background:#081421;color:#e8eff8;border:1px solid #446078;border-radius:10px;overflow:hidden}.swift-hazard-dialog::backdrop{background:#0009}.swift-hazard-dialog header{height:48px;display:flex;align-items:center;justify-content:space-between;padding:0 16px;font:15px Arial;border-bottom:1px solid #2c4358}.swift-hazard-dialog header button{color:#e8eff8;background:#20364a;border:1px solid #446078;border-radius:5px;padding:5px 10px;cursor:pointer}.swift-hazard-dialog iframe{display:block;width:100%;height:calc(100% - 48px);border:0}.swift-hazard-bridge{display:none}
`
document.head.append(style)
let available = false, pending: string[] = [], initialized = false, lastSeen = 0
let dirty = false
let popup: HTMLDialogElement | undefined
let popupFrame: HTMLIFrameElement | undefined
let opener: HTMLButtonElement | undefined
function frameUrl(key: string) { const url = new URL(host); url.searchParams.set(key,'1'); url.searchParams.set('parent_origin',location.origin); return url.href }
const bridge = document.createElement('iframe')
bridge.className = 'swift-hazard-bridge'; bridge.title = 'Hazard Services status'; bridge.src = frameUrl('hazard-status')
function render() {
  document.querySelectorAll<HTMLButtonElement>('.swift-hazard-button').forEach(button => {
    button.dataset.available = String(available)
    const label = available ? `Hazard Services: DEMO, ${pending.length} unreviewed. Live monitoring not connected.` : 'Hazard Services unavailable. Live monitoring not connected.'
    button.title=label;button.setAttribute('aria-label',label)
    button.querySelector('small')!.textContent=available ? `D${pending.length}` : '!'
  })
}
function close() { if (dirty && !confirm('Discard unsaved Hazard Services text?')) return; popup?.close();popup?.remove();popup=undefined;popupFrame=undefined;dirty=false;opener?.focus() }
function open(button: HTMLButtonElement) {
  if(popup) return
  opener=button;dirty=false
  popup=document.createElement('dialog');popup.className='swift-hazard-dialog';popup.setAttribute('aria-label','Hazard Services demonstration workspace')
  const header=document.createElement('header');header.append(document.createTextNode('SWIFT Hazard Services · DEMO'))
  const dismiss=document.createElement('button');dismiss.textContent='Close';dismiss.addEventListener('click',close);header.append(dismiss)
  popupFrame=document.createElement('iframe');popupFrame.title='Shared Hazard Services workspace';popupFrame.src=frameUrl('hazard-embed')
  popup.append(header,popupFrame);document.body.append(popup)
  popup.addEventListener('cancel',event=>{event.preventDefault();close()})
  popup.showModal()
}
window.addEventListener('message',event=>{
  if(event.origin!==host.origin || (event.source!==bridge.contentWindow && event.source!==popupFrame?.contentWindow)) return
  const data=event.data
  if(!data || typeof data!=='object') return
  if(data.type==='swift-hazards-dirty' && event.source===popupFrame?.contentWindow) dirty=data.dirty===true
  if(data.type!=='swift-hazards-status') return
  const next=Array.isArray(data.pendingIds) ? data.pendingIds.filter((id:unknown):id is string=>typeof id==='string') : []
  const newArrival=initialized && next.some((id:string)=>!pending.includes(id))
  available=data.available===true && data.mode==='demo';lastSeen=Date.now()
  if(available){pending=next;initialized=true}
  render()
  if(available && newArrival) document.querySelectorAll('.swift-hazard-button').forEach(button=>{button.classList.remove('swift-hazard-pulse');requestAnimationFrame(()=>button.classList.add('swift-hazard-pulse'))})
})
function mount() {
  document.querySelectorAll<HTMLElement>('[data-swift-hazard-anchor]').forEach(anchor=>{
    if(anchor.childElementCount) return
    const button=document.createElement('button');button.type='button';button.className='swift-hazard-button';button.setAttribute('aria-haspopup','dialog')
    button.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 3 4 6v6c0 5 8 9 8 9s8-4 8-9V6Z"/><path d="M12 7v6m0 3v1"/></svg><small>!</small>'
    button.addEventListener('click',()=>open(button));anchor.append(button)
  });render()
}
function start(){if(new URLSearchParams(location.search).has('hazard-embed') || new URLSearchParams(location.search).has('hazard-status'))return;document.body.append(bridge);mount();new MutationObserver(records=>{if(records.some(r=>Array.from(r.addedNodes).some(n=>n instanceof Element && (n.matches('[data-swift-hazard-anchor]')||n.querySelector('[data-swift-hazard-anchor]')))))mount()}).observe(document.body,{childList:true,subtree:true})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start()
window.setInterval(()=>{if(Date.now()-lastSeen>45000){available=false;render()}},5000)
window.addEventListener('beforeunload',event=>{if(dirty){event.preventDefault();event.returnValue=''}})
