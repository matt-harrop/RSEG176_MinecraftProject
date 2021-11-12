const days_tags = document.querySelectorAll(".days-tag");
console.log(days_tags);
console.log(`Days_tags Count: ${days_tags.length}`);

days_tags.forEach(e => {
    try {
        let days = e.innerHTML.match(/[A-Za-z]+/g);
        e.innerHTML = "Repeats: ";
        for (let day of days) {
            e.innerHTML += `<button class='btn btn-sm btn-outline-dark mx-1 my-auto' disabled>${day}</button>`
        }
    } catch (e) {
        e.innerHTML = "Repeats: ";
    }
})