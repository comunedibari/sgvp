function createSnowflake() {
    const snowflake = document.createElement("div");
    snowflake.innerHTML = "❄"; // Simbolo Unicode del fiocco di neve
    snowflake.classList.add("snowflake");
    document.body.appendChild(snowflake);

    // Dimensione casuale per il fiocco
    const size = Math.random() * 20 + 10 + "px";
    snowflake.style.fontSize = size;

    // Posizione casuale
    snowflake.style.left = Math.random() * 100 + "vw";

    // Durata casuale dell'animazione
    const duration = Math.random() * 3 + 2; // Tra 2 e 5 secondi
    snowflake.style.animationDuration = duration + "s";
    snowflake.style.opacity = Math.random() * 0.8 + 0.2; // Trasparenza per effetto realistico

    // Rimuove il fiocco dopo la durata dell'animazione
    setTimeout(() => {
        snowflake.remove();
    }, duration * 1000); // Converte i secondi in millisecondi
}

setInterval(createSnowflake, 200);
