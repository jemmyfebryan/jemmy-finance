// MULTIPLE OUTCOMES KELLY

function addOutcome() {
    const outcomeProb = document.getElementById("outcome-prob").value;
    const outcomeOdds = document.getElementById("outcome-odds").value;

    const outcomesList = document.getElementById("outcomes-list");
    const newOutcome = document.createElement("li");
    newOutcome.textContent = "p=" + outcomeProb + ";b=" + outcomeOdds;
    newOutcome.dataset.value = "p=" + outcomeProb + ";b=" + outcomeOdds;
    newOutcome.onclick = function () {
        this.remove(); // Removes the clicked <li> element
    };
    outcomesList.appendChild(newOutcome);

    outcomeProb.value = "";

    // if (assetCode) {
    //     const assetList = document.getElementById("available-assets");
    //     const existingAssets = [...assetList.children].map(li => li.dataset.value);
    //     if (!existingAssets.includes("custom-" + assetCode)) {
    //         const newAsset = document.createElement("li");
    //         newAsset.textContent = assetCode;
    //         newAsset.dataset.value = "custom-" + assetCode;
    //         newAsset.onclick = function() { toggleSelection(this); };
    //         assetList.appendChild(newAsset);
    //     }
    //     customAssetInput.value = "";
    // }
}

document.getElementById("mokc-form").addEventListener("submit", function(event) {
    event.preventDefault();

    // Normalize Probabilities
    const outcomesList = document.getElementById("outcomes-list");
    const items = outcomesList.getElementsByTagName("li");

    // Extract current probabilities
    let probabilities = [];
    for (let item of items) {
        let match = item.textContent.match(/p=([\d.]+);b=/);
        if (match) {
            probabilities.push(parseFloat(match[1]));
        }
    }

    // Compute total probability
    let total = probabilities.reduce((sum, p) => sum + p, 0);
    if (total === 0) return; // Avoid division by zero

    // Normalize probabilities so they sum to 1
    let index = 0;
    for (let item of items) {
        let match = item.textContent.match(/p=([\d.]+);b=([\d.]+)/);
        if (match) {
            let newProb = (probabilities[index] / total).toFixed(4);
            item.textContent = `p=${newProb};b=${match[2]}`;
            item.dataset.value = `p=${newProb};b=${match[2]}`;
            index++;
        }
    }

    // POST
    
    let form_type = "mokc";
    
    // Collect all p and q values from outcomesList
    let outcomes = [];
    
    for (let item of outcomesList.getElementsByTagName("li")) {
        let match = item.textContent.match(/p=([\d.]+);b=([\d.]+)/);
        if (match) {
            outcomes.push({ p: parseFloat(match[1]), b: parseFloat(match[2]) });
        }
    }
    
    fetch("/ipm/kelly_criterion", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            form_type: form_type,
            outcomes: outcomes // Send all p and q values
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("mokc-result").innerHTML = `<b>${data.result}</b>`;
    })
    .catch(error => {
        alert("Error submitting kelly");
        console.error("Error:", error);
    });
    
});