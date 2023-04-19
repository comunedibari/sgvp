/**
 * ordinamento delle tabelle con colonne dichiarate ordinabili
 * es:
 *  <th sortable="true" scope="col"><span field-name="sotto_serie__nome" >TIPO PASS</span></th>
 *      ^^^^^^^^^^^^^^^              ^^^^  ^^^^^^^^^  ^^^^-> il pattern name utilizzato anche nel model.filter di django  
 */
window.addEventListener("load", () => {
    const thSpan = document.querySelectorAll('th[sortable="true"] span');
    [...thSpan].map((button) => {
      //setto il display delle data-dir a seconda dei parametri nella query
     let params = (new URL(document.location)).searchParams;
     let orderFields=params.getAll('o');
     let fields=orderFields.map(ff=>ff.startsWith("-")?ff.substring(1):ff);
     fields.forEach((field,idx) => {
        document.querySelectorAll('th[sortable=true] span[field-name='+field+']')
        .forEach(node=>node.setAttribute("data-dir",
            orderFields[idx].startsWith("-")?"desc":"asc"
        ));   
     });
     button.addEventListener("click", (e) => {
        let field_name=e.target.getAttribute("field-name");
        var searchParamsObj = new URLSearchParams(window.location.search);
        var searchParams = searchParamsObj.toString();
        if (!e.target.getAttribute("data-dir")) {
            searchParamsObj.append('o',field_name)
            window.location.search = searchParamsObj.toString();
        }
        else if (e.target.getAttribute("data-dir") == "desc") {
            searchParams=searchParams.replaceAll("o=-"+field_name,"")
            window.location.search = searchParams;
        } else if (e.target.getAttribute("data-dir") == "asc") {
            searchParams=searchParams.replaceAll("o="+field_name,"o=-"+field_name)
            window.location.search = searchParams;
        }
        
      });
    });
  });
  