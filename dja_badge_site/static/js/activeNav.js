// inserisce la classe active sul menù corrispondente al windows.location.pathname
document.addEventListener("DOMContentLoaded", function(){
    let current = location.pathname;
    let links=document.querySelectorAll('.menu-wrapper .navbar-nav li a');
        for (var i = 0; i < links.length; ++i) {
            let li = links[i];
            let href=li.attributes['href'].value;
            let item_menuref="";
            if(li.attributes['item-menuref'] && li.attributes['item-menuref'] ){
                item_menuref=li.attributes['item-menuref'].value;
            }
            if(current.endsWith("/")){
                current=current.substring(0,current.length-1)
            }
            if(href.endsWith("/")){
                href=href.substring(0,href.length-1)
            }
            if(current==href){
                li.classList.add('active')
            }else{
                li.classList.remove('active')
                /**
                 * se è un megamenù allora verifico nel suo attributo item_menuref i path a cui le sotto voci fanno riferimento
                 * inseriti in attributo item_menuref separati da ;
                 */
                if(item_menuref){
                    let refs=item_menuref.split(";");
                    for(var j = 0; j < refs.length; ++j){
                        if(refs[j] && current.startsWith(refs[j])){
                            console.log("ok item-menuref current {} <> refs[j] {}",current,refs[j])
                            li.classList.add('active')
                        }
                    }
                }
            }
          }
});
