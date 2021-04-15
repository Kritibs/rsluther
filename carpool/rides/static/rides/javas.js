window.addEventListener('DOMContentLoaded', (event) => {
  var utc = new Date().toJSON().slice(0,10);
  document.querySelector("#date").value = utc;
  setBodyHeight();
});
window.onresize = setBodyHeight;
window.onload = setBodyHeight;
function setBodyHeight(){ 
    headerHeight = document.querySelector("nav").scrollHeight;
    document.querySelector("#header").style.height = headerHeight;
    footerHeight = document.querySelector("#footer").offsetHeight;
    windowHeight = window.innerHeight;

    bodyHeight = windowHeight - footerHeight - headerHeight - 16

    document.querySelector("#allbody").style.minHeight = bodyHeight + "px";



}
