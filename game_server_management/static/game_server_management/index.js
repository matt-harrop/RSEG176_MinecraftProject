const serverDivs = document.querySelectorAll(".server-block");

for (let server of serverDivs) {
    const server_ip = server.querySelector(".ip-address");
    if (server_ip) {
        const gameStatus = server.querySelector(".game-status");
        // gameStatus.toggleAttribute("hidden");
    }
}