var list = document.createElement('div');
list.className = 'list';
var tags = document.querySelector('#search div.refs');
if (!tags) {
    tags = document.createElement('div');
    tags.className='refs';
    document.querySelector('form#search').appendChild(tags);
}
let kindname = { 't': 'serie', 'p': 'upphovsperson',
                 'x': 'i serien', 'f': 'Fantomen' }

document.querySelector('form#search').appendChild(list);
let input = document.querySelector('form#search input');
function placeList() {
    list.style.left = input.getBoundingClientRect().left + 'px';
    list.style.top = input.getBoundingClientRect().bottom + 'px';
};
window.addEventListener('scroll', placeList);
window.addEventListener('load', placeList);
window.addEventListener('resize', placeList);
window.addEventListener('fullscreenchange', placeList);
placeList();
function removeTag(t) {
    let l = t.target;
    console.log("Clicked", l);
    l.remove()
    return false;
}
tags.querySelectorAll('lable').forEach(e => e.addEventListener('click', removeTag));
function addTag(title, kind, url) {
    let tag = url.substring(url.lastIndexOf('/') + 1);
    let s = document.createElement('lable');
    s.innerHTML = title + '<input type="hidden" name="' + kind +
	'" value="' + tag + '">';
    s.tabindex = "1";
    s.className = kind;
    s.addEventListener('click', removeTag);
    tags.appendChild(s);
    list.innerHTML = '';
    input.value = '';
    console.log(s.innerHTML);
    input.focus();
    return false;
}
input.addEventListener('keyup', function(e) {
    let v = e.target.value;
    if (v.length > 1) {
	let r = new XMLHttpRequest();
	r.onload = function() {
	    let t = JSON.parse(this.responseText);
	    list.innerHTML = '';
	    t.map(x => {
		let a = document.createElement('a');
		a.innerHTML = x.t + ' <small>(' + kindname[x.k] + ')</small>';
		a.className='hit ' + x.k;
		a.href = x.u;
		a.tabindex = "1";
		a.onclick = function() { return addTag(x.t, x.k, x.u) }
		list.appendChild(a)
	    })
	};
	r.open('GET', document.location.origin + '/ac?q=' + encodeURIComponent(v));
	r.send(null);
    } else {
	list.innerHTML = '';
    }
})
