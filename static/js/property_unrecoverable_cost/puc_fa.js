// PROPERTY UNRECOVERABLE COST FIXED ASSUMPTIONS

document.getElementById("puc-fa-form").addEventListener("submit", function(event) {
    event.preventDefault();
    
    let form_type = "puc-fa"
    let puc_fa_pv = document.getElementById("puc-fa-pv").value;
    let puc_fa_pt = document.getElementById("puc-fa-pt").value;
    let puc_fa_mc = document.getElementById("puc-fa-mc").value;
    let puc_fa_coc = document.getElementById("puc-fa-coc").value;
    let puc_fa_rc = document.getElementById("puc-fa-rc").value;
    
    fetch("/pf/property_unrecoverable_cost", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            form_type: form_type,
            puc_fa_pv: puc_fa_pv,
            puc_fa_pt: puc_fa_pt,
            puc_fa_mc: puc_fa_mc,
            puc_fa_coc: puc_fa_coc,
            puc_fa_rc: puc_fa_rc
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("puc-fa-result").innerHTML = `<b>${data.result}</b>`;
    })
    .catch(error => {
        alert("Error submitting calculation");
        console.error("Error:", error);
    });
});