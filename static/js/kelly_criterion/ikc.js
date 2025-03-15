// INVESTMENT KELLY

document.getElementById("ikc-p").addEventListener("input", function() {
    let p = parseFloat(this.value);
    if (!isNaN(p)) {
        document.getElementById("ikc-q").value = (1 - p).toFixed(3);
    }
});

document.getElementById("ikc-q").addEventListener("input", function() {
    let q = parseFloat(this.value);
    if (!isNaN(q)) {
        document.getElementById("ikc-p").value = (1 - q).toFixed(3);
    }
});

document.getElementById("ikc-form").addEventListener("submit", function(event) {
    event.preventDefault();
    
    let form_type = "ikc"
    let ikc_p = document.getElementById("ikc-p").value;
    let ikc_q = document.getElementById("ikc-q").value;
    let ikc_g = document.getElementById("ikc-g").value;
    let ikc_l = document.getElementById("ikc-l").value;
    
    fetch("/ipm/kelly_criterion", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            form_type: form_type,
            ikc_p: ikc_p,
            ikc_q: ikc_q,
            ikc_g: ikc_g,
            ikc_l: ikc_l
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("ikc-result").innerHTML = `<b>${data.result}</b>`;
    })
    .catch(error => {
        alert("Error submitting kelly");
        console.error("Error:", error);
    });
});