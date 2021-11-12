const day_buttons = document.querySelectorAll('.day-btn');
const form = document.querySelector("#scheduleCreationForm");
let scheduleID = null;
try {
    scheduleID = new URL(window.location.href).pathname.match(`.*\/([0-9])\/.*`)[1];
} catch (e) {
    console.log("No ScheduleID")
}
// Allowing the repeat-day buttons to have their appearance updated when they've
// been clicked on, or 'selected'.
for (let button of day_buttons) {
    button.addEventListener('click', (e) => {
        e.target.classList.toggle('btn-outline-secondary');
        e.target.classList.toggle('btn-secondary');
    })
}

// This method will interrupt form processing to add a list of days that the
// schedule should repeat; this is not being supplied by the form itself because
// I wanted to use cool buttons to let users select the days in a nicer
// way than the Django form supplies natively.

form.addEventListener('submit', (e) => {
    const formData = new FormData(form);
    // Get the days of the week that were selected
    const buttons = document.querySelectorAll('.day-btn');

    // Trying to create a JSON list to store days in instead:
    const days = [];

    for (let button of buttons) {
        if (button.classList.contains('btn-secondary')) {
            // Add a list to the post data including all those days selected.
            days.push(button.id)
        }
    }
    formData.append('days', days)
    // Send a separate request using Axios with the new FormData object:
    //Using the create path for now; don't know how I can tell JS here to use
    //the create or update path...?
    e.preventDefault();
    // Below is how I'm checking to see if we're updating a schedule or creating a new one;
    // by whether or not there is a schedule ID in the URL.
    if (scheduleID) {
        axios.post(`/schedules/${scheduleID}/update`, formData)
            .then((res) => {
                window.location.href = '/schedules';
            })
            .catch((error) => {

            })
    } else {
        axios.post('/schedules/create', formData)
            .then((res) => {
                window.location.href = '/schedules';
            })
            .catch((error) => {

            })
    }
})