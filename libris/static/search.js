let form = document.querySelector('form#search');
let list = document.createElement('div');
list.className = 'list';
let tags = form.querySelector('div.refs');
if (!tags) {
    tags = document.createElement('div');
    tags.className='refs';
    form.appendChild(tags);
}
let kindname = { 't': 'serie', 'p': 'upphovsperson',
                 'x': 'i serien', 'f': 'Fantomenätten' }

form.appendChild(list);
let input = form.querySelector('input');
function placeList() {
    list.style.left = input.getBoundingClientRect().left + 'px';
    list.style.top = input.getBoundingClientRect().bottom + 'px';
};
window.addEventListener('scroll', placeList);
window.addEventListener('load', placeList);
window.addEventListener('resize', placeList);
window.addEventListener('fullscreenchange', placeList);
placeList();
function removeTag(e) {
    e.target.remove();
    return false;
}
tags.querySelectorAll('lable').forEach(e => e.addEventListener('click', removeTag));
function addTag(title, kind, url) {
    let tag = url.substring(url.lastIndexOf('/') + 1);
    let s = document.createElement('lable');
    s.innerHTML = title + '<input type="hidden" name="' + kind +
	'" value="' + tag + '">';
    s.tabIndex = 4;
    s.className = kind;
    s.addEventListener('click', removeTag);
    tags.appendChild(s);
    list.innerHTML = '';
    input.value = '';
    input.focus();
    return false;
}
input.addEventListener('keyup', e => {
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
		a.tabIndex = 2;
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
form.addEventListener('keypress', e => {
    let t = e.target;
    switch(e.code) {
    case 'ArrowUp':
	(t.parentNode == list && t.previousSibling || list.querySelector('a:last-child')).focus();
	break;
    case 'ArrowDown':
	(t.parentNode == list && t.nextSibling || list.querySelector('a:first-child')).focus();
	break;
    case 'Escape':
	input.focus();
	break;
    default:
	return true;
    };
    e.preventDefault();
    e.stopPropagation();
    return false;
});
