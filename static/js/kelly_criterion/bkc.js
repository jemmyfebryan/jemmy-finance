// BASIC KELLY

document.getElementById("bkc-p").addEventListener("input", function() {
    let p = parseFloat(this.value);
    if (!isNaN(p)) {
        document.getElementById("bkc-q").value = (1 - p).toFixed(3);
    }
});

document.getElementById("bkc-q").addEventListener("input", function() {
    let q = parseFloat(this.value);
    if (!isNaN(q)) {
        document.getElementById("bkc-p").value = (1 - q).toFixed(3);
    }
});

document.getElementById("bkc-form").addEventListener("submit", function(event) {
    event.preventDefault();
    
    let form_type = "bkc"
    let bkc_p = document.getElementById("bkc-p").value;
    let bkc_q = document.getElementById("bkc-q").value;
    let bkc_b = document.getElementById("bkc-b").value;
    
    fetch("/ipm/kelly_criterion", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            form_type: form_type,
            bkc_p: bkc_p,
            bkc_q: bkc_q,
            bkc_b: bkc_b
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("bkc-result").innerHTML = `<b>${data.result}</b>`;
    })
    .catch(error => {
        alert("Error submitting kelly");
        console.error("Error:", error);
    });
});