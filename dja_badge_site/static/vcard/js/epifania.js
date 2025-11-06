// Aggiunge la Befana all'inizio
document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("befana-container");

    if (container) {
        createBefana(container);
    }
});

function createBefana(container) {
    // Creazione immagine della Befana
    const befana = document.createElement("img");
    befana.src = befanaImagePath; // Usa la variabile globale definita nell'HTML
    befana.alt = "Befana";
    befana.className = "befana";

    // Aggiungi al contenitore
    container.appendChild(befana);

    // Alterna la direzione di volo
    setInterval(() => {
        befana.classList.toggle("reverse");
    }, 5000); // Cambia direzione ogni 5 secondi
}
