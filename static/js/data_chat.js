
    function addInput() {
        const container = document.getElementById("input-container");
        const newInput = document.createElement("input");
        newInput.type = "text";
        newInput.name = "ingredient";
        newInput.placeholder = "Entrez un ingrédient";
        container.appendChild(newInput);
    }

    function deleteFn() {
        const container = document.getElementById("input-container");
        const inputs = container.getElementsByTagName("input");
        if (inputs.length > 0) {
            container.removeChild(inputs[inputs.length - 1]);
        }
    }
/*
    document.querySelector(".soumettre").addEventListener("click", function () {
        const inputs = document.querySelectorAll("#inputFields input");
        const ingredients = Array.from(inputs).map(input => input.value).filter(value => value);

        fetch("/integrer_ia_llm", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ingredients: ingredients })
        })
        .then(response => response.json())
        .then(data => {
            const resultDiv = document.createElement("div");
            resultDiv.innerHTML = `<h3>Résultat :</h3><p>${data.result}</p>`;
            document.body.appendChild(resultDiv);
        })
        .catch(error => console.error("Erreur :", error));
    });

*/