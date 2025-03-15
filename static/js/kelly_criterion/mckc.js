// MULTIPLE CONDITIONS KELLY

function addCondition() {
    const conditionProb = document.getElementById("condition-prob").value;
    const conditionReturn = document.getElementById("condition-return").value;

    const conditionsList = document.getElementById("conditions-list");
    const newCondition = document.createElement("li");
    newCondition.textContent = "p=" + conditionProb + ";r=" + conditionReturn;
    newCondition.dataset.value = "p=" + conditionProb + ";r=" + conditionReturn;
    newCondition.onclick = function () {
        this.remove(); // Removes the clicked <li> element
    };
    conditionsList.appendChild(newCondition);

    conditionsProb.value = "";

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

document.getElementById("mckc-form").addEventListener("submit", function(event) {
    event.preventDefault();

    // Normalize Probabilities
    const conditionsList = document.getElementById("conditions-list");
    const items = conditionsList.getElementsByTagName("li");

    // Extract current probabilities
    let probabilities = [];
    for (let item of items) {
        let match = item.textContent.match(/p=([\d.]+);r=/);
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
        let match = item.textContent.match(/p=(-?[\d.]+);r=(-?[\d.]+)/);
        if (match) {
            let newProb = (probabilities[index] / total).toFixed(4);
            item.textContent = `p=${newProb};r=${match[2]}`;
            item.dataset.value = `p=${newProb};r=${match[2]}`;
            index++;
        }
    }

    // POST
    
    let form_type = "mckc";
    
    // Collect all p and q values from conditionsList
    let conditions = [];
    
    for (let item of conditionsList.getElementsByTagName("li")) {
        let match = item.textContent.match(/p=(-?[\d.]+);r=(-?[\d.]+)/);
        if (match) {
            conditions.push({ p: parseFloat(match[1]), r: parseFloat(match[2]) });
        }
    }
    
    fetch("/ipm/kelly_criterion", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            form_type: form_type,
            conditions: conditions // Send all p and r values
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("mckc-result").innerHTML = `<b>${data.result}</b>`;
    })
    .catch(error => {
        alert("Error submitting kelly");
        console.error("Error:", error);
    });
    
});